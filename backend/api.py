""" RESTful API for http://tuixue.online/global/"""

from enum import Enum
from typing import Optional, List
from datetime import datetime, timedelta

from fastapi import FastAPI, Body, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import global_var as G
import tuixue_mongodb as DB
from notifier import Notifier
from tuixue_typing import VisaType, EmbassyCode

EMBASSY_LST = G.USEmbassy.get_embassy_lst()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r'http[s]://localhost:?[\d]*',
    allow_methods=['GET', 'POST'],
)


# This class will be moved to tuixue_typing.py if it's needed by other modules
class EmailSubsRep(str, Enum):
    first_rep = 'first'
    second_rep = 'second'


# These classes serve for the purpose of request body type chechking for FastAPI
class SingleSubscription(BaseModel):
    visa_type: str
    code: str
    till: Optional[datetime]


class EmailSubscription(BaseModel):
    email: str
    subscription: List[SingleSubscription]


@app.get('/')
def handshake():
    """ Index page that returns a 200 status with a OK message."""
    return {'status_code': 200, 'msg': 'OK'}


@app.get('/visastatus/meta')
def get_meta_data():
    """ Return metadata such as region mapping and embassy detail."""
    region_lst = []
    for region, embassy_code_lst in G.REGION_LOCATION_MAPPING.items():
        region_lst.append({
            'region': region,
            'embassy_code_lst': embassy_code_lst
        })
    return {'region': region_lst, 'embassy': G.EMBASSY_LOC}


@app.get('/visastatus/earliest')
def get_earliest_visa_status(
    visa_type: List[VisaType] = Query(...),
    embassy_code: List[EmbassyCode] = Query(...),
    since: Optional[datetime] = datetime.today() - timedelta(days=15),
    to: Optional[datetime] = datetime.today(),
):
    """ Get the available visa appointment status with given query."""

    since = since.replace(hour=0, minute=0, second=0, microsecond=0)
    to = to.replace(hour=0, minute=0, second=0, microsecond=0)
    dt_range = [since + timedelta(days=d) for d in range((to - since).days)]

    tabular_data = DB.VisaStatus.find_earliest_visa_status(visa_type, embassy_code, dt_range)

    return {
        'visa_type': visa_type,
        'embassy_code': embassy_code,
        'since': since,
        'to': to,
        'visa_status': tabular_data,
    }


@app.get('/visastatus/latest')
def get_latest_visa_status(
    visa_type: List[VisaType] = Query(...),
    embassy_code: List[EmbassyCode] = Query(...),
):
    """ Get the latest fetched visa status with the given query"""

    latest_written = DB.VisaStatus.find_latest_written_visa_status(visa_type, embassy_code)

    return latest_written


@app.get('/visastatus/{visa_type}/{embassy_code}')
def get_visa_status_by_visa_type_and_embassy(
    visa_type: VisaType,
    embassy_code: EmbassyCode,
    write_date: Optional[datetime] = datetime.today(),
):
    """ Return all of the historical data fetched for a givenv `(visa_type, embassy_code)` pair.
        If a given `since` or `or` date query is given, the historical data will be truncated to
        the specified dates.
        It's noteworthy that this endpoint consume a huge amount of resource in backend when `since`
        and `to` date range are too large. Use with caution.
    """
    write_date = write_date.replace(hour=0, minute=0, second=0, microsecond=0)
    empty_record = {
        'visa_type': visa_type,
        'embassy_code': embassy_code,
        'write_date': write_date,
        'available_dates': []
    }
    hist_visa_status = (DB.VisaStatus.find_historical_visa_status(visa_type, embassy_code, write_date) or empty_record)

    return hist_visa_status


@app.post('/subscribe/email/{rep}')
def post_email_subscription(rep: EmailSubsRep, subscription: EmailSubscription = Body(..., embed=True)):
    """ Post email subscription."""
    subscription = subscription.dict()
    subs_lst = [
        (
            subs['visa_type'],
            subs['code'],
            subs['till'] or datetime.max
        ) for subs in subscription['subscription']
    ]

    if rep == EmailSubsRep.first_rep:
        # TODO: construct the email addresses. send the email. new unsubscribe route
        Notifier.send_subscription_confirmation(subscription['email'], subs_lst)
        return Response(status_code=status.HTTP_202_ACCEPTED)

    elif rep == EmailSubsRep.second_rep:
        updated_subscriber = DB.Subscription.add_email_subscription(subscription['email'], subs_lst)

        return updated_subscriber
