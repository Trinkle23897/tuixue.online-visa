""" Classes for interaction with MongoDB NoSQL
    pymongo gurantees that the MongoClient is thread-safe
"""

import pymongo
from collections import defaultdict
from datetime import datetime, timedelta
from tuixue_typing import VisaType, EmbassyCode
from typing import Union, List, Tuple, Optional, Dict

EmailSubscription = NewVisaStatus = Tuple[VisaType, EmbassyCode, datetime]
EmailSubscriptionNoDate = NewVisaStatusNoDate = Tuple[VisaType, EmbassyCode]  # seeking for a better name...

MONGO_CONFIG = {'host': '127.0.0.1', 'port': 27017, 'database': 'tuixue_dev'}
ATLAS_CONNECTION = 'mongodb+srv://benji:{pwd}@tuixue-dev.jcq33.mongodb.net/{db}?retryWrites=true&w=majority'
MONGO_CLIENT = None


def connect() -> pymongo.database.Database:
    """ Connect to the local MongoDB server. Return a handle of tuixue database."""
    global MONGO_CLIENT
    if MONGO_CLIENT is None:  # keep one alive connection will be enough (and preferred)
        MONGO_CLIENT = pymongo.MongoClient(host=MONGO_CONFIG['host'], port=MONGO_CONFIG['port'])
        # MONGO_CLIENT = pymongo.MongoClient(ATLAS_CONNECTION.format(pwd='benji', db='tuixue'))

    database = MONGO_CLIENT.get_database(MONGO_CONFIG['database'])
    return database


def get_collection(collection_name: str) -> pymongo.collection.Collection:
    """ Return a MongoDB collection from the established client database."""
    db = connect()
    return db.get_collection(collection_name)


