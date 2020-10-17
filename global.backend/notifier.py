""" Functionality for sending notification for visa status change as well as
    confirmation for email subscription.
"""
import os
import json
import util
import queue
import requests
from typing import List
from tuixue_db import TuixueDB
from datetime import datetime, timedelta
from global_var import USEmbassy, VISA_TYPE_DETAILS

with open(os.path.join(os.curdir, 'config', 'secret.json')) as f:
    SECRET = json.load(f)

VISA_STATUS_CHANGE_TITLE = '[tuixue.online] {visa_detail} Visa Status Change'
VISA_STATUS_CHANGE_CONTENT = \
"""
{send_time}
{location} changed from {old_status} to {new_status}.

See <a href="">Some link to the website</a> for more detail.
If you want to change your subscribe option, please re-submit a request over <a href="">Some link to the website</a>.
"""



class Notifier:
    """ A class that contains methods for sending notifications visa emails
        and other social media platforms.
    """
    notification_task_queue = queue.Queue()  # queue of (visa_type, embassy.code, new_visa_status_str)
    email_request = requests.Session()

    @staticmethod
    def visa_status_is_changed(file_path: str, new_visa_status: List[int]):
        """ Determine if a notification should be sent to the subscribers."""
        year, month, day = new_visa_status
        new_latest_date = datetime(year=year, month=month, day=day)
        try:
            old_latest_date = util.get_latest_update_dt(file_path)
        except util.EmptyDataFile:  # the first updated status of the date
            today = datetime.strptime('/'.join(file_path.split('/')[-3:]), '%Y/%m/%d')
            yesterday = today - timedelta(days=1)
            yesterday_fp = '/'.join([
                *file_path.split('/')[:-3],
                yesterday.strftime('%Y'),
                yesterday.strftime('%m'),
                yesterday.strftime('%d'),
            ])
            try:
                old_latest_date = util.get_latest_update_dt(yesterday_fp)
            except util.EmptyDataFile:  # yesterday has no update
                return True, '/', f'{year}/{month}/{day}'
            else:
                return (
                    new_latest_date != old_latest_date,
                    old_latest_date.strftime('%Y/%m/%d'),
                    new_latest_date.strftime('%Y/%m/%d'),
                )
        else:
            return (
                new_latest_date != old_latest_date,
                old_latest_date.strftime('%Y/%m/%d'),
                new_latest_date.strftime('%Y/%m/%d'),
            )

    @classmethod
    def send_email(
        cls,
        title: str,
        content: str,
        receivers: List[str],
        sendfrom: str = 'dean@tuixue.online',
        sendto: str = 'pending@tuixue.online'
    ):
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

    def __init__(self, visa_type: str, location: str):
        self.visa_type = visa_type
        self.embassy = next((e for e in USEmbassy.get_embassy_lst() if e.location == location), None)
        TuixueDB.initiate_db()  # manually update the "database" every before sending notification

    def notify_visa_status_change(self, file_path: str, new_visa_status: List[int]):
        """ Determine and send the notification to the subscribers.
            Returning the should_send_notification flag for logging purpose.
        """
        should_send_notification, old_visa_status , new_visa_status = \
            self.visa_status_is_changed(file_path, new_visa_status)

        if should_send_notification:
            subscribers = TuixueDB.find_by_visa_type_and_code(self.visa_type, self.embassy.code)
            sent_result = self.send_email(
                title=VISA_STATUS_CHANGE_TITLE.format(visa_detail=VISA_TYPE_DETAILS[self.visa_type]),
                content=VISA_STATUS_CHANGE_CONTENT.format(
                    send_time=datetime.now().strftime('%Y/%m/%d %H/%M/%S'),
                    location=self.embassy.name_en,
                    old_status=old_visa_status,
                    new_status=new_visa_status,
                ),
                receivers=[subs['email'] for subs in subscribers]
            )
            return True
        else:
            return False


if __name__ == "__main__":
    result = Notifier('F', '金边').notify_visa_status_change(util.construct_data_file_path('F', '金边'), [2021, 1, 6])
    print(result)