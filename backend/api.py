""" RESTful API for http://tuixue.online/global/"""

from enum import Enum
from typing import Optional, List
from datetime import datetime, timedelta

from fastapi import FastAPI, Body, Response, status
from pydantic import BaseModel

import tuixue_mongodb as DB
from notifier import Notifier
from tuixue_typing import VisaType, System, Region
from global_var import USEmbassy, CGI_LOCATION_DOMESTIC

EMBASSY_LST = USEmbassy.get_embassy_lst()
app = FastAPI()


# This class will be moved to tuixue_typing.py if it's needed by other modules
class EmailSubsRep(str, Enum):
    first_rep = 'first'
    second_rep = 'second'


# These classes serve for the purpose of request body type chechking for FastAPI
class SingleSubscription(BaseModel):
    visa_type: str
    code: str
    till: str


class EmailSubscription(BaseModel):
    email: str
    subscription: List[SingleSubscription]


@app.get('/')
def handshake():
    """ Index page that returns a 200 status with a OK message."""
    return {'status_code': 200, 'msg': 'OK'}


@app.get('/backend/global')
def get_global_visa_status(
    visa_type: VisaType = VisaType.F,
    sys: System = System.CGI,
    region: Optional[Region] = None,
    exclude_domestic: bool = True,
    skip: int = 0,
    take: int = 15,
):
    """ Get the global visa appointment status with given query."""

    today = datetime.today()
    dt_range = [today - timedelta(days=skip + d) for d in range(take)]

    embassy_lst = [embassy for embassy in EMBASSY_LST if embassy.sys == sys]
    if exclude_domestic:
        embassy_lst = [embassy for embassy in embassy_lst if embassy.location not in CGI_LOCATION_DOMESTIC]
    if region is not None:
        embassy_lst = [embassy for embassy in embassy_lst if embassy.region == region]

    embassy_code_lst = [emb.code for emb in embassy_lst]

    tabular_data = DB.VisaStatus.find_earliest_visa_status(visa_type, embassy_code_lst, dt_range)

    return {'visa_type': visa_type, 'region': region, 'sys': sys, 'visa_status': tabular_data}


@app.get('/backend/domestic')
def get_domestic_visa_status(visa_type: VisaType = VisaType.F, skip: int = 0, take: int = 15):
    """ Get the domestic visa appointment status with given query."""
    today = datetime.today()
    dt_range = [today - timedelta(days=skip + d) for d in range(take)]

    embassy_lst = [embassy for embassy in EMBASSY_LST if embassy.location in CGI_LOCATION_DOMESTIC]
    embassy_code_lst = [emb.code for emb in embassy_lst]

    tabular_data = DB.VisaStatus.find_earliest_visa_status(visa_type, embassy_code_lst, dt_range)
    return {'visa_type': visa_type, 'visa_status': tabular_data}


@app.post('/backend/subscribe/email/{rep}')
def post_email_subscription(rep: EmailSubsRep, subscription: EmailSubscription = Body(..., embed=True)):
    """ Post email subscription."""
    if rep == EmailSubsRep.first_rep:
        Notifier.send_subscription_confirmation(subscription.dict())
        return Response(status_code=status.HTTP_202_ACCEPTED)
    elif rep == EmailSubsRep.second_rep:
        subscription = subscription.dict()
        subs_lst = [(subs['visa_type'], subs['code'], subs['till']) for subs in subscription['subscription']]
        updated_subscriber = DB.Subscription.add_email_subscription(subscription['email'], subs_lst)

        return updated_subscriber
