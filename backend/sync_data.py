""" A request function that grab all the data from current tuixue"""

import os
import requests
import argparse
from datetime import datetime, timedelta

import util
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
    DB.VisaStatus.initiate_collections(since_date)


def infinite_fetch(since: str):
    """ Incase the connection drop or something..."""
    while True:
        try:
            fetch_all(since)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
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
    parser.add_argument(
        '--since', '-s',
        type=str,
        default='2020/4/8',
        help='Date string indicating the start date of fetching data'
    )
    args = parser.parse_args()

    try:
        datetime.strptime(args.since, '%Y/%m/%d')
    except ValueError:
        print(f'Illegal argument given to \'since\': {args.since}, required a YYYY/MM/DD format string')
        exit(1)

    if args.operation == 'fetch':
        infinite_fetch(args.since)
    elif args.operation == 'write':
        initiate_database(args.since)  # havn't fetched all data before 2020/9/16
