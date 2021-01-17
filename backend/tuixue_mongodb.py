""" Classes for interaction with MongoDB NoSQL
    pymongo gurantees that the MongoClient is thread-safe
"""

import os
import util
import pymongo
from collections import defaultdict
from tuixue_typing import VisaType, EmbassyCode
from datetime import datetime, timedelta, timezone
from typing import Union, List, Tuple, Optional, Dict
from global_var import USEmbassy, VISA_TYPES, MONGO_CONFIG
from global_var import AIS_FETCH_TIME_INTERVAL, CGI_FETCH_TIME_INTERVAL
from pymongo import database, collection
from util import dt_to_utc

EmailSubscription = NewVisaStatus = Tuple[VisaType, EmbassyCode, datetime]
EmailSubscriptionNoDate = NewVisaStatusNoDate = Tuple[VisaType, EmbassyCode]  # seeking for a better name...

MONGO_CLIENT = None


def connect() -> database.Database:
    """ Connect to the local MongoDB server. Return a handle of tuixue database."""
    global MONGO_CLIENT
    if MONGO_CLIENT is None:  # keep one alive connection will be enough (and preferred)
        MONGO_CLIENT = pymongo.MongoClient(host=MONGO_CONFIG['host'], port=MONGO_CONFIG['port'])

    database = MONGO_CLIENT.get_database(MONGO_CONFIG['database'])
    return database


