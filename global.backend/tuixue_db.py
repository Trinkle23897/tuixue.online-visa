""" A mimic MongoDB based on a JSON file =.="""
import json
import global_var as G
from typing import List
from datetime import datetime
from pprint import pprint


class TuixueDB:
    """ A class that mimics the NoSQL operations to store the email subscription
        to a JSON file.
        The representation of a subscriber:
        ```json
        {
            'email': 'subs@tuixue.online',
            'subscription': [
                {'visa_type': 'F', 'code': 'pp', 'till': 'FOREVER'},
            ]
        }
        ```
    """
    email_subs_data_path = G.EMAIL_SUBSCRIPTION_PATH
    email_subscription = []

    @classmethod
    def initiate_db(cls):
        """ Initiate the database. Try read the JSON file into memory if there is
            data, otherwise dump an empty list into it.
        """
        try:
            with open(cls.email_subs_data_path) as f:
                cls.email_subscription = json.load(f)
        except json.decoder.JSONDecodeError:
            with open(cls.email_subs_data_path, 'w') as f:
                json.dump(cls.email_subscription, f)

    @classmethod
    def save(cls):
        """ Save the change of subscrition to file."""
        with open(cls.email_subs_data_path, 'w') as f:
            json.dump(cls.email_subscription, f, indent=4)

    @classmethod
    def find_by_email(cls, email: str):
        """ Find a subscriber by email address."""
        return next((subs for subs in cls.email_subscription if subs['email'] == email), None)

    @classmethod
    def find_by_visa_type(cls, visa_type: str, exclude_expired: bool = True):
        """ Find a subscriber by subscribed visa type."""
        result = []
        for subscriber in cls.email_subscription:
            for subs in subscriber['subscription']:
                if subs['visa_type'] == visa_type:
                    if (not exclude_expired
                            or subs['till'] == 'FOREVER'
                            or datetime.strptime(subs['till'], '%Y/%m/%d') > datetime.today()):
                        result.append(subscriber)
                        break

        return result or None

    @classmethod
    def find_by_code(cls, code: str, exclude_expired: bool = True):
        """ Find a subscriber by embassy code."""
        result = []
        for subscriber in cls.email_subscription:
            for subs in subscriber['subscription']:
                if subs['code'] == code:
                    if (not exclude_expired
                            or subs['till'] == 'FOREVER'
                            or datetime.strptime(subs['till'], '%Y/%m/%d') > datetime.today()):
                        result.append(subscriber)
                        break

        return result or None

    @classmethod
    def find_by_visa_type_and_code(cls, visa_type: str, code: str, exclude_expired: bool = True):
        """ Find all subscribers by visa type and code."""
        result_by_visa_type = cls.find_by_visa_type(visa_type, exclude_expired) or []
        result_by_code = cls.find_by_code(code, exclude_expired) or []

        return [subs for subs in result_by_visa_type if subs in result_by_code] or None

    @classmethod
    def create_subscriber(cls, email: str, subscription: List[dict] = []):
        """ Create an subscriber object and insert into the database.
            Subscription dict should be in the following format:
            ```json
            [
                {'visa_type': visa_type, 'code': embassy_code, 'till': date},
                ...
            ]
            ```
            where `till` can be a datetime string in format of YYYY/MM/DD or
            string 'FOREVER' indicating no end day of subscription.
        """
        subs_keys = ('visa_type', 'code', 'till')
        for subs in subscription:
            for key in subs_keys:
                if key not in subs:
                    raise ValueError(f'Invalid subscription object: {subs}')

        new_subscriber = {'email': email, 'subscription': subscription}
        cls.email_subscription.append(new_subscriber)

    @classmethod
    def delete_subscriber(cls, email: str):
        """ Remove a subscriber by email.
            Return deleted object.
        """
        subscriber = cls.find_by_email(email)
        if subscriber is not None:
            return cls.email_subscription.pop(cls.email_subscription.index(subscriber))

    @classmethod
    def add_subscription(cls, email: str, new_subscription: List[dict]):
        """ Add subscription for a given email address.
            If the email doesn't exist, create a new subscriber.
        """
        subscriber = cls.find_by_email(email)
        if subscriber is not None:
            subscriber['subscription'].extend(new_subscription)
        else:
            cls.create_subscriber(email, new_subscription)

    @classmethod
    def remove_subscription(cls, email: str, removing_subscription: List[dict]):
        """ Remove subscription from a given email address.
            If the subscription list become empty, remove the subscriber.
        """
        subscriber = cls.find_by_email(email)
        removing_targets = [(unsubs['visa_type'], unsubs['code']) for unsubs in removing_subscription]
        if subscriber is not None:
            subscriber['subscription'] = [
                subs for subs in subscriber['subscription']
                if (subs['visa_type'], subs['code']) not in removing_targets
            ]

            if len(subscriber['subscription']) == 0:
                deleted_subs = cls.delete_subscriber(email)
                print('Deleted: ', deleted_subs)


def simple_test():
    """ Simple testing for TuixueDB."""
    # Manual testing for the TuixueDB
    subs0 = {
        'email': 'email0@tuixue.online',
        'subscription': [
            {'visa_type': 'F', 'code': 'pp', 'till': 'FOREVER'},
            {'visa_type': 'F', 'code': 'bj', 'till': '2020/12/13'},
        ]
    }

    subs1 = {
        'email': 'email1@tuixue.online',
        'subscription': [
            {'visa_type': 'F', 'code': 'sh', 'till': '2020/11/30'},
            {'visa_type': 'B', 'code': 'pp', 'till': '2020/11/30'}
        ]
    }

    TuixueDB.initiate_db()
    TuixueDB.create_subscriber(**subs0)
    TuixueDB.create_subscriber(**subs1)

    pprint(TuixueDB.email_subscription)

    # res = TuixueDB.find_by_visa_type_and_code(visa_type='B', code='pp')
    # pprint(res)
    TuixueDB.add_subscription(
        'email1@tuixue.online',
        [
            {'visa_type': 'H', 'code': 'sy', 'till': '2020/11/23'}
        ]
    )
    pprint(TuixueDB.email_subscription)

    print('-' * 20)
    TuixueDB.remove_subscription(
        'email1@tuixue.online',
        [
            {'visa_type': 'F', 'code': 'sh'}
        ]
    )
    pprint(TuixueDB.find_by_email('email1@tuixue.online'))
    TuixueDB.remove_subscription(
        'email1@tuixue.online',
        [
            {'visa_type': 'H', 'code': 'sy'},
            {'visa_type': 'B', 'code': 'pp'},
        ]
    )
    pprint(TuixueDB.find_by_email('email1@tuixue.online'))
    pprint(TuixueDB.email_subscription)


def populate_test_user():
    TuixueDB.initiate_db()
    email = 'benjamincaiyh+tuixue.test@gmail.com'
    subscriptions = []
    for visa_type in G.VISA_TYPES:
        for embassy in G.USEmbassy.get_embassy_lst():
            subscriptions.append({'visa_type': visa_type, 'code': embassy.code, 'till': 'FOREVER'})
    TuixueDB.add_subscription(email, subscriptions)
    TuixueDB.save()

if __name__ == "__main__":
    populate_test_user()
