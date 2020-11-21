""" WebSocket service for http://tuixue.online/visa/"""
import typing
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi.encoders import jsonable_encoder
from starlette.concurrency import run_until_first_complete
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query

import tuixue_mongodb as DB
import global_var as G

EMBASSY_CODES = [emb.code for emb in G.USEmbassy.get_embassy_lst()]
app = FastAPI(root_path='/ws')

# P.S. The broadcasting logic copy-paste a LOT of code from https://github.com/encode/broadcaster
class VisaStatusUpdateEvent:
    def __init__(
        self,
        visa_type: str,
        embassy_code: str,
        prev_avai_date: typing.Optional[datetime],
        curr_avai_date: datetime
    ) -> None:
        self.visa_type = visa_type
        self.embassy_code = embassy_code
        self.prev_avai_date = prev_avai_date
        self.curr_avai_date = curr_avai_date

    def __repr__(self):
        return 'VisaStatusUpdateEvent\
            (visa_type={!r}, embassy_code={!r}, prev_avai_date={!r}, curr_avai_date={!r})'.format(
                self.visa_type,
                self.embassy_code,
                self.prev_avai_date,
                self.curr_avai_date,
            )

    def to_dict(self):
        return {
            'visa_type': self.visa_type,
            'embassy_code': self.embassy_code,
            'prev_avai_date': self.prev_avai_date,
            'curr_avai_date': self.curr_avai_date,
        }

class BroadcastBackend:
    """ A in-memory broadcaster backend.
        Maintaining an event queue that publish every incoming event. There is no
        channel distinguishment as there is only one channel in our case, therefore
        no subscribe nor unsubscribe methods.
    """
    def __init__(self) -> None:
        self.published_visa_status: asyncio.Queue = asyncio.Queue()

    async def publish(
        self,
        visa_type: str,
        embassy_code: str,
        prev_avai_date: typing.Optional[datetime],
        curr_avai_date: datetime,
    ) -> None:
        """ Publish a new visa status update."""
        event = VisaStatusUpdateEvent(visa_type, embassy_code, prev_avai_date, curr_avai_date)
        await self.published_visa_status.put(event)

    async def next_published(self) -> VisaStatusUpdateEvent:
        """ Listen to the visa status update event and dispatch event to the broadcaster."""
        while True:
            event: VisaStatusUpdateEvent = await self.published_visa_status.get()
            # if (event.visa_type, event.embassy_code) in self.subscribed_visa_status:
            return event


class Broadcast:
    default_channel = 'new_visa_status'

    def __init__(self) -> None:
        self.subscribers = {}
        self.backend = BroadcastBackend()
        self.connected = False

    async def __aenter__(self) -> 'Broadcast':
        self.connect()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        self.disconnect()

    async def connect(self):
        self.listener_task = asyncio.create_task(self.listener())
        self.connected = True

    async def disconnect(self):
        if self.listener_task.done():
            self.listener_task.result()
        else:
            self.listener_task.cancel()
        self.connected = False

    async def listener(self) -> None:
        """ Dispatch new visa status event to all subscriber."""
        while True:
            event = await self.backend.next_published()
            for queue in list(self.subscribers.get(self.default_channel, [])):
                await queue.put(event)

    async def publish(
        self,
        visa_type: str,
        embassy_code: str,
        prev_avai_date: typing.Optional[datetime],
        curr_avai_date: datetime,
    ) -> None:
        """ Publish a new visa status event. Meant to be called by notifier."""
        await self.backend.publish(visa_type, embassy_code, prev_avai_date, curr_avai_date)

    @asynccontextmanager
    async def subscribe(self):
        queue: asyncio.Queue = asyncio.Queue()

        try:
            # subscribe at context manager entering
            if not self.subscribers.get(self.default_channel):
                # if there is a third party (e.g. Redis) backend here, subscribe here
                self.subscribers[self.default_channel] = {queue}
            else:
                self.subscribers[self.default_channel].add(queue)

            yield Subscriber(queue)

            # unsubscribe at context manager exiting
            self.subscribers[self.default_channel].remove(queue)
            # if there are more than one channel, or a third party backend, unsubscribe here
        finally:
            await queue.put(None)  # End iterational wait in asyncio.Queue.get in websocket route


class Unsubscribed(Exception):
    pass


class Subscriber:
    def __init__(self, queue: asyncio.Queue):
        self.queue: asyncio.Queue = queue

    async def __aiter__(self):
        try:
            while True:
                yield await self.get_event()
        except Unsubscribed:
            pass

    async def get_event(self) -> VisaStatusUpdateEvent:
        event = await self.queue.get()
        if event is None:
            raise Unsubscribed()
        return event


BROADCASTER = Broadcast()


async def visa_status_notification_sender(websocket: WebSocket):
    """ The websocket connection from notifier.Notifier will be send a JSON string
        handled by this function. The JSON string contains new visa status update
        which will be dispatched into the broadcast channel.
    """
    async for new_visa_status in websocket.iter_json():
        await BROADCASTER.publish(**new_visa_status)


async def visa_status_notification_receiver(websocket: WebSocket):
    """ The websocket connection from frontend React app will receive a new pushed
        JSON string via this function. Entering this function will create a new
        subscription to the broadcasting channel. Exiting it will unsubscribe the
        channel.
    """
    async with BROADCASTER.subscribe() as subscriber:
        async for new_visa_status in subscriber:  # get an Event object
            ws_data = {
                'type': 'notification',
                'data': new_visa_status.to_dict()
            }
            await websocket.send_json(jsonable_encoder(ws_data))


async def get_newest_visa_status(websocket: WebSocket):
    """ Get the latest fetched visa status with the given query"""
    try:
        while True:
            visa_type, embassy_code = await websocket.receive_json()
            if not isinstance(visa_type, list):
                visa_type = [visa_type]
            if not isinstance(embassy_code, list):
                embassy_code = [embassy_code]

            if not (
                all([vt in G.VISA_TYPES for vt in visa_type]) and
                all([ec in EMBASSY_CODES for ec in embassy_code])
            ):
                await websocket.send_json(
                    {'error': f'In valid visa_type ({visa_type}) or embsssy_code ({embassy_code}) is given'}
                )
                continue

            latest_written = DB.VisaStatus.find_latest_written_visa_status(visa_type, embassy_code)
            ws_data = {
                'type': 'newest',
                'data': latest_written
            }
            await websocket.send_json(jsonable_encoder(ws_data))
    except WebSocketDisconnect:
        pass


@app.websocket('/visastatus/latest')
async def get_newest_visa_status_update(websocket: WebSocket, token: str = Query('')):
    """ Implement a PUB/SUB for updating the newest visa status"""
    if not BROADCASTER.connected:
        await BROADCASTER.connect()

    await websocket.accept()
    try:
        if token == G.SECRET['websocket_token']:
            await asyncio.create_task(visa_status_notification_sender(websocket))
        else:
            await run_until_first_complete(
                (visa_status_notification_receiver, {'websocket': websocket}),
                (get_newest_visa_status, {'websocket': websocket})
            )
    except WebSocketDisconnect:
        pass
