""" Functionality for sending notification for visa status change as well as
    confirmation for email subscription.
"""
import json
import asyncio
import requests
import websockets
import tuixue_mongodb as DB
from datetime import datetime
from tuixue_typing import EmbassyCode, VisaType
from typing import Any, Dict, List, Optional, Tuple
from fastapi.encoders import jsonable_encoder
from global_var import USEmbassy, VISA_TYPE_DETAILS, SECRET, FRONTEND_BASE_URI, DEFAULT_FILTER
from url import URL


VISA_STATUS_CHANGE_TITLE = '[tuixue.online] {visa_detail} Visa Status Change'
VISA_STATUS_CHANGE_CONTENT = """
    {send_time}<br>
    {location} changed from {old_status} to {new_status}.<br>
    <br>
    See <a href="https://{base_uri}/visa">https://{base_uri}/visa</a> for more detail.<br>
    If you want to change your subscribe option, please re-submit a request over
    <a href="">Some link to the website</a>.
"""
# TODO: add the frontend href attr here.
# TODO: unsubscribe link

SUBSCRIPTION_CONFIRMATION_TITLE = '(PLEASE CONFIRM) - Your Application Decision from tuixue.online'
SUBSCRIPTION_CONFIRMATION_CONTENT = """
    Dear {user}:<br>
    <br>
    A faculty committee at tuixue.online has made a decision on your application with email
    {email} for subcription of following visa types and embassies/consulate.<br>
    <b>Please review your decision by logging back into tuixue.online application status
    page at <a href="{confirmation_url}">this link</a></b>. Otherwise, the above application
    record will be cleared.<br>
    {subscription_str}
    <br>
    Sincerely,<br>
    <br>
    tuixue.online Graduate Division<br>
    Diversity, Inclusion and Admissions<br>
    <br>
    Please note: This e-mail message was sent from a notification-only address that cannot
    accept incoming e-mail. Please do not reply to this message. Please save or print your
    decision letter and any related online documents immediately for your records.<br>
"""

UNSUBSCRIPTION_CONFIRMATION_TITLE = '(PLEASE CONFIRM) - Your Unsubscription from tuixue.online'
UNSUBSCRIPTION_CONFIRMATION_CONTENT = """
    Dear {user}:<br>
    <br>
    This email is to confirm {email} for unsubcription of following visa types and embassies/consulate.<br>
    {unsubscription_str}
    <br>
    Or click <a href="{unsubscribe_all_url}">this link</a> to unsubscribe all subscription.
    <br>
    Sincerely,<br>
    <br>
    tuixue.online Graduate Division<br>
    Diversity, Inclusion and Admissions<br>
    <br>
    Please note: This e-mail message was sent from a notification-only address that cannot
    accept incoming e-mail. Please do not reply to this message. Please save or print your
    decision letter and any related online documents immediately for your records.<br>
"""
UNSUBSCRIPTION_EMPTY_SUBS_TITLE = '(CATCHA ;-) - You don\'t have any subscription in {email}'
UNSUBSCRIPTION_EMPTY_SUBS_CONTENT = """
    Dear {user}:<br>
    <br>
    Thie email address {email} either has 0 subscription from tuixue.online or the Visa type and embassy you
    are unsubscribing are not subscribed at the first place.
    <br>
    Feel free to check out <a href="https://dev.tuixue.online/visa">our website</a> for info of U.S. Visa interview appointment around
    the global!
    <br>
    Sincerely,<br>
    <br>
    tuixue.online Graduate Division<br>
    Diversity, Inclusion and Admissions<br>
    <br>
    Please note: This e-mail message was sent from a notification-only address that cannot
    accept incoming e-mail. Please do not reply to this message. Please save or print your
    decision letter and any related online documents immediately for your records.<br>
"""


