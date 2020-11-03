""" A mocking crawler node."""

import random
import string
import threading
from fastapi import FastAPI
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

MOCK_DATE = datetime(2020, 1, 1)
# LAST_MINUTE = None

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r'http[s]://localhost:?[\d]*',
    allow_methods=['GET', 'POST'],
)


def generate_session(sys):
    """ Randomly generate session."""
    sess = 'mockingsess_{}'.format(''.join(random.choices(string.ascii_lowercase, k=16)))
    if sys == 'cgi':
        return sess
    else:
        sche_id = ''.join(random.choices(string.digits, k=6))
        return (sess, sche_id)


def update_mock_date():
    """ Change available date"""
    global MOCK_DATE
    last_two_min = None
    while True:
        now = datetime.now()
        if now.minute % 2 == 0 and now.minute != last_two_min:
            last_two_min = now.minute
            MOCK_DATE += timedelta(days=1)
            print(f'{now}: Change MOCK_DATE to {MOCK_DATE}')


@app.get('/')
def handshake():
    return {'code': 0, 'msg': 'OK'}


@app.get('/register')
def cgi_register(type: str, place: str):
    """ Return a success response."""
    session = generate_session('cgi')
    dt = MOCK_DATE.strftime('%Y-%m-%d')
    return {'code': 0, 'msg': dt, 'session': session}


@app.get('/refresh')
def cgi_refresh(session: str):
    """ Return a sucess response, and change the mock date every 2 minutes."""
    return {'code': 0, 'msg': MOCK_DATE.strftime('%Y-%m-%d')}


@app.get('/ais/register')
def ais_register(code: str, email: str, pswd: str):
    """ Return a success login"""
    sess, sche_id = generate_session('ais')
    year, month, day = [int(i) for i in MOCK_DATE.strftime('%Y-%m-%d').split('-')]
    return {
        'code': 0,
        'msg': [['Belfast', [year, month, day]], ['London', [year, month, day]]],
        'session': sess,
        'id': sche_id
    }


@app.get('/ais/refresh')
def asi_refresh(code: str, id: str, session: str):
    """ Return a success response."""
    year, month, day = [int(i) for i in MOCK_DATE.strftime('%Y-%m-%d').split('-')]
    return {
        'code': 0,
        'msg': [['Belfast', [year, month, day]], ['London', [year, month, day]]],
        'session': generate_session('cgi')  # single random session string
    }


t = threading.Thread(target=update_mock_date)
t.start()