class VisaStatus:
    """ MongoDB operations for storing:
        1. All fetched visa status by (visa_type, embassy_code), *only successful fetching*
        2. Latest written time and data, *including failed one*

        The successfully fetched visa status will be stored in Mongo collection `'visa_status'`
        and the latest written time will be stored in Mongo collection `'latest_written'`.

        The schema of documents for `'visa_status'` is as follow:

        ```python
        {
            'visa_type': str,
            'embassy_code': str,
            'available_dates': [
                {'write_time': datetime, 'available_date': datetime},
            ]
        }
        ```

        The schema of documents for `'latest_written'` is as follow:

        ```python
        {
            'visa_type': str,
            'embassy_code': str,
            'write_time': datetime,
            'available_date': datetime,
        }
        ```
   """
    visa_status = get_collection('visa_status')
    latest_written = get_collection('latest_written')

    @classmethod
    def drop(cls, collection: str = 'all') -> None:
        """ THSI METHOD SHOULD BE USED WITH CAUTION (OR DELETED) IN PRODUCTION."""
        if collection not in ('visa_status', 'latest_written', 'all'):
            raise ValueError('collection can only be one of [\'visa_status\', \'latest_written\', \'all\']')

        if collection in ('visa_status', 'all'):
            cls.visa_status.drop()
        if collection in ('latest_written', 'all'):
            cls.latest_written.drop()

    @classmethod
    def save_fetched_visa_status(
        cls,
        visa_type: VisaType,
        embassy_code: EmbassyCode,
        write_time: datetime,
        available_date: Optional[datetime],
    ) -> None:
        """ The method called when a new fetched result is obtained from crawler backend. The
            `'latest_written'` collection will always be modified, whereas the `'available_dates'`
            collection will only be modified when available date is not None
        """
        query = {'visa_type': visa_type, 'embassy_code': embassy_code}
        visa_status_query = {**query, 'write_date': datetime.combine(write_time.date(), datetime.min.time())}
        new_fetch = {'write_time': write_time, 'available_date': available_date}

        if cls.latest_written.find_one(query) is None:
            cls.latest_written.insert_one({**query, **new_fetch})
        else:
            cls.latest_written.update_one(query, {'$set': new_fetch})

        if available_date is not None:
            if cls.visa_status.find_one(visa_status_query) is None:
                cls.visa_status.insert_one({**visa_status_query, 'available_dates': [new_fetch]})
            else:
                cls.visa_status.update_one(visa_status_query, {'$push': {'available_dates': new_fetch}})

    @classmethod
    def find_earliest_visa_status(
        cls,
        visa_type: Union[VisaType, List[VisaType]],
        embassy_code: Union[EmbassyCode, List[EmbassyCode]],
        date: Union[datetime, List[datetime]],
    ) -> List[dict]:
        """ Return a tabular data containing the earliest available appointment date
            of for the given `visa_type`, `embassy_code` and `date`. Lists of `visa_types`,
            `embassy_code` and `date` are also accepted. The returned result will be the
            permutation of the argument lists. The returned tabular data's structure is as
            followed:

            ```py
            [
                {  # each row is indexed with 'date'
                    'date': datetime,
                    'earliest_dates': [
                        {'visa_type': VisaType, 'embassy_code': EmbassyCode, 'earliest_date': datetime},
                    ],
                },
            ]
            ```

            It's noteworthy that:
            1. The rows of tabular data are indexed by 'date' and gurantee to sort in ascending order.
            2. When multiple visa_type and embassy_code are given, the 'earliest_date' field contains
                all the result of the 'date', it's up to the caller to decide how to further propess
                the data.
        """
        if not isinstance(visa_type, list):
            visa_type = [visa_type]
        if not isinstance(embassy_code, list):
            embassy_code = [embassy_code]
        if not isinstance(date, list):
            date = [date]

        # ensure date list is unique and ascendingly sorted and each date is at mid-night
        date = sorted(set([datetime.combine(d.date(), datetime.min.time()) for d in date]))

        tabular_data = []
        for dt in date:
            row = {'date': dt, 'earliest_dates': []}

            for vt in visa_type:
                for emb in embassy_code:
                    cursor = cls.visa_status.aggregate([
                        {'$match': {'visa_type': vt, 'embassy_code': emb, 'write_date': dt}},
                        {'$unwind': '$available_dates'},
                        {
                            '$group': {
                                '_id': None,
                                'visa_type': {'$first': '$visa_type'},
                                'embassy_code': {'$first': '$embassy_code'},
                                'earliest_date': {'$min': '$available_dates.available_date'},
                            },
                        },
                        {'$project': {'_id': False}},
                    ])

                    try:
                        earliest_date = next(cursor)
                    except StopIteration:
                        earliest_date = {'visa_type': vt, 'embassy_code': emb, 'earliest_date': None}

                    row['earliest_dates'].append(earliest_date)
            tabular_data.append(row)

        return tabular_data

    @classmethod
    def find_latest_written_visa_status(
        cls,
        visa_type: Union[VisaType, List[VisaType]],
        embassy_code: Union[EmbassyCode, List[EmbassyCode]],
    ) -> Union[dict, List[dict]]:
        """ Find the latest written visa status of a given visa_type and embassy_code"""
        if not isinstance(visa_type, list):
            visa_type = [visa_type]
        if not isinstance(embassy_code, list):
            embassy_code = [embassy_code]

        latest_written_vs_lst = []
        for vt in visa_type:
            for emb in embassy_code:
                latest_written = cls.latest_written.find_one(
                    filter={'visa_type': vt, 'embassy_code': emb},
                    projection={'_id': False}
                )
                latest_written_vs_lst.append(latest_written)

        return latest_written_vs_lst


