""" Functionality for sending notification for visa status change as well as
    confirmation for email subscription.
"""
import os
import json
import requests
import tuixue_mongodb as DB
from datetime import datetime
from typing import List, Optional
from tuixue_typing import VisaType
from global_var import USEmbassy, VISA_TYPE_DETAILS

with open(os.path.join(os.curdir, 'config', 'secret.json')) as f:
    SECRET = json.load(f)

VISA_STATUS_CHANGE_TITLE = '[tuixue.online] {visa_detail} Visa Status Change'
VISA_STATUS_CHANGE_CONTENT = """
    {send_time}<br>
    {location} changed from {old_status} to {new_status}.<br>
    <br>
    See <a href="">Some link to the website</a> for more detail.<br>
    If you want to change your subscribe option, please re-submit a
    request over <a href="">Some link to the website</a>.
"""

SUBSCRIPTION_CONFIRMATION_TITLE = '[tuixue.online] Subscription Confirmation of {email}'
SUBSCRIPTION_CONFIRMATION_CONTENT = """
    Dear subscriber:<br>
    <br>
    A faculty committee at tuixue.online has made a decision on your
    application with email {email} for subcription of following visa types
    and embassies: <br>
    <br>
    {subscription_str}
    <br>
    Please review your decision by logging back into tuixue.online
    application status page at <a href="">this link</a>.<br>
    <br>
    Sincerely,<br>
    <br>
    tuixue.online Graduate Division<br>
    Diversity, Inclusion and Admissions<br>
    <br>
    Please note: This e-mail message was sent from a notification-only<br>
    address that cannot accept incoming e-mail. Please do not reply to<br>
    this message. Please save or print your decision letter and any<br>
    related online documents immediately for your records.<br>
"""


class Notifier:
    """ A class that contains methods for sending notifications visa emails
        and other social media platforms.
    """
    email_request = requests.Session()

    @classmethod
    def send_subscription_confirmation(cls, subscription: dict):
        """ Send the email for confirmation of email subscription."""
        email = subscription['email']
        subs_lst = [(subs['visa_type'], subs['code'], subs['till']) for subs in subscription['subscription']]

        # Show user the {visa_type}-{location} {till}
        subscription_str = '<ul>\n{}</ul>'.format(
            '\n'.join(
                ['<li>{visa_type}-{code} till {till}</li>'.format(
                    visa_type=visa_type,
                    code=code,
                    till=till,
                ) for (visa_type, code, till) in subs_lst]
            )
        )
        sent = cls.send_email(
            title=SUBSCRIPTION_CONFIRMATION_TITLE.format(email=email),
            content=SUBSCRIPTION_CONFIRMATION_CONTENT.format(
                email=email,
                subscription_str=subscription_str,
            ),
            receivers=[email]
        )
        return sent

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
        res = cls.email_request.post(SECRET['email'], data=data)

        return res.status_code == 200

    @classmethod
    def notify_visa_status_change(
        cls,
        visa_type: VisaType,
        embassy: USEmbassy,
        available_date: Optional[datetime],
    ) -> bool:
        """ Determine whether or not a email notification should be sent.
            And send the notification if needed.
            Return a flag indicating wheter the email is sent or not.
        """
        latest_written = DB.VisaStatus.find_latest_written_visa_status(visa_type, embassy.code)
        if latest_written is None:  # when the new code deploy into production
            return False

        last_available_date = latest_written['available_date']

        if available_date is None:
            return False
        else:
            email_lst = DB.Subscription.get_email_list(
                new_visa_status=(visa_type, embassy.code, available_date),
                inclusion='effective_only',  # if the available date surpass the effective date
            )[(visa_type, embassy.code)]

            if (last_available_date is None or last_available_date != available_date) and len(email_lst) > 0:
                old_status = '/' if last_available_date is None else last_available_date.strftime('%Y/%m/%d')
                new_status = available_date.strftime('%Y/%m/%d')

                success = cls.send_email(
                    title=VISA_STATUS_CHANGE_TITLE.format(visa_detail=VISA_TYPE_DETAILS[visa_type]),
                    content=VISA_STATUS_CHANGE_CONTENT.format(
                        send_time=datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                        location=embassy.name_en,
                        old_status=old_status,
                        new_status=new_status,
                    ),
                    receivers=email_lst
                )
                return success
            else:
                return False
