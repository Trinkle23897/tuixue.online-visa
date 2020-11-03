""" Functionality for sending notification for visa status change as well as
    confirmation for email subscription.
"""
import requests
import tuixue_mongodb as DB
from datetime import datetime
from typing import List, Optional
from tuixue_typing import VisaType
from urllib.parse import urlencode, urlunsplit, quote
from global_var import USEmbassy, VISA_TYPE_DETAILS, SECRET, MAX_EMAIL_SENT


VISA_STATUS_CHANGE_TITLE = '[tuixue.online] {visa_detail} Visa Status Change'
VISA_STATUS_CHANGE_CONTENT = """
    {send_time}<br>
    {location} changed from {old_status} to {new_status}.<br>
    <br>
    See <a href="">Some link to the website</a> for more detail.<br>
    If you want to change your subscribe option, please re-submit a
    request over <a href="">Some link to the website</a>.
"""  # TODO: add the frontend href attr here.

SUBSCRIPTION_CONFIRMATION_TITLE = '[tuixue.online] Subscription Confirmation of {email}'
SUBSCRIPTION_CONFIRMATION_CONTENT = """
    Dear subscriber:<br>
    <br>
    A faculty committee at tuixue.online has made a decision on your
    application with email {email} for subcription of following visa types and embassies/consulate:<br>
    {subscription_str}
    Please review your decision by logging back into tuixue.online
    application status page at <a href="{confirmation_url}"><strong>this link</strong></a>.<br>
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
    def send_subscription_confirmation(cls, email: str, subs_lst: List[DB.EmailSubscription]):
        """ Send the email for confirmation of email subscription."""
        query_dct = {'visa_type': [], 'code': [], 'till': []}
        for visa_type, code, till in subs_lst:
            query_dct['visa_type'].append(visa_type)
            query_dct['code'].append(code)
            query_dct['till'].append(till)

        # Construct the redirect frontend url
        confirmation_url = urlunsplit(
            ('https', 'tuixue.online', '/subscription/email', urlencode(query_dct, doseq=True, quote_via=quote), '')
        )

        subscription_str = '<ul>\n{}\n</ul>'.format(
            '\n'.join(['<li>{} Visa at {} till {}.</li>'.format(
                vt,
                next((e.name_en for e in USEmbassy.get_embassy_lst() if e.code == ec), 'None'),
                tl.strftime('%Y/%m/%d') if tl != datetime.max else 'FOREVER',
            ) for vt, ec, tl in subs_lst])
        )

        content = SUBSCRIPTION_CONFIRMATION_CONTENT.format(
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

        return 'success' in res.text

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
        else:
            email_dct = DB.Subscription.get_email_list(
                new_visa_status=(visa_type, embassy.code, available_date),
                inclusion='effective_only',  # if the available date surpass the effective date
            )  # should return an one-element dictionary

            if (visa_type, embassy.code) in email_dct:
                email_lst = email_dct[(visa_type, embassy.code)]
            else:
                return False

            if (last_available_date is None or available_date < last_available_date) and len(email_lst) > 0:
                old_status = '/' if last_available_date is None else last_available_date.strftime('%Y/%m/%d')
                new_status = available_date.strftime('%Y/%m/%d')

                email_sent = []  # handling maximum email sent
                for step in range(len(email_lst) // MAX_EMAIL_SENT + 1):
                    success = cls.send_email(
                        title=VISA_STATUS_CHANGE_TITLE.format(visa_detail=VISA_TYPE_DETAILS[visa_type]),
                        content=VISA_STATUS_CHANGE_CONTENT.format(
                            send_time=datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                            location=embassy.name_en,
                            old_status=old_status,
                            new_status=new_status,
                        ),
                        receivers=email_lst[step * MAX_EMAIL_SENT: step * MAX_EMAIL_SENT + MAX_EMAIL_SENT]
                    )
                    email_sent.append(success)
                return all(email_sent)
            else:
                return False
