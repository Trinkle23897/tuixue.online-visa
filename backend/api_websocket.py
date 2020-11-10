""" WebSocket service for http://tuixue.online/visa/"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import tuixue_mongodb as DB
import global_var as G

EMBASSY_CODES = [emb.code for emb in G.USEmbassy.get_embassy_lst()]
app = FastAPI()


@app.websocket('/visastatus/latest')
async def get_latest_visa_status(websocket: WebSocket):
    """ Get the latest fetched visa status with the given query"""
    await websocket.accept()
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
            await websocket.send_json(latest_written)
    except WebSocketDisconnect:
        pass