class Notifier:
    """ A class that contains methods for sending notifications visa emails
        and other social media platforms.
    """
    email_request = requests.Session()

    @classmethod
    def send_subscription_confirmation(cls, email: str, subs_lst: List[DB.EmailSubscription]):
        """ Send the email for confirmation of email subscription."""
        confirmation_url = URL(f'https://{FRONTEND_BASE_URI}/visa/email/subscription')
        # confirmation_url = URL(f'http://localhost:3000/visa/email/subscription')
        confirmation_url.query_param.set('email', email)
        for visa_type, code, till in subs_lst:
            confirmation_url.query_param.append('visa_type', visa_type)
            confirmation_url.query_param.append('code', code)
            confirmation_url.query_param.append('till', till)

        subscription_str = '<ul>\n{}\n</ul>'.format(
            '\n'.join(['<li>{} Visa at {} till {}.</li>'.format(
                VISA_TYPE_DETAILS[vt],
                next((e.name_en for e in USEmbassy.get_embassy_lst() if e.code == ec), 'None'),
                tl.strftime('%Y/%m/%d') if tl != datetime.max else 'FOREVER',
            ) for vt, ec, tl in subs_lst])
        )

        content = SUBSCRIPTION_CONFIRMATION_CONTENT.format(
            user=email.split('@')[0],
            email=email,
            subscription_str=subscription_str,
            confirmation_url=confirmation_url,
        )

        for _ in range(10):  # for robust
            sent = cls.send_email(
                title=SUBSCRIPTION_CONFIRMATION_TITLE.format(email=email),
                content=content,
                receivers=[email]
            )
            if sent:
                break
        else:
            sent = False

        return sent

    @classmethod
    def send_unsubscription_confirmation(cls, email: str, unsubs_lst: List[DB.EmailSubscriptionNoDate]):
        """ Send the email for confirmation of email unsubscription. """
        subs_lst_by_email = DB.Subscription.get_subscriptions_by_email(email)
        unsubs_url = URL(f'https://{FRONTEND_BASE_URI}/visa/email/unsubscription')  # Unsubscription confirmation url
        # unsubs_url = URL(f'http://localhost:3000/visa/email/unsubscription')  # Unsubscription confirmation url
        unsubs_url.query_param.set('email', email)

        
        unsubs_all_url = unsubs_url.copy()
        unsubs_info = []
        for subs in subs_lst_by_email:
            if (subs['visa_type'], subs['embassy_code']) in unsubs_lst:
                url = unsubs_url.copy()
                url.query_param.set('visa_type', subs['visa_type'])
                url.query_param.set('embassy_code', subs['embassy_code'])
                unsubs_info.append((subs['visa_type'], subs['embassy_code'], subs['till'], subs['expired'], url))

                unsubs_all_url.query_param.append('visa_type', subs['visa_type'])
                unsubs_all_url.query_param.append('embassy_code', subs['embassy_code'])

        if len(unsubs_info) == 0:  # If the user has no subscription or is messing with us, we will know
            for _ in range(10):
                sent = cls.send_email(
                    title=UNSUBSCRIPTION_EMPTY_SUBS_TITLE.format(email=email),
                    content=UNSUBSCRIPTION_EMPTY_SUBS_CONTENT.format(user=email.split('@')[0], email=email),
                    receivers=[email],
                )
                if sent:
                    break
            else:
                sent = False

            return sent

        unsubscription_str = '<ul>\n{}\n</ul>'.format(
            '\n'.join(['<li>{} Visa at {} {} on {}: click <a href="{}">this link</a> to unsubscribe.</li>'.format(
                VISA_TYPE_DETAILS[vt],
                next((e.name_en for e in USEmbassy.get_embassy_lst() if e.code == ec), 'None'),
                'expired' if exp else 'expiring',
                tl.strftime('%Y/%m/%d') if tl != datetime.max else 'FOREVER',
                url,
            ) for vt, ec, tl, exp, url in unsubs_info])
        )

        content = UNSUBSCRIPTION_CONFIRMATION_CONTENT.format(
            user=email.split('@')[0],
            email=email,
            unsubscription_str=unsubscription_str,
            unsubscribe_all_url=unsubs_all_url,
        )

        for _ in range(10):
            sent = cls.send_email(
                title=UNSUBSCRIPTION_CONFIRMATION_TITLE,
                content=content,
                receivers=[email]
            )

            if sent:
                break
        else:
            sent = False

        return sent

    @classmethod
    async def send_via_websocket(cls, data: Dict[str, Any]) -> None:
        """ Send an object in JSON string visa websocket."""
        ws_url, ws_token = SECRET['websocket_url'], SECRET['websocket_token']
        async with websockets.connect(f'{ws_url}?token={ws_token}') as ws:
            data_str = json.dumps(jsonable_encoder(data))
            await ws.send(data_str)

    @classmethod
    def send_email(
        cls,
        title: str,
        content: str,
        receivers: List[str],
        sendfrom: str = 'dean@tuixue.online',
        sendto: str = 'pending@tuixue.online'
    ) -> bool:
        """ Send email to receviers."""
        data = {
            'title': title,
            'content': content,
            'receivers': '@@@'.join(receivers),
            'sendfrom': sendfrom,
            'sendto': sendto
        }
        res = cls.email_request.post(SECRET['email'], data=data, proxies=SECRET['email_proxy'])

        return 'success' in res.text

    @classmethod
    def send_qq_tg(
        cls,
        embassy: USEmbassy,
        prev: Optional[datetime],
        curr: Optional[datetime],
    ) -> bool:
        """ Send notification to QQ group and Telegram channel."""
        def converter(d: Optional[datetime]) -> str:
            if d is None:
                return "/"
            if d.year == datetime.now().year:
                return f'{d.month}/{d.day}'
            return f'{d.year}/{d.month}/{d.day}'
        prev, curr = converter(prev), converter(curr)
        content = f"{embassy.name_cn}: {prev} -> {curr}"
        # qq
        extra = SECRET["qq"]
        base_uri = extra["mirai_base_uri"]
        auth_key = extra["mirai_auth_key"]
        qq_num = extra["qq_num"]
        if embassy.region == "DOMESTIC":
            group_id = extra["qq_group_id"]["domestic"]
        elif embassy.code in DEFAULT_FILTER:
            group_id = extra["qq_group_id"]["non_domestic"]
        else:
            group_id = []
        if group_id:
            r = requests.post(base_uri + "/auth",
                              data=json.dumps({"authKey": auth_key})).json()
            session = r["session"]
            requests.post(base_uri + "/verify",
                          data=json.dumps({"sessionKey": session, "qq": qq_num}))
            for g in group_id:
                requests.post(base_uri + "/sendGroupMessage", data=json.dumps(
                    {"sessionKey": session, "target": g, "messageChain": [{
                        "type": "Plain",
                        "text": f"{content}\n详情: https://{FRONTEND_BASE_URI}/visa/"
                    }]}))
            requests.post(base_uri + "/release",
                          data=json.dumps({"sessionKey": session, "qq": qq_num}))
        # tg
        # TODO

    @classmethod
    def notify_visa_status_change(
        cls,
        visa_type: VisaType,
        embassy: USEmbassy,
        available_date: Optional[datetime],
    ) -> bool:
        """ Determine whether or not a email notification should be sent. And send the notification
            if needed. Return a flag indicating wheter the email is sent or not.

            Only notify user when one of two condition below is satisfied:
            1. `last_available_date` is None and `available_date` is not None
            2. `last_available_date` is datetime and `available_date` is an earlier datetime
        """
        latest_written_lst = DB.VisaStatus.find_latest_written_visa_status(visa_type, embassy.code)
        if len(latest_written_lst) == 0:  # when the new code deploy into production
            return False

        last_available_date = latest_written_lst[0]['available_date']
        if available_date is None:
            return False
        if last_available_date is None or available_date < last_available_date:
            # email
            email_dct = DB.Subscription.get_email_list(
                new_visa_status=(visa_type, embassy.code, available_date),
                inclusion='effective_only',  # if the available date surpass the effective date
            )  # should return an one-element dictionary

            if (visa_type, embassy.code) in email_dct:
                email_lst = email_dct[(visa_type, embassy.code)]
                if len(email_lst) > 0:
                    old_status = '/' if last_available_date is None else last_available_date.strftime('%Y/%m/%d')
                    new_status = available_date.strftime('%Y/%m/%d')

                    cls.send_email(
                        title=VISA_STATUS_CHANGE_TITLE.format(visa_detail=VISA_TYPE_DETAILS[visa_type]),
                        content=VISA_STATUS_CHANGE_CONTENT.format(
                            send_time=datetime.now().strftime('%Y/%m/%d %H:%M:%S GMT+8'),
                            location=embassy.name_en,
                            old_status=old_status,
                            new_status=new_status,
                            base_uri=FRONTEND_BASE_URI,
                        ),
                        receivers=email_lst,
                    )
            # websocket
            ws_data = {
                'visa_type': visa_type,
                'embassy_code': embassy.code,
                'prev_avai_date': last_available_date,
                'curr_avai_date': available_date
            }
            asyncio.run(cls.send_via_websocket(ws_data))

            # QQ/TG, need async
            if visa_type == "F":
                cls.send_qq_tg(embassy, last_available_date, available_date)

            return True
        return False
