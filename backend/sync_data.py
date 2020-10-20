""" A request function that grab all the data from current tuixue"""

import os
import requests
import argparse
from datetime import datetime, timedelta

import util
import pymongo
import global_var as G
import tuixue_mongodb as DB

BASE_URL = 'https://tuixue.online'


def fetch_all(since: str):
    """ Fetch global USEbassy data."""
    since_date = datetime.strptime(since, '%Y/%m/%d')
    date_span = datetime.today() - since_date  # - timedelta(days=1)
    date_range = [since_date + timedelta(days=d) for d in range(date_span.days)]

    embassy_lst = G.USEmbassy.get_embassy_lst()

    for embassy in embassy_lst:
        if embassy.country != 'CHN':
            path = '/global/crawler'
        else:
            path = '/visa2'

        for visa_type in G.VISA_TYPES:
            for date in date_range:
                dt_str = date.strftime('%Y/%m/%d')
                endpoint = f'{path}/{visa_type}/{embassy.location}/{dt_str}'
                file_path = util.construct_data_file_path(visa_type, embassy.location, dt_str)
                os.makedirs(os.path.join(*file_path.split('/')[:-1]), exist_ok=True)
                if os.path.exists(file_path):
                    print(f'Skipping fetching data: {visa_type}-{embassy.location}-{dt_str}')
                    continue  # skip if the file is already fetched.

                print(f'Fetching down data: {visa_type}-{embassy.location}-{dt_str}', end=' | ')
                res = requests.get(f'{BASE_URL}{endpoint}', timeout=60)

                with open(file_path, 'w') as f:
                    if res.status_code == 200:
                        f.write(res.text)
                    else:
                        f.write('')

                print('Written')


def initiate_database(since: str):
    """ Clear all the previous visa_status data.
        Write all file based data into MongoDB.
    """
    since_date = datetime.strptime(since, '%Y/%m/%d')
    date_span = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - since_date  # all mid-nights
    date_range = [since_date + timedelta(days=d) for d in range(date_span.days)]

    embassy_lst = G.USEmbassy.get_embassy_lst()

    DB.VisaStatus.drop()
    DB.VisaStatus.visa_status.create_index(  # this function help improving performance when executing queries.
        [
            ('available_dates.write_time', pymongo.ASCENDING),
            ('available_dates.available_date', pymongo.DESCENDING),
        ]
    )

    for vt in G.VISA_TYPES:
        for emb in embassy_lst:
            print()
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

                DB.VisaStatus.visa_status.insert_one(
                    {
                        'visa_type': vt,
                        'embassy_code': emb.code,
                        'write_date': date,
                        'available_dates': available_dates_arr
                    }
                )

                print(
                    f'Inserted: {vt}-{emb.location}-{date.year}/{date.month}/{date.day}\
                        \t\t{len(available_dates_arr)}\trecords',
                    end='\r'
                )


def infinite_fetch():
    """ Incase the connection drop or something..."""
    while True:
        try:
            fetch_all('2020/4/8')
        except requests.exceptions.ReadTimeout:
            continue
        else:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--operation', '-o',
        required=True,
        type=str,
        choices=['fetch', 'write'], help='Choose what function to run'
    )
    args = parser.parse_args()

    if args.operation == 'fetch':
        infinite_fetch()
    elif args.operation == 'write':
        initiate_database('2020/9/16')  # havn't fetched all data before 2020/9/16
