""" A request function that grab all the data from current tuixue"""

import os
import requests
from datetime import datetime, timedelta

import util
import global_var as G

BASE_URL = 'https://tuixue.online'


def fetch_all(since: str = '2020/9/16'):
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
                res = requests.get(f'{BASE_URL}{endpoint}')

                with open(file_path, 'w') as f:
                    if res.status_code == 200:
                        f.write(res.text)
                    else:
                        f.write('')

                print('Written')

if __name__ == "__main__":
    fetch_all()
