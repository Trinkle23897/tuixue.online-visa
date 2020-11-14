""" Classes for interaction with MongoDB NoSQL
    pymongo gurantees that the MongoClient is thread-safe
"""

import os
import pymongo
import util
from collections import defaultdict
from tuixue_typing import VisaType, EmbassyCode
from datetime import datetime, timedelta, timezone
from typing import Union, List, Tuple, Optional, Dict
from global_var import USEmbassy, VISA_TYPES, MONGO_CONFIG

EmailSubscription = NewVisaStatus = Tuple[VisaType, EmbassyCode, datetime]
EmailSubscriptionNoDate = NewVisaStatusNoDate = Tuple[VisaType, EmbassyCode]  # seeking for a better name...

MONGO_CLIENT = None


def connect() -> pymongo.database.Database:
    """ Connect to the local MongoDB server. Return a handle of tuixue database."""
    global MONGO_CLIENT
    if MONGO_CLIENT is None:  # keep one alive connection will be enough (and preferred)
        MONGO_CLIENT = pymongo.MongoClient(host=MONGO_CONFIG['host'], port=MONGO_CONFIG['port'])

    database = MONGO_CLIENT.get_database(MONGO_CONFIG['database'])
    return database


def get_collection(collection_name: str) -> pymongo.collection.Collection:
    """ Return a MongoDB collection from the established client database."""
    db = connect()
    return db.get_collection(collection_name)


