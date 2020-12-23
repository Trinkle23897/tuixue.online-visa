""" RESTful API for http://tuixue.online/visa/"""

from enum import Enum
from typing import Optional, List
from datetime import datetime, timedelta, timezone

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
    allow_origins=['*'],
    allow_methods=['GET', 'POST'],
)


# This class will be moved to tuixue_typing.py if it's needed by other modules
class EmailSubsStep(str, Enum):
    confirming = 'confirming'
    subscribed = 'subscribed'


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
    """ Return metadata such as region mapping and embassy detail. Where `region` is
        a list of `region-embassy_code` mapping in following shape:

        ```json
        [
            {"region": "REGION_0", "embassy_code_lst": ["code0", "code1"]}
        ]
        ```

        and embassy lst is an array of array, where each sub array carries attributes
        in following order:

        ```json
        [
            ["name_cn", "name_en", "code", "sys", "region", "continent", "country", "tz_info"]
        ]
        ```
    """
    return {
        'region': G.USEmbassy.get_region_mapping(),
        'region_country_embassy_tree': G.USEmbassy.get_region_country_embassy_tree(),
        'embassy_lst': G.EMBASSY_ATTR,
        'visa_type_details': G.VISA_TYPE_DETAILS,
        'default_filter': ['bj', 'sh', 'gz', 'sy', 'hk', 'tp', 'pp', 'sg', 'bfs', 'lcy', 'gye'],
    }


@app.get('/visastatus/overview')
def get_visa_status_overview(
    visa_type: List[VisaType] = Query(...),
    embassy_code: List[EmbassyCode] = Query(...),
    since: Optional[datetime] = datetime.now(timezone.utc) - timedelta(days=15),
    to: Optional[datetime] = datetime.now(timezone.utc),
):
    """ Get the available visa appointment status with given query.
        The `since` and `to` query params, if provided, MUST be in the timezone of UTC.
    """
    # embassy = G.USEmbassy.get_embassy_by_code(embassy_code)

    # Convert `since` and `to` to embassy local time and get rid of tzinfo
    since = since.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    to = to.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    dt_range = [since + timedelta(days=d) for d in range((to - since).days + 1)]

    tabular_data = DB.VisaStatus.find_visa_status_overview(visa_type, embassy_code, dt_range)

    return {
        'visa_type': visa_type,
        'embassy_code': embassy_code,
        'since': since,
        'to': to,
        'visa_status': tabular_data,
    }


@app.get('/visastatus/{visa_type}/{embassy_code}')
def get_visa_status_by_visa_type_and_embassy(
    visa_type: VisaType,
    embassy_code: EmbassyCode,
):
    """ Return all of the historical data fetched for a givenv `(visa_type, embassy_code)` pair.
        If a given `since` or `or` date query is given, the historical data will be truncated to
        the specified dates.
        It's noteworthy that this endpoint consume a huge amount of resource in backend when `since`
        and `to` date range are too large. Use with caution.
    """
    timestamp = datetime.now(timezone.utc)

    empty_record = {
        'visa_type': visa_type,
        'embassy_code': embassy_code,
        'time_range': [timestamp - timedelta(days=1), timestamp],
        'available_dates': []
    }
    hist_visa_status = (
        DB.VisaStatus.find_visa_status_past24h(visa_type, embassy_code, timestamp) or
        empty_record
    )

    return hist_visa_status


@app.post('/subscribe/email/{step}')
def post_email_subscription(step: EmailSubsStep, subscription: EmailSubscription = Body(..., embed=True)):
    """ Post email subscription."""
    subscription = subscription.dict()
    subs_lst = [
        (
            subs['visa_type'],
            subs['code'],
            (subs['till'] or datetime.max).astimezone(tz=None)  # TODO: untested
        ) for subs in subscription['subscription']
    ]

    if step == EmailSubsStep.confirming:
        # TODO: construct the email addresses. send the email. new unsubscribe route
        Notifier.send_subscription_confirmation(subscription['email'], subs_lst)
        return Response(status_code=status.HTTP_202_ACCEPTED)

    elif step == EmailSubsStep.subscribed:
        updated_subscriber = DB.Subscription.add_email_subscription(subscription['email'], subs_lst)

        return updated_subscriber


@app.get('/test')
def test(dt: datetime):
    """ Log the datetime."""
    print(dt, dt.astimezone())
    print(dt.strftime('%Z%z'), dt.astimezone().strftime('%Z%z'))
    return dt
