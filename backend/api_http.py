""" RESTful API for http://tuixue.online/visa/"""

from enum import Enum
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from threading import Lock

from fastapi import FastAPI, Body, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import global_var as G
import tuixue_mongodb as DB
from notifier import Notifier
from tuixue_typing import VisaType, EmbassyCode
from util import dt_to_utc, httpdate

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


class EmailUnsubsStep(str, Enum):
    confirming = 'confirming'
    deleted = 'deleted'


# These classes serve for the purpose of request body type chechking for FastAPI
class SingleSubscription(BaseModel):
    visa_type: VisaType
    code: List[EmbassyCode]
    till: Optional[datetime]


class EmailSubscription(BaseModel):
    email: str
    subscription: List[SingleSubscription]


class EmailUnsubscription(BaseModel):
    email: str
    unsubscription: Optional[List[SingleSubscription]] = []


@app.get('/')
def handshake():
    """ Index page that returns a 200 status with a OK message."""
    return {'status_code': 200, 'msg': 'OK'}


metadata = {
    'region': G.USEmbassy.get_region_mapping(),
    'region_country_embassy_tree': G.USEmbassy.get_region_country_embassy_tree(),
    'embassy_lst': G.EMBASSY_ATTR,
    'visa_type_details': G.VISA_TYPE_DETAILS,
    'default_filter': G.DEFAULT_FILTER,
    'nondomestic_default_filter': G.NONDOMESTIC_DEFAULT_FILTER,
    'region_attr': G.REGION_ATTR,
    'qq_tg_info': {
        'qq': G.SECRET['qq']['info'],
        'tg': G.SECRET['telegram']['info'],
    },
    'additional_info': G.ADDITIONAL_INFO,
    'cancel_date': G.CANCEL_DATE,
}


@app.get('/visastatus/meta')
def get_meta_data(response: Response):
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
            ["name_cn", "name_en", "code", "sys", "region", "continent", "country", "tz_info", "crawler_code"]
        ]
        ```
    """
    response.headers["Cache-Control"] = "public"
    now = datetime.now(timezone.utc)
    response.headers["Expires"] = httpdate(now + timedelta(days=1))
    return metadata


@app.get('/visastatus/overview')
def get_visa_status_overview(
    response: Response,
    visa_type: List[VisaType] = Query(...),
    embassy_code: List[EmbassyCode] = Query(...),
    since: Optional[datetime] = datetime.now(timezone.utc) - timedelta(days=15),
    to: Optional[datetime] = datetime.now(timezone.utc),
):
    """ Get the available visa appointment status with given query.
        The `since` and `to` query params, if provided, MUST be in the timezone of UTC.
    """
    response.headers["Cache-Control"] = "public"
    now = datetime.now(timezone.utc)
    response.headers["Expires"] = httpdate(now + timedelta(minutes=1))
    if to > now:
        to = now
    if since > now:
        since = now
    keys = "".join(visa_type) + "".join(list(sorted(embassy_code)))
    cache_since, cache_to, cache_result = G.OVERVIEW_CACHE.get(keys, (None, None, None))
    if cache_result is None or abs(to - cache_to) > timedelta(minutes=1) or abs(since - cache_since) > timedelta(minutes=1):
        tabular_data = DB.VisaStatus.find_visa_status_overview_embtz(visa_type, embassy_code, since, to)
        G.OVERVIEW_CACHE[keys] = (since, to, tabular_data)
    else:
        tabular_data = cache_result

    return {
        'visa_type': visa_type,
        'embassy_code': embassy_code,
        'since': since,
        'to': to,
        'visa_status': tabular_data,
    }


@app.get('/visastatus/detail')
def get_visa_status_detail(
    visa_type: VisaType = Query(...),
    embassy_code: List[EmbassyCode] = Query(...),
    timestamp: Optional[datetime] = datetime.now(timezone.utc),
):
    """ Return all of the historical data fetched for a given `(visa_type, embassy_code)` pair.
        If a given `since` or `or` date query is given, the historical data will be truncated to
        the specified dates.
    """
    if not isinstance(embassy_code, list):
        embassy_code = [embassy_code]
    embassy_code = list(set(embassy_code))
    now = datetime.now(timezone.utc)
    #if timestamp > now:
    #    timestamp = now
    time_range = [
        dt_to_utc((timestamp - timedelta(days=1)), remove_second=True),
        dt_to_utc(timestamp, remove_second=True),
    ]

    keys = visa_type + "".join(list(sorted(embassy_code)))
    cache_timestamp, cache_result = G.DETAIL_CACHE.get(keys, (None, None))
    if cache_result is None or abs(timestamp - cache_timestamp) > timedelta(minutes=1):
        detail = []
        for e in embassy_code:
            single_result = DB.VisaStatus.find_visa_status_past24h_turning_point(visa_type, e, timestamp)
            if single_result:
                single_result = single_result['available_dates']
            else:
                single_result = [{'write_time': time_range[0], 'available_date': None}]
            detail.append({'embassy_code': e, 'available_dates': single_result})
        G.DETAIL_CACHE[keys] = (timestamp, detail)
    else:
        detail = cache_result
    return {
        'visa_type': visa_type,
        'embassy_code': embassy_code,
        'time_range': time_range,
        'detail': detail,
    }


@app.post('/email/subscription/{step}')
def post_email_subscription(step: EmailSubsStep, subscription: EmailSubscription = Body(..., embed=True)):
    """ Post email subscription."""
    subscription = subscription.dict()
    subs_lst = [
        (
            subs['visa_type'],
            code,
            (subs['till'] or datetime.max)
        ) for subs in subscription['subscription'] for code in subs['code']
    ]

    if step == EmailSubsStep.confirming:
        # TODO: construct the email addresses. send the email. new unsubscribe route
        Notifier.send_subscription_confirmation(subscription['email'], subs_lst)
        return Response(status_code=status.HTTP_202_ACCEPTED)

    elif step == EmailSubsStep.subscribed:
        DB.Subscription.add_email_subscription(subscription['email'], subs_lst)
        return Response(status_code=status.HTTP_204_NO_CONTENT)


# @app.get('/subscription/email')
def get_email_subscription(email: str = Query(...)):
    """ Get the subscription record of a email address."""
    return DB.Subscription.get_subscriptions_by_email(email)


@app.post('/email/unsubscription/{step}')
def delete_email_subscription(step: EmailUnsubsStep, unsubscription: EmailUnsubscription = Body(..., embed=True)):
    """ Delete the subscription under the given email."""
    unsubscription = unsubscription.dict()
    # unsubs_lst = [
    #     (unsubs['visa_type'], code) for unsubs in unsubscription['unsubscription'] for code in unsubs['code']
    # ]

    # if step == EmailUnsubsStep.confirming:
    #     Notifier.send_unsubscription_confirmation(unsubscription['email'])
    #     return Response(status_code=status.HTTP_202_ACCEPTED)

    # elif step == EmailUnsubsStep.deleted:
    unsubs_lst = DB.Subscription.get_subscriptions_by_email(unsubscription['email'])
    if len(unsubs_lst) > 0:
        unsubs_lst = [(unsubs['visa_type'], unsubs['embassy_code']) for unsubs in unsubs_lst]
        DB.Subscription.remove_email_subscription(unsubscription['email'], unsubs_lst)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get('/test')
def test(dt: datetime):
    """ Log the datetime."""
    print(dt, dt.astimezone())
    print(dt.strftime('%Z%z'), dt.astimezone().strftime('%Z%z'))
    return dt
