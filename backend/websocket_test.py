""" Test suite for websocket feature in the FastAPI backend."""
import json
import enum
import asyncio
import logging
import argparse
import websockets
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder
from global_var import SECRET
from util import init_logger

LOGGER: logging.Logger = init_logger('websocket_test', './logs', True)


class Role(str, enum.Enum):
    client: str = 'client'
    notifier: str = 'notifier'


async def connect_ws(role: Role):
    """ Create a websocket connection."""
    ws_url, ws_token = SECRET['websocket_url'], SECRET['websocket_token']
    if role == Role.notifier:
        async with websockets.connect(f'{ws_url}?token={ws_token}', ssl=True) as ws:
            LOGGER.debug('[role: notifier] Websocket connected: %s', str(ws.local_address))
            data_str: str = json.dumps(
                jsonable_encoder(
                    {
                        'visa_type': 'F',
                        'embassy_code': 'pp',
                        'prev_avai_date': datetime.now(timezone.utc),
                        'curr_avai_date': datetime.now(timezone.utc),
                    }
                )
            )
            await ws.send(data_str)

    elif role == Role.client:
        async with websockets.connect(ws_url, ssl=True) as ws:
            LOGGER.debug('[role: client] Websocket connected: %s', str(ws.local_address))
            async for msg in ws:
                LOGGER.debug('[role: client] Websocket %s received msg | Timestamp: %s', str(ws.local_address), msg)


async def keep_ws_alive(alive_time: float, role: Role):
    """ Keep websocket alive for `for` seconds."""
    await asyncio.wait([asyncio.create_task(connect_ws(role))], timeout=alive_time)


async def load_test_ws(load: int, alive_time: float):
    """ Load test with concurrently running websocket."""
    await asyncio.gather(*[keep_ws_alive(alive_time, 'client' if i % 2 else 'notifier') for i in range(load)])


def init():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        '-l', '--load',
        dest='load',
        default=2 ** 10,
        type=int,
        help='The number of websockets to keep alive for load test.'
    )
    parser.add_argument(
        '-f', '--for',
        dest='alive_for',
        default=60,
        type=float,
        help='Number of seconds for running the test.'
    )

    args = parser.parse_args()
    print(args)
    asyncio.run(load_test_ws(args.load, args.alive_for))


if __name__ == '__main__':
    init()