def get_collection(collection_name: str) -> collection.Collection:
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
    def restore_overview(cls) -> None:
        """ This method should only be used when `mongorestore` is executed and the
            `tuixue.visa_status` collection is restored.
        """
        cls.drop('overview')
        embassy_lst = USEmbassy.get_embassy_lst()

        for visa_type in VISA_TYPES:
            for emb in embassy_lst:
                print()
                avai_dt_cache = defaultdict(list)

                all_avai_dt = cls.visa_status.aggregate([
                    {'$match': {'visa_type': visa_type, 'embassy_code': emb.code}},
                    {'$unwind': '$available_dates'},
                    {
                        '$project': {
                            '_id': False,
                            'write_time': '$available_dates.write_time',
                            'available_date': '$available_dates.available_date'
                        }
                    },
                ])

                for adt in all_avai_dt:
                    write_time_utc = adt['write_time']
                    available_date = adt['available_date']

                    write_time_emb = write_time_utc.astimezone(emb.timezone)
                    write_date_emb = write_time_emb.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

                    avai_dt_cache[write_date_emb].append(available_date)

                for write_date, avai_dt_arr in avai_dt_cache.items():
                    if len(avai_dt_arr) > 0:
                        earliest_dt, latest_dt = min(avai_dt_arr), max(avai_dt_arr)
                        cls.overview.update_one(
                            {'visa_type': visa_type, 'embassy_code': emb.code},
                            {
                                '$push': {
                                    'overview': {
                                        'write_date': write_date,
                                        'earliest_date': earliest_dt,
                                        'latest_date': latest_dt,
                                    }
                                }
                            },
                            upsert=True,
                        )
                        print(
                            'Update tuixue.overview: {}\t{}\t\t\t{}'.format(
                                visa_type,
                                emb.location,
                                write_date.strftime('%Y/%m/%d')
                            ),
                            end='\r'
                        )

    @classmethod
    def initiate_latest_written_parallel(cls, sys: str) -> None:
        """ write an empty latest_written record for every embassy and visa type.

            this method pick the latest `write_date` for a `(visa_type, embassy_code)` pair, then get
            the last written record from `available_dates` array of it. And overwrite the whole
            `last_written` collection.
        """
        embassy_code_lst = [emb.code for emb in USEmbassy.get_embassy_lst() if emb.sys == sys]
        query_param = list(cls.visa_status.aggregate([
            {
                '$group': {
                    '_id': {'visa_type': '$visa_type', 'embassy_code': '$embassy_code'},
                    'write_date': {'$max': '$write_date'},
                },
            },
            {'$replaceRoot': {'newRoot': {'$mergeObjects': ['$_id', {'write_date': '$write_date'}]}}},
        ]))

        query_param = [query for query in query_param if query['embassy_code'] in embassy_code_lst]

        last_effective_write = cls.visa_status.aggregate([
            {'$facet': {'{}{}'.format(q['visa_type'], q['embassy_code']): [
                {'$match': q},
                {
                    '$project': {
                        '_id': False,
                        'visa_type': True,
                        'embassy_code': True,
                        'available_date': {'$slice': ['$available_dates.available_date', -1]},
                    },
                },
                {'$unwind': '$available_date'},
            ] for q in query_param}},
            {
                '$project': {
                    'facet_result': {
                        '$setUnion': ['${}{}'.format(q['visa_type'], q['embassy_code']) for q in query_param],
                    },
                },
            },
            {'$unwind': '$facet_result'},
            {'$replaceRoot': {'newRoot': '$facet_result'}},
            {'$set': {'write_time': datetime.now(timezone.utc)}},
        ], allowDiskUse=True)

        cls.latest_written.drop()
        cls.latest_written.insert_many(list(last_effective_write))

    @classmethod
    def initiate_latest_written_sequential(cls, sys: str, backtrack_hr: int = 12) -> None:
        """ Initate latest_written in sequentail order."""
        embassy_code_lst = [emb.code for emb in USEmbassy.get_embassy_lst() if emb.sys == sys]

        now = datetime.now()
        start = datetime.combine((now - timedelta(hours=backtrack_hr)).date(), datetime.min.time())
        end = datetime.combine(now.date(), datetime.min.time())
        dates = [start + timedelta(days=d) for d in range((end - start).days + 1)]

        query_param = cls.visa_status.aggregate([
            {'$match': {'write_date': {'$in': dates}}},
            {
                '$group': {
                    '_id': {'visa_type': '$visa_type', 'embassy_code': '$embassy_code'},
                    'write_date': {'$max': '$write_date'},
                },
            },
            {'$replaceRoot': {'newRoot': {'$mergeObjects': ['$_id', {'write_date': '$write_date'}]}}},
        ], allowDiskUse=True)

        for query in query_param:
            if query['embassy_code'] not in embassy_code_lst:
                continue

            cursor = cls.visa_status.aggregate([
                {'$match': query},
                {
                    '$project': {
                        '_id': False,
                        'write_time': datetime.now(timezone.utc),
                        'available_date': {'$slice': ['$available_dates.available_date', -1]},
                    },
                },
                {'$unwind': '$available_date'},
            ], allowDiskUse=True)

            query.pop('write_date')
            for last_effective_fetch in cursor:
                cls.latest_written.update_one(query, {'$set': last_effective_fetch}, upsert=True)

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

                avai_dt_cache_utc = defaultdict(list)
                avai_dt_cache_emb = defaultdict(list)

                for date in date_range:
                    file_path = util.construct_data_file_path(vt, emb.location, date.strftime('%Y/%m/%d'))
                    if not os.path.exists(file_path):
                        continue

                    with open(file_path) as f:
                        available_dates_arr = [
                            {'write_time': datetime.combine(date.date(), wt), 'available_date': avai_dt}
                            for wt, avai_dt in [util.file_line_to_dt(ln) for ln in f.readlines()]
                        ]

                    for adt in available_dates_arr:
                        write_time_utc = adt['write_time'].astimezone(tz=None).astimezone(tz=timezone.utc)

                        write_date_utc = write_time_utc.replace(hour=0, minute=0, second=0, microsecond=0)
                        write_date_emb = write_time_utc\
                            .astimezone(emb.timezone)\
                            .replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

                        available_date = adt['available_date']
                        avai_dt_cache_utc[write_date_utc].append(
                            {'write_time': write_time_utc, 'available_date': available_date}
                        )
                        avai_dt_cache_emb[write_date_emb].append(available_date)

                        print(' ' * 150, end='\r')  # erase previous print
                        print('Reading: {}-{}-{}'.format(vt, emb.location, date.strftime('%Y/%m/%d')), end='\t\t')
                        print(
                            'UTC\t{}: {}'.format(
                                write_date_utc.strftime('%Y/%m/%d'),
                                len(avai_dt_cache_utc[write_date_utc])
                            ),
                            end='\t'
                        )
                        print(
                            'EMB\t{}: {}'.format(
                                write_date_emb.strftime('%Y/%m/%d'),
                                len(avai_dt_cache_emb[write_date_emb])
                            ),
                            end='\t'
                        )
                        print(
                            '|Total:\tUTC-{}\tEMB-{}'.format(
                                sum([len(cache_len) for cache_len in avai_dt_cache_emb.values()]),
                                sum([len(cache_len) for cache_len in avai_dt_cache_emb.values()]),
                            ),
                            end='\r'
                        )

                if len(avai_dt_cache_utc) > 0:
                    cls.visa_status.insert_many([  # insert all visa status fetch result in one write
                        {
                            'visa_type': vt,
                            'embassy_code': emb.code,
                            'write_date': write_date,
                            'available_dates': avai_dt_arr,
                        } for write_date, avai_dt_arr in avai_dt_cache_utc.items()
                    ])
                else:
                    print('Skipping: {}-{} No records'.format(vt, emb.location), end='\r')

                for write_date, avai_dt_arr in avai_dt_cache_emb.items():
                    if len(avai_dt_arr) > 0:
                        earliest_dt, latest_dt = min(avai_dt_arr), max(avai_dt_arr)
                        cls.overview.update_one(
                            {'visa_type': vt, 'embassy_code': emb.code},
                            {
                                '$push': {
                                    'overview': {
                                        'write_date': write_date,
                                        'earliest_date': earliest_dt,
                                        'latest_date': latest_dt,
                                    }
                                }
                            },
                            upsert=True,
                        )

    @classmethod
    def initiate_collections(cls, since: datetime) -> None:
        """ Initiate the visa status storage with the file based data."""
        since_midnight = since.replace(hour=0, minute=0, second=0, microsecond=0)
        today_midnight = datetime.combine(datetime.now().date(), datetime.min.time())
        date_range = [since_midnight + timedelta(days=d) for d in range((today_midnight - since_midnight).days + 1)]

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
        write_date_emb = write_time_utc.astimezone(embassy.timezone)\
            .replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

        query = {'visa_type': visa_type, 'embassy_code': embassy_code}
        visa_status_query = {**query, 'write_date': write_date_utc}
        overview_query = {**query, 'overview.write_date': write_date_emb}

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
                                'write_date': write_date_emb,
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
    def find_visa_status_overview_embtz(
        cls,
        visa_type: Union[VisaType, List[VisaType]],
        embassy_code: Union[EmbassyCode, List[EmbassyCode]],
        since_utc: datetime,
        to_utc: datetime,
    ):
        """ This method fix the problem of `cls.find_visa_status_overview` as the previous method doesn't
            convert the querying date into the embassy timezone.
        """

        def dt_to_date(dt: datetime) -> datetime:
            return dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

        def utc_to_embtz(dt: datetime, embtz: timezone) -> datetime:
            return dt_to_date(dt.astimezone(embtz))

        def single_target_query(visa_type: str, embassy_code: str, date_range: List[datetime]) -> List[dict]:
            """ construct the sub-pipeline for mongodb aggregation `facet` stage."""
            return [
                {'$match': {'visa_type': visa_type, 'embassy_code': embassy_code}},
                {
                    '$project': {
                        'visa_type': '$visa_type',
                        'embassy_code': '$embassy_code',
                        'overview': {
                            '$filter': {
                                'input': '$overview',
                                'as': 'ov',
                                'cond': {'$in': ['$$ov.write_date', date_range]}
                            }
                        }
                    }
                },
                {'$unwind': '$overview'},
                {
                    '$project': {
                        '_id': False,
                        'visa_type': '$visa_type',
                        'embassy_code': '$embassy_code',
                        'write_date': '$overview.write_date',
                        'earliest_date': '$overview.earliest_date',
                        'latest_date': '$overview.latest_date',
                    }
                },
            ]

        if not isinstance(visa_type, list):
            visa_type = [visa_type]
        if not isinstance(embassy_code, list):
            embassy_code = [embassy_code]

        overview_target = [
            {
                'visa_type': vt,
                'embassy_code': emb.code,
                'date_range': [
                    utc_to_embtz(since_utc, emb.timezone) + timedelta(days=d)
                    for d in range(
                        (utc_to_embtz(to_utc, emb.timezone) - utc_to_embtz(since_utc, emb.timezone)).days + 1
                    )
                ],
            } for vt in visa_type for emb in [USEmbassy.get_embassy_by_code(ec) for ec in embassy_code]
        ]

        utc_date_range = [
            dt_to_date(since_utc) + timedelta(days=d)
            for d in range((dt_to_date(to_utc) - dt_to_date(since_utc)).days + 1)
        ]

        embtz_utc_map = {tgt['embassy_code']: dict(zip(tgt['date_range'], utc_date_range)) for tgt in overview_target}

        query = [
            {
                '$facet': {
                    '{}{}'.format(tgt['visa_type'], tgt['embassy_code']): single_target_query(**tgt)
                    for tgt in overview_target
                },
            },
            {
                '$project': {
                    'facet_result': {
                        '$setUnion': ['${}{}'.format(tgt['visa_type'], tgt['embassy_code']) for tgt in overview_target]
                    }
                },
            },
            {'$unwind': '$facet_result'},
            {'$replaceRoot': {'newRoot': '$facet_result'}}
        ]
        overview_embtz = list(cls.overview.aggregate(query))
        overview_utc = [{
            **ov,
            'write_date': embtz_utc_map[ov['embassy_code']][ov['write_date']],
        } for ov in overview_embtz]

        ov_groupby_date = defaultdict(list)
        for overview in overview_utc:
            write_date = overview.pop('write_date')
            ov_groupby_date[write_date].append(overview)

        return sorted(
            [{'date': write_date, 'overview': overview} for write_date, overview in ov_groupby_date.items()],
            key=lambda ov: ov['date'],
            reverse=True,
        )

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

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999)

        cursor = cls.latest_written.aggregate([
            {
                '$match': {
                    'visa_type': {'$in': visa_type},
                    'embassy_code': {'$in': embassy_code},
                    'write_time': {'$gte': today_start, '$lte': today_end},
                }
            },
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
            {
                '$group': {
                    '_id': {'$dateToString': {'format': '%Y-%m-%dT%H:%M', 'date': '$available_dates.write_time'}},
                    'visa_type': {'$first': '$visa_type'},
                    'embassy_code': {'$first': '$embassy_code'},
                    'write_time': {'$first': '$available_dates.write_time'},
                    'available_date': {'$min': '$available_dates.available_date'}
                }
            },
            {'$sort': {'write_time': pymongo.ASCENDING}},
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
                                        {'$gte': ['$write_time', ts_start]},
                                        {'$lte': ['$write_time', ts_end]},
                                    ],
                                },
                                {
                                    'write_time': '$write_time',
                                    'available_date': '$available_date',
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
        ], allowDiskUse=True)

        result = list(cursor)
        if len(result) > 0:
            return result[0]
        else:
            return None

    @classmethod
    def find_visa_status_past24h_turning_point(
        cls,
        visa_type: VisaType,
        embassy_code: EmbassyCode,
        timestamp: datetime,
    ):
        """ Fill in the missing minute and return the visa status detail with consecutive duplicate removed"""
        visa_status = cls.find_visa_status_past24h(visa_type, embassy_code, timestamp)
        if visa_status is None or len(visa_status['available_dates']) == 0:
            return
        embassy = USEmbassy.get_embassy_by_code(embassy_code)
        interval = CGI_FETCH_TIME_INTERVAL[visa_type] if embassy.sys == 'cgi' else AIS_FETCH_TIME_INTERVAL[visa_type]
        interval = (interval + 60) * 1000  # add 1min tolerance

        def convert(dt: datetime):
            return dt_to_utc(dt, remove_second=True)

        available_dates = [{
            'write_time': convert(i['write_time']),
            'available_date': i['available_date'],
        } for i in visa_status['available_dates']]
        ts_start, ts_end = list(map(convert, visa_status['time_range']))
        purified_available_dates = []

        first_dp = available_dates[0]
        if first_dp['write_time'] - ts_start > 1:
            purified_available_dates = [{'write_time': ts_start, 'available_date': None}]

        for i, (prev_dp, next_dp) in enumerate(zip(available_dates[:-1], available_dates[1:])):
            if i == 0:
                purified_available_dates.append(prev_dp)
            if next_dp['write_time'] - prev_dp['write_time'] <= interval:
                if prev_dp['available_date'] == next_dp['available_date']:
                    continue
                else:
                    purified_available_dates.append(next_dp)
            else:
                purified_available_dates.append({'write_time': prev_dp['write_time'] + 60000, 'available_date': None})
                purified_available_dates.append(next_dp)

        last_dp = available_dates[-1]
        if ts_end - last_dp['write_time'] > interval:
            purified_available_dates.append({'write_time': last_dp['write_time'] + 60000, 'available_date': None})

        return {
            **visa_status,
            'time_range': [ts_start, ts_end],
            'available_dates': purified_available_dates,
        }

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
    def get_subscriptions_by_email(cls, email: str) -> dict:
        """ Get all subscription of a given email"""
        cursor = cls.email.aggregate([
            {'$match': {'email': email}},
            {'$unwind': '$subscription'},
            {'$set': {'subscription.expired': {'$lt': ['$subscription.till', datetime.now()]}}},
            {
                '$group': {
                    '_id': None,
                    'email': {'$first': '$email'},
                    'subscription': {'$push': '$subscription'},
                },
            },
            {'$project': {'_id': False}},
        ])

        for result in cursor:
            return result
        else:
            return {'email': email, 'subscription': []}

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
    def initiate_email(cls, path: str) -> None:
        """ Initialize the database with old version of email records."""
        cls.email.drop()
        all_users_dir = os.path.join(path, 'tmp')
        visa_type_list = [v for v in os.listdir(path) if len(v) == 1]
        user_choice = defaultdict(list)
        for visa_type in visa_type_list:
            city_list = os.listdir(os.path.join(path, visa_type))
            for city in city_list:
                # get the user list under visa_type + code
                user_list = os.listdir(os.path.join(path, visa_type, city))
                for user in user_list:
                    user_choice[user].append((visa_type.upper(), city))
        # at this time, the user_choice has the format
        # { email: [visa_type, embassy_code]}
        for email in user_choice:
            # read `till` under /tmp/{email}
            with open(os.path.join(path, 'tmp', email)) as f:
                dt = f.read().strip()
            if len(dt) == 0:  # FOREVER
                till = datetime.max
            else:
                try:
                    till = datetime.strptime(dt, '%Y/%m/%d')
                except:
                    till = datetime.strptime(dt, '%m/%d/%Y')
            subscription = []
            for (visa_type, embassy_code) in user_choice[email]:
                subscription.append({
                    "visa_type": visa_type,
                    "embassy_code": embassy_code,
                    "till": till,
                })
            if till > datetime.now() and len(subscription) > 0:
                cls.email.update_one({'email': email}, {'$set': {'subscription': subscription}}, upsert=True)

    @classmethod
    def add_email_subscription(
        cls,
        email: str,
        subscription: Union[EmailSubscription, List[EmailSubscription]],
    ) -> dict:
        """ Add one or more email subscription, create the subscriber document if
            one doesn't exist. And overwrite previous subscription record if there
            is a same email subscription exists.

            Return the subscriber after subscipriton edition.
        """
        if not isinstance(subscription, list):
            subscription = [subscription]

        new_subscription = [
            {'visa_type': visa_type, 'embassy_code': embassy_code, 'till': till}
            for visa_type, embassy_code, till in subscription
        ]

        cls.email.update_one({'email': email}, {'$set': {'subscription': new_subscription}}, upsert=True)

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

        current_subscription = list(cls.email.aggregate([
            {'$match': {'email': email}},
            {'$unwind': '$subscription'},
            {'$replaceRoot': {'newRoot': '$subscription'}},
        ]))

        updated_subscription = [
            subs for subs in current_subscription
            if (subs['visa_type'], subs['embassy_code']) not in unsubscription
        ]
        if len(updated_subscription) > 0:
            cls.email.update_one({'email': email}, {'$set': {'subscription': updated_subscription}})
        else:
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
    # simple_test_subscription()
    from pprint import pprint
    cursor = Subscription.email.aggregate([
        {'$match': {'email': 'baiyh+tuixue@gmail.com'}},
        {'$unwind': '$subscription'},
        {'$replaceRoot': {'newRoot': '$subscription'}}
    ])
    pprint(list(cursor))
    pass