class Subscription:
    """ MongoDB operations for storing:
        1. Email subscription - a one-to-few relationship. Comparing to the previous JSON
            based TuixueDB, the difference is that to represent 'subscribe with no end date'
            we use the `datetime.max` instead of a special string. It helps to simplify the
            logic here as suggested by @n+e.
        2. other social media (Telegram, QQ) subscription: HOWTO is to be decided

        The schema of email susbcriber is as following:

        ```python
        {
            'email': str,  # should be unique
            'subscription': [
                {'visa_type': VisaType, 'embassy_code': EmbassyCode, 'till': datetime}
            ]
        }
        ```
    """
    email = get_collection('email_subscription')

    @classmethod
    def get_subscriptions_by_email(cls, email: str):
        """ Get all subscription of a given email"""
        return cls.email.find_one({'email': email}, {'_id': False})

    @classmethod
    def get_email_list(
        cls,
        new_visa_status: Union[NewVisaStatus, List[NewVisaStatus]],
        inclusion: str = 'both',
    ) -> Dict[NewVisaStatusNoDate, List[str]]:
        """ Find all of the email address for given new visa status.
            param `inclusion` spcify the filtering strategy of email list. It can be one of
            `{'both', 'expired_only', 'effective_only'}`, `'expired_only'` returns the email
            whose subscription has expired and `'effective_only'` returns subscription that
            are still effective.
        """
        if inclusion not in ('both', 'expired_only', 'effective_only'):
            raise ValueError('`inclusion` only accept one of \'both\', \'expired_only\' or \'effective_only\'')

        if not isinstance(new_visa_status, list):
            new_visa_status = [new_visa_status]

        email_list = defaultdict(list)
        for visa_type, embassy_code, available_date in new_visa_status:
            all_subs = cls.email.find(
                {'subscription': {'$elemMatch': {'visa_type': visa_type, 'embassy_code': embassy_code}}},
                {'_id': False, 'email': True, 'subscription.$': True}
            )
            for subs in all_subs:
                if (inclusion == 'both' or
                        (inclusion == 'effective_only' and subs['subscription'][0]['till'] >= available_date) or
                        (inclusion == 'expired_only' and subs['subscription'][0]['till'] < available_date)):
                    email_list[(visa_type, embassy_code)].append(subs['email'])

        return dict(email_list)

    @classmethod
    def add_email_subscription(
        cls,
        email: str,
        subscription: Union[EmailSubscription, List[EmailSubscription]],
    ) -> dict:
        """ Add one or more email subscription, create the subscriber document if
            one doesn't exist. And SILENTLY update the subscription if there is a
            same `(visa_type, embassy_code)` subscription exists.

            Return the subscriber after subscipriton edition.
        """
        if not isinstance(subscription, list):
            subscription = [subscription]

        if cls.email.find_one({'email': email}) is None:  # create new subscriber
            cls.email.insert_one({
                'email': email,
                'subscription': [
                    {
                        'visa_type': visa_type,
                        'embassy_code': embassy_code,
                        'till': till,
                    } for visa_type, embassy_code, till in subscription
                ]
            })
        else:  # udpate subscription list of existed subscriber
            for visa_type, embassy_code, till in subscription:
                subs = {'visa_type': visa_type, 'embassy_code': embassy_code, 'till': till}
                existed_subs = cls.email.find_one(
                    {
                        'email': email,
                        'subscription': {'$elemMatch': {'visa_type': visa_type, 'embassy_code': embassy_code}}
                    }
                )  # this query return a subscriber ONLY IF the subscriber subscribes this (visa_type, embassy_code)
                if existed_subs is None:
                    cls.email.update_one({'email': email}, {'$push': {'subscription': subs}})
                else:
                    cls.email.update_one(
                        {
                            'email': email,
                            'subscription.visa_type': visa_type,  # these two lines is equvilent to $elemMatch
                            'subscription.embassy_code': embassy_code
                        },
                        {'$set': {'subscription.$.till': till}}
                    )

        return cls.email.find_one({'email': email})

    @classmethod
    def remove_email_subscription(
        cls,
        email: str,
        unsubscription: Union[EmailSubscriptionNoDate, List[EmailSubscriptionNoDate]],
    ) -> None:
        """ Remove the email subscription from given email address. If the subscription list
            is empty after unsubscribing, the document will be deleted SILIENTLY.
        """
        if not isinstance(unsubscription, list):
            unsubscription = [unsubscription]

        if cls.email.find_one({'email': email}) is None:
            return  # would LOVE to hear about insights on raising an exception here.

        for visa_type, embassy_code in unsubscription:
            # trust the Mongo to handle the missing (visa_type, embassy_code) here
            # not using $pullAll here as $pullAll requires a fully matchnig document
            # where as $pull is matching the given query
            # read more: https://docs.mongodb.com/manual/reference/operator/update/pullAll/#behavior
            cls.email.update_one(
                {'email': email},
                {'$pull': {'subscription': {'visa_type': visa_type, 'embassy_code': embassy_code}}}
            )

        if cls.email.find_one({'email': email, 'subscription': {'$size': 0}}) is not None:
            cls.email.find_one_and_delete({'email': email})