class VisaStatus:
    """ MongoDB operations for storing:
        1. All fetched visa status by (visa_type, embassy_code), *only successful fetching*
        2. Overview of available appointment date of a given write date, *only successful fetching*
        3. Latest written time and data, *including failed one*

        The successfully fetched visa status will be stored in Mongo collection `'visa_status'`
        and the latest written time will be stored in Mongo collection `'latest_written'`.

        The schema of documents for `'visa_status'` is as follow:

        ```python
        {
            'visa_type': str,
            'embassy_code': str,
            'write_date': datetime,
            'available_dates': [
                {'write_time': datetime, 'available_date': datetime},
            ]
        }
        ```

        The schema of documents for `'overview'` is as follow:

        ```python
        {
            'visa_type': str,
            'embassy_code': str,
            'overview': [
                {'write_date': datetime, 'earliest_date': datetime, 'latest_date': datetime},
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
    overview = get_collection('overview')
    latest_written = get_collection('latest_written')

    @classmethod
    def initiate_collections_tz(cls, since: datetime) -> None:
        """ Initiate the database with following handling of datetime object regarding timezone.

            1. All of the `available_date` data are stored as is. (what we fetch is what we store)
            2. All of the `write_time` and `write_date` data in Mongo collections **`visa_status`**
                and **`latest_written`** are stored in UTC+0 standard time.
            3. **(Very important here)** All of the `write_time` and `write_date` data in Mongo
                collection **`overview`** are stored in the time in the local time zone of a given
                U.S. Embassy location. e.g. The overview data of U.S. Embassy in Phnom Pend on the
                date Oct 10th, 2020 stands for the time range `"2020-10-10T00:00+07:00"` to
                `"2020-10-10T23:59+07:00"`, **NOT** `"2020-10-10T00:00+00:00"` to `"2020-10-10T23:59+00:00"`.
            4. All time data in a HTTP request from frontend **must be** a UTC standard time. The
                `Date.toISOString` is the default way we construct the time related query in a request
                url in frontend. FastAPI backend should add a layer of logic that consolidate the received
                datetime object must have a `tzinfo` attribute otherwise should return a 422 status code.
        """
        since_midnight = since.replace(hour=0, minute=0, second=0, microsecond=0)
        today_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        date_range = [since_midnight + timedelta(days=d) for d in range((today_midnight - since_midnight).days + 1)]

        embassy_lst = USEmbassy.get_embassy_lst()

        cls.drop()
        cls.visa_status.create_index([('write_date', pymongo.ASCENDING)])

        for vt in VISA_TYPES:
            for emb in embassy_lst:
                print()  # Go to a new line (inner loop using end='\r')
                accumulated_inserted = 0
                for date in date_range:
                    file_path = util.construct_data_file_path(vt, emb.location, date.strftime('%Y/%m/%d'))
                    if not os.path.exists(file_path):
                        continue

                    with open(file_path) as f:
                        available_dates_arr = [
                            {'write_time': datetime.combine(date.date(), wt), 'available_date': avai_dt}
                            for wt, avai_dt in [util.file_line_to_dt(ln) for ln in f.readlines()]
                        ]

                    for i, adt in enumerate(available_dates_arr):
                        write_time_utc = adt['write_time'].astimezone(tz=None).astimezone(tz=timezone.utc)
                        write_date_utc = write_time_utc.replace(hour=0, minute=0, second=0, microsecond=0)
                        available_date = adt['available_date']

                        # Push the available date one by one because write_date_utc may be different
                        # MongoDB will convert the datetime obj with tzinfo attr to UTC time
                        cls.visa_status.update_one(
                            {'visa_type': vt, 'embassy_code': emb.code, 'write_date': write_date_utc},
                            {'$push': {'available_dates': available_date}},
                            upsert=True,
                        )

                        write_date_emb_local = write_time_utc\
                            .astimezone(emb.timezone)\
                            .replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
                        
                        query = {'visa_type': vt, 'embassy_code': emb.code}
                        overview_query = {**query, 'overview.write_date': write_date_emb_local}

                        if cls.overview.find_one(overview_query) is None:  # $(update) of array can't work with upsert
                            cls.overview.update_one(
                                query,
                                {
                                    '$push': {
                                        'overview': {
                                            'write_date': write_date_emb_local,
                                            'earliest_date': available_date,
                                            'latest_date': available_date,
                                        },
                                    },
                                },
                                upsert=True,
                            )

                        else:
                            cls.overview.update_one(
                                overview_query,
                                {
                                    '$min': {'overview.$.earliest_date': available_date},
                                    '$max': {'overview.$.latest_date': available_date}, 
                                }
                            )

                        accumulated_inserted += 1
                        print(
                            f'{vt}\t{emb.location}\t\t{date.year}/{date.month}/{date.day}\t{write_date_utc.year}/{write_date_utc.month}/{write_date_utc.day}\t{write_date_emb_local.year}/{write_date_emb_local.month}/{write_date_emb_local.day}\t{i + 1}/{len(available_dates_arr)}\t{accumulated_inserted}',
                            end='\r'
                        )

    @classmethod
    def initiate_collections(cls, since: datetime) -> None:
        """ Initiate the visa status storage with the file based data."""
        since_midnight = since.replace(hour=0, minute=0, second=0, microsecond=0)
        today_midnight = datetime.combine(datetime.now().date(), datetime.min.time())
        date_range = [since_midnight + timedelta(days=d) for d in range((today_midnight - since_midnight).days)]

        embassy_lst = USEmbassy.get_embassy_lst()

        cls.drop()
        cls.visa_status.create_index([('write_date', pymongo.ASCENDING)])

        for vt in VISA_TYPES:
            for emb in embassy_lst:
                print()
                accumulated_inserted = 0
                for date in date_range:
                    file_path = util.construct_data_file_path(vt, emb.location, date.strftime('%Y/%m/%d'))
                    if not os.path.exists(file_path):
                        continue

                    with open(file_path) as f:
                        fetched_result_lst = [util.file_line_to_dt(ln) for ln in f.readlines()]
                        available_dates_arr = [
                            {'write_time': datetime.combine(date.date(), wt), 'available_date': avai_dt}
                            for wt, avai_dt in fetched_result_lst
                        ]

                    cls.visa_status.insert_one(
                        {
                            'visa_type': vt,
                            'embassy_code': emb.code,
                            'write_date': date,
                            'available_dates': available_dates_arr
                        }
                    )

                    if len(available_dates_arr) > 0:
                        earliest_dt = min([d['available_date'] for d in available_dates_arr])
                        latest_dt = max([d['available_date'] for d in available_dates_arr])
                        cls.overview.update_one(
                            {'visa_type': vt, 'embassy_code': emb.code},
                            {
                                '$push': {
                                    'overview': {
                                        'write_date': date,
                                        'earliest_date': earliest_dt,
                                        'latest_date': latest_dt,
                                    }
                                }
                            },
                            upsert=True,
                        )

                    accumulated_inserted += len(available_dates_arr)
                    print(
                        f'Inserted: {vt}-{emb.location}-{date.year}/{date.month}/{date.day}\
                            \t\t{len(available_dates_arr)}\trecords |\t{accumulated_inserted} in total',
                        end='\r'
                    )

    @classmethod
    def drop(cls, collection: str = 'all') -> None:
        """ THSI METHOD SHOULD BE USED WITH CAUTION (OR DELETED) IN PRODUCTION."""
        if collection not in ('visa_status', 'latest_written', 'overview', 'all'):
            raise ValueError(
                f'collection can only be one of [\'visa_status\', \'latest_written\', \'overview\', \'all\'],\
                    get {collection}'
            )

        if collection in ('visa_status', 'all'):
            cls.visa_status.drop()
        if collection in ('latest_written', 'all'):
            cls.latest_written.drop()
        if collection in ('overview', 'all'):
            cls.overview.drop()

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
        embassy = USEmbassy.get_embassy_by_code(embassy_code)
        write_time_utc = write_time.astimezone(tz=None).astimezone(tz=timezone.utc)
        write_date_utc = write_time_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        write_date_emb_local = write_date_utc.astimezone(embassy.timezone).replace(tzinfo=None)

        query = {'visa_type': visa_type, 'embassy_code': embassy_code}
        visa_status_query = {**query, 'write_date': write_date_utc}
        overview_query = {**query, 'overview.write_date': write_date_emb_local}

        new_fetch = {'write_time': write_time_utc, 'available_date': available_date}

        # udpate document if exists, otherwise insert a new document
        cls.latest_written.update_one(query, {'$set': new_fetch}, upsert=True)

        if available_date is not None:
            cls.visa_status.update_one(visa_status_query, {'$push': {'available_dates': new_fetch}}, upsert=True)

            if cls.overview.find_one(overview_query) is None:  # $(update) of array can't work with upsert
                cls.overview.update_one(
                    query,
                    {
                        '$push': {
                            'overview': {
                                'write_date': write_date_emb_local,
                                'earliest_date': available_date,
                                'latest_date': available_date
                            }
                        }
                    },
                    upsert=True
                )
            else:
                cls.overview.update_one(
                    overview_query,
                    {
                        '$min': {'overview.$.earliest_date': available_date},
                        '$max': {'overview.$.latest_date': available_date},
                    }
                )

    @classmethod
    def find_visa_status_overview(
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
                    'overview': [
                        {
                            'visa_type': VisaType,
                            'embassy_code': EmbassyCode,
                            'earliest_date': datetime,
                            'latest_date': datetime
                        },
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

        cursor = cls.overview.aggregate([
            {'$match': {'visa_type': {'$in': visa_type}, 'embassy_code': {'$in': embassy_code}}},
            {
                '$project': {
                    'visa_type': '$visa_type',
                    'embassy_code': '$embassy_code',
                    'overview': {
                        '$filter': {
                            'input': '$overview',
                            'as': 'ov',
                            'cond': {'$in': ['$$ov.write_date', date]}
                        }
                    }
                }
            },
            {'$unwind': '$overview'},
            {
                '$group': {
                    '_id': '$overview.write_date',
                    'date': {'$first': '$overview.write_date'},
                    'overview': {
                        '$push': {
                            'visa_type': '$visa_type',
                            'embassy_code': '$embassy_code',
                            'earliest_date': '$overview.earliest_date',
                            'latest_date': '$overview.latest_date',
                        }
                    }
                }
            },
            {'$project': {'_id': False}},
            {'$sort': {'date': pymongo.DESCENDING}},  # today first
        ])

        return list(cursor)  # tabular data on the fly

    @classmethod
    def find_latest_written_visa_status(
        cls,
        visa_type: Union[VisaType, List[VisaType]],
        embassy_code: Union[EmbassyCode, List[EmbassyCode]],
    ) -> List[dict]:
        """ Find the latest written visa status of a given visa_type and embassy_code"""
        if not isinstance(visa_type, list):
            visa_type = [visa_type]
        if not isinstance(embassy_code, list):
            embassy_code = [embassy_code]

        cursor = cls.latest_written.aggregate([
            {'$match': {'visa_type': {'$in': visa_type}, 'embassy_code': {'$in': embassy_code}}},
            {'$project': {'_id': False}}
        ])

        return list(cursor)

    @classmethod
    def find_visa_status_past24h(
        cls,
        visa_type: VisaType,
        embassy_code: EmbassyCode,
        timestamp: datetime,
    ) -> Optional[dict]:
        """ Return historical data of a given `visa_type`-`embassy_cde` pair for the past 24 hours"""
        ts_start, ts_end = timestamp - timedelta(days=1), timestamp

        today = datetime.combine(timestamp.date(), datetime.min.time())
        yesterday = today - timedelta(days=1)
        dates = list({today, yesterday})

        cursor = cls.visa_status.aggregate([
            {'$match': {'visa_type': visa_type, 'embassy_code': embassy_code, 'write_date': {'$in': dates}}},
            {'$unwind': '$available_dates'},
            {'$sort': {'available_dates.write_time': pymongo.ASCENDING}},
            {
                '$group': {
                    '_id': None,
                    'visa_type': {'$first': '$visa_type'},
                    'embassy_code': {'$first': '$embassy_code'},
                    'available_dates': {
                        '$push': {
                            '$cond': [
                                {
                                    '$and': [
                                        {'$gte': ['$available_dates.write_time', ts_start]},
                                        {'$lte': ['$available_dates.write_time', ts_end]},
                                    ],
                                },
                                {
                                    'write_time': '$available_dates.write_time',
                                    'available_date': '$available_dates.available_date',
                                },
                                None
                            ]
                        },
                    },
                }
            },
            {'$project': {
                '_id': False,
                'visa_type': '$visa_type',
                'embassy_code': '$embassy_code',
                'time_range': [ts_start, ts_end],
                'available_dates': {'$setDifference': ['$available_dates', [None]]},
            }}
        ])

        result = list(cursor)
        if len(result) > 0:
            return result[0]
        else:
            return None

    @classmethod
    def find_historical_visa_status(
        cls,
        visa_type: VisaType,
        embassy_code: EmbassyCode,
        write_date: datetime,
    ) -> Optional[dict]:
        """ Return historical data of a given `visa_type`-`embassy_cde` pair.
            If we sort the available dates in the guranularity of minutes, it will be too heavy a
            work load for backend servers, so sort by date and leave the other work to front end.
        """
        cursor = cls.visa_status.aggregate([
            {'$match': {'visa_type': visa_type, 'embassy_code': embassy_code, 'write_date': write_date}},
            {'$unwind': '$available_dates'},
            {'$sort': {'available_dates.write_time': pymongo.ASCENDING}},
            {
                '$group': {
                    '_id': None,
                    'visa_type': {'$first': '$visa_type'},
                    'embassy_code': {'$first': '$embassy_code'},
                    'write_date': {'$first': '$write_date'},
                    'available_dates': {
                        '$push': {
                            'write_time': '$available_dates.write_time',
                            'available_date': '$available_dates.available_date',
                        },
                    },
                }
            },
            {'$project': {'_id': False}}
        ], allowDiskUse=True)

        result = list(cursor)
        if len(result) > 0:
            return result[0]
        else:
            return None


class Subscription:
    """ MongoDB operations for storing:
        1. Email subscription - a one-to-few relationship. Comparing to the previous JSON
            based TuixueDB, the difference is that to represent 'subscribe with no end date'
            we use the `datetime.max` instead of a special string. It helps to simplify the
            logic here as suggested by @n+e.

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

        return cls.email.find_one({'email': email}, projection={'_id': False})

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
                random.shuffle(write_time_by_min)
                for write_time in write_time_by_min:
                    VisaStatus.save_fetched_visa_status(
                        visa_type,
                        embassy_code,
                        write_time,
                        random.choice(available_dts)
                    )

    result = VisaStatus.find_historical_visa_status('F', 'pp', datetime(2020, 9, 25), datetime(2020, 9, 26))
    pprint(result)

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

    email = 'benjamincaiyh+tuixuetest@gmail.com'
    subs = [
        ('F', 'pp', datetime.max),
        ('O', 'beg', datetime.max),
        ('H', 'lcy', datetime.max),
        ('B', 'sel', datetime.max)
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
    # simple_test_visa_status()
    simple_test_subscription()
    pass