def simple_test_visa_status():
    """ Just a SUPER SIMPLE test..."""
    import random  # SORRY
    from pprint import pprint  # SORRY

    available_dts = [datetime.strptime('2020/10/30', '%Y/%m/%d') + timedelta(days=d) for d in range(20)] + [None]
    write_times_date = [datetime.strptime('2020/9/25', '%Y/%m/%d') + timedelta(days=d) for d in range(5)]

    VisaStatus.drop()
    for visa_type in 'FB':
        for embassy_code in ('pp', 'bj', 'syd'):
            for wtd in write_times_date:
                write_time_by_min = [wtd + timedelta(minutes=m) for m in range(15)]
                for write_time in write_time_by_min:
                    VisaStatus.save_fetched_visa_status(
                        visa_type,
                        embassy_code,
                        write_time,
                        random.choice(available_dts)
                    )

    result = VisaStatus.find_earliest_visa_status(
        ['F', 'B'],
        ['pp', 'syd'],
        [datetime.strptime('2020/9/27', '%Y/%m/%d') + timedelta(days=d) for d in range(3)]
    )
    pprint(result)

    VisaStatus.save_fetched_visa_status('F', 'pp', datetime.now(), None)
    result = VisaStatus.find_latest_written_visa_status('F', 'pp')
    pprint(result)


def simple_test_subscription():
    """ Just a SIMPLE test"""
    from pprint import pprint  # SORRY

    Subscription.email.drop()

    email = 'benji@example.com'
    subs = [
        ('F', 'pp', datetime(2020, 9, 25)),
        ('F', 'sh', datetime(2020, 10, 15)),
        ('H', 'bj', datetime.max)
    ]
    Subscription.add_email_subscription(email, subs)
    pprint(Subscription.get_subscriptions_by_email(email))

    update_susbs = ('F', 'sh', datetime(2020, 11, 30))
    Subscription.add_email_subscription(email, update_susbs)
    pprint(Subscription.get_subscriptions_by_email(email))

    unsubs = ('F', 'sh')
    Subscription.remove_email_subscription(email, unsubs)
    pprint(Subscription.get_subscriptions_by_email(email))

    unsubs_all = [('F', 'pp'), ('F', 'sh'), ('H', 'bj')]
    Subscription.remove_email_subscription(email, unsubs_all)
    pprint(Subscription.get_subscriptions_by_email(email))

    Subscription.email.drop()
    emails = ['em0@example.com', 'em1@example.com']
    subses = [
        [('F', 'pp', datetime(2020, 10, 23)), ['H', 'pp', datetime.max]],
        [('F', 'pp', datetime(2020, 10, 26))],
    ]
    Subscription.add_email_subscription(emails[0], subses[0])
    Subscription.add_email_subscription(emails[1], subses[1])

    print('-' * 10)
    pprint(Subscription.get_email_list(('F', 'pp', datetime(2020, 10, 24))))
    print('-' * 10)
    pprint(Subscription.get_email_list(('F', 'pp', datetime(2020, 10, 24)), 'expired_only'))
    print('-' * 10)
    pprint(Subscription.get_email_list(('F', 'pp', datetime(2020, 10, 24)), 'effective_only'))


if __name__ == "__main__":
    # manual test
    simple_test_visa_status()
    # simple_test_subscription()
    pass
