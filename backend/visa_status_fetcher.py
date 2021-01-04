""" Fetch the latest available U.S. Visa interveiw spots from Visa crawler server.
    An equvilant functionality to ../global/lite_visa.py
"""

import os
import json
import time
import argparse
import traceback
import threading
from typing import List
from queue import Queue
from datetime import datetime

import requests

import util
import global_var as G
import tuixue_mongodb as DB
from notifier import Notifier
from session_operation import Session, SessionCache


def init():
    """ Program entry, a simple command line interface"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', required=True, type=str, choices=['ais', 'cgi'], help='targeting system')
    parser.add_argument('--proxy', type=int, help='local proxy port')
    parser.add_argument('--crawler', type=str, default='crawler.txt', help='crawler api list')
    parser.add_argument('--ais', type=str, default='ais.json', help='ais account in json format')
    parser.add_argument('--log_dir', type=str, default=os.path.join(os.curdir, 'logs'), help='directory to save logs')
    parser.add_argument('--log_name', type=str, default='visa_fetcher', help='name of log file')
    parser.add_argument('--debug', action='store_true', default=False, help='log debug information')
    parser.add_argument(
        '--noinit_lw',
        action='store_true',
        default=False,
        help='whether not to initiate the latest_written'
    )
    args = parser.parse_args()

    if not os.path.exists(args.log_dir):
        os.mkdir(args.log_dir)

    G.assign('target_system', args.target)
    G.assign('session_file', f'{args.target}-session.json')
    G.assign('crawler_path', args.crawler)
    G.assign(
        'proxies',
        {
            'http': f'socks5h://127.0.0.1:{args.proxy}',
            'https': f'socks5h://127.0.0.1:{args.proxy}',
        } if args.proxy is not None else None
    )
    G.assign('log_dir', args.log_dir)
    G.assign('log_name', f'{args.target}_{args.log_name}')

    if args.target.lower() == 'ais':
        with open(args.ais) as f:
            ais_accounts = json.load(f)
            for k, v in ais_accounts.items():
                G.assign(k, v)

    if not args.noinit_lw:
        DB.VisaStatus.initiate_latest_written_sequential(args.target)

    global LOGGER
    global SESSION_CACHE
    LOGGER = util.init_logger(f'{args.target}_{args.log_name}', args.log_dir, args.debug)
    SESSION_CACHE = SessionCache()

    LOGGER.info('FETCHING TARGET: %s', args.target.upper())


def set_fetching_interval(
    visa_type: str,
    location: str,
    sys: str,
    interval_sec: int,
    first_run: bool = True
):
    """ Execute the fetching function every `interval` seconds
        https://stackoverflow.com/questions/2697039/python-equivalent-of-setinterval
    """
    def function_wrapper():
        set_fetching_interval(visa_type, location, sys, interval_sec, first_run=False)
        VisaFetcher.fetch_visa_status(
            visa_type,
            location,
            G.value(f'{visa_type}_requests_Session', requests.Session())
        )

    emb = G.USEmbassy.get_embassy_by_loc(location)
    now_minute = datetime.now().minute
    if sys == 'cgi' and visa_type == 'F' and 47 <= now_minute <= 49 and emb.region == 'DOMESTIC':
        interval = 5
    else:
        interval = interval_sec

    fetching_thread = threading.Timer(interval, function_wrapper)
    fetching_thread.start()

    if first_run:  # execute fecthing without waiting for the first time.
        VisaFetcher.fetch_visa_status(
            visa_type,
            location,
            G.value(f'{visa_type}_requests_Session', requests.Session())
        )
    return fetching_thread


def start_threads():
    """ Start the threads for fetching data from crawler server."""
    LOGGER.info('Setting up crawler node...')
    VisaFetcher.check_crawler_server_connection()

    LOGGER.info('Starting threads...')
    LOGGER.info('Setting up session update consumer...')
    session_update_consumer = threading.Thread(target=VisaFetcher.consume_new_session_request)
    session_update_consumer.start()

    LOGGER.info('Setting interval for fetching visa status...')
    sys = G.value('target_system', None)
    thread_pool = []
    for visa_type, interval_sec in G.FETCH_TIME_INTERVAL[sys].items():
        for location in G.SYS_LOCATION[sys]:
            thread_pool.append(set_fetching_interval(visa_type, location, sys, interval_sec))
    LOGGER.info('Fetching threads start, %s threads in total', len(thread_pool))

    for thread in thread_pool:
        thread.join()


def change_crawler_server():
    """ Manuanly check and update crawler server every 10 mintues."""
    while True:
        time.sleep(600)
        VisaFetcher.check_crawler_server_connection()


class VisaFetcher:
    """ A bundle of network requests and util functions."""
    @staticmethod
    def save_fetched_data(visa_type: str, location: str, available_visa_date: List[int]):
        """ Write the visa status to the end of the file."""
        logging_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        year, month, day = available_visa_date
        available_date = None if year == month == day == 0 else datetime(year, month, day)
        embassy = G.USEmbassy.get_embassy_by_loc(location)

        # decide if a notification should be send BEFORE writing the new data into file
        sent_notification = Notifier.notify_visa_status_change(visa_type, embassy, available_date)
        if sent_notification:
            LOGGER.info(
                'Sent notification for %s - %s-%s %s',
                logging_time,
                visa_type,
                location,
                available_date
            )

        try:
            LOGGER.debug(
                'WRITING TO DATABASE %s - %s-%s %s',
                logging_time,
                visa_type,
                location,
                available_date
            )
            writting_start = datetime.now()
            DB.VisaStatus.save_fetched_visa_status(
                visa_type=visa_type,
                embassy_code=embassy.code,
                write_time=datetime.now(),
                available_date=available_date
            )
            writting_finish = datetime.now()
        except Exception:
            LOGGER.error('Catch an error when saveing fetched result to database', traceback.format_exc())
        else:
            LOGGER.debug(
                'WRITE TO DATABASE SUCCESS %s - %s-%s %s',
                logging_time,
                visa_type,
                location,
                available_date
            )
            LOGGER.debug('WRITTING TAKES %f seconds', (writting_finish - writting_start).total_seconds())

    @staticmethod
    def check_crawler_server_connection():
        """ Check the connection of all the crawler server.
            Update the current crawler server in use.
        """
        if G.value('checking_crawler_connection', False):
            return
        previous_crawler_node = G.value('current_crawler_node', '')
        try:
            res = requests.get(previous_crawler_node, timeout=5)
            if res.status_code == 200:
                return  # current cralwer node is ok
        except Exception:
            pass

        G.assign('checking_crawler_connection', True)
        crawler_path = G.value('crawler_path', None)

        if crawler_path is None or not os.path.exists(crawler_path):
            LOGGER.warning('GlobalVar crawler file path is not found or path not valid.')
            G.assign('checking_crawler_connection', False)
            return

        with open(crawler_path) as f:
            crawler_server_lst = [line.strip() for line in f.readlines()]

        for crawler_node in crawler_server_lst:
            try:
                res = requests.get(crawler_node, timeout=5)
                if res.status_code == 200 and previous_crawler_node != crawler_node:
                    G.assign('current_crawler_node', crawler_node)
                    LOGGER.warning('Choose crawler node: %s', crawler_node)
                    G.assign('checking_crawler_connection', False)
                    return
            except Exception:
                pass

        LOGGER.error('All crawler servers fail!')
        G.assign('checking_crawler_connection', False)

    @classmethod
    def save_placeholder_at_exception(cls, visa_type: str, location: str):
        """ When fetching visa status encounters failure like `Session Expired` and `Endpoint Timeout`
            save the last successful fetch result into database.
        """
        embassy = G.USEmbassy.get_embassy_by_loc(location)
        if embassy is None:
            embassyLst = G.USEmbassy.get_embassy_list_by_crawler_code(location)
        else:
            embassyLst = [embassy]
        for embassy in embassyLst:
            latest_written = DB.VisaStatus.find_latest_written_visa_status(visa_type, embassy.code)
            avai_dt = None if len(latest_written) < 1 else latest_written[0]['available_date']
            cls.save_fetched_data(
                visa_type,
                embassy.location,
                [0, 0, 0] if avai_dt is None else [avai_dt.year, avai_dt.month, avai_dt.day]
            )

    @classmethod
    def fetch_visa_status(cls, visa_type: str, location: str, req: requests.Session):
        """ Fetch the latest visa status available from crawler server."""
        now = datetime.now().strftime('%H:%M:%S')
        try:
            session = SESSION_CACHE.get_session(visa_type, location)
            if session is None:
                LOGGER.warning('%s, %s, %s, FAILED - No Session', now, visa_type, location)
                return

            if session.sys == 'ais':
                endpoint = G.CRAWLER_API['refresh']['ais'].format(location, session.schedule_id, session.session)
            elif session.sys == 'cgi':
                endpoint = G.CRAWLER_API['refresh']['cgi'].format(session.session)

            url = '{}{}'.format(G.value('current_crawler_node', ''), endpoint)
            try:
                res = req.get(url, timeout=G.WAIT_TIME['refresh'], proxies=G.value('proxies', None))
            except requests.exceptions.Timeout:
                LOGGER.warning('%s, %s, %s, FAILED - Endpoint Timeout.', now, visa_type, location)
                cls.save_placeholder_at_exception(visa_type, location)
                cls.check_crawler_server_connection()
                return
            except requests.exceptions.ConnectionError:
                LOGGER.warning('%s, %s, %s, FAILED - Endpoint Connection Aborted.', now, visa_type, location)
                cls.check_crawler_server_connection()
                return
            else:
                if res.status_code != 200:
                    LOGGER.warning('%s, %s, %s, FAILED - Endpoint Inaccessible.', now, visa_type, location)
                    cls.check_crawler_server_connection()
                    return

                result = res.json()
                LOGGER.debug('fetch_visa_status - Endpoint: %s | Response json: %s', endpoint, json.dumps(result))

                if result['code'] != 0:  # code == 0 stands for success in crawler api code
                    LOGGER.warning('%s, %s, %s, FAILED - Session Expired', now, visa_type, location)

                    # session expired will trigger database update using the last successful fetch result
                    cls.save_placeholder_at_exception(visa_type, location)

                    SESSION_CACHE.produce_new_session_request(visa_type, location, session)
                    return

                if session.sys == 'cgi':
                    dt_segments = [int(dt_seg) for dt_seg in result['msg'].split('-')]
                    cls.save_fetched_data(visa_type, location, dt_segments)
                    LOGGER.info('%s, %s, %s, SUCCESS - %d/%d/%d', now, visa_type, location, *dt_segments)

                elif session.sys == 'ais':
                    date_lst = result['msg']
                    for city, dt_segments in date_lst:
                        if city in G.AIS_MONITORING_CITY:
                            cls.save_fetched_data(visa_type, city, dt_segments)
                            LOGGER.info(
                                '%s, %s, %s, %s, SUCCESS - %d/%d/%d',
                                now,
                                visa_type,
                                location,
                                city,
                                *dt_segments
                            )

                    new_session = Session(
                        session=(result['session'], session.schedule_id),
                        sys=session.sys
                    )
                    SESSION_CACHE.replace_session(visa_type, location, session, new_session)

        except Exception:
            LOGGER.error(traceback.format_exc())

    @classmethod
    def consume_new_session_request(cls, task_queue: Queue = G.SESSION_UPDATE_QUEUE):
        """ Consume the session update event in the task queue to request new session
            from crawler server.
        """
        LOGGER.info('Listening to session update request task queue...')
        while True:
            visa_type, location, session = task_queue.get()
            LOGGER.debug(
                'Receive new session update request: %s-%s | Current queue size: %d',
                visa_type,
                location,
                task_queue.qsize()
            )

            if session is None:
                LOGGER.error('A session object from %s-%s is NoneType', visa_type, location)  # just in case

            if not SESSION_CACHE.contain_session(visa_type, location, session):
                LOGGER.debug('Session %s is no longer in the %s-%s session list.', session, visa_type, location)
                continue

            try:
                if session.sys == 'ais':
                    email = G.value(f'ais_email_{visa_type}', None)
                    password = G.value(f'ais_pswd_{visa_type}', None)

                    LOGGER.debug('Fetching new session for AIS: %s, %s, %s', location, email, password)
                    endpoint = G.CRAWLER_API['register']['ais'].format(location, email, password)
                elif session.sys == 'cgi':
                    endpoint = G.CRAWLER_API['register']['cgi'].format(visa_type, location)

                url = '{}{}'.format(G.value('current_crawler_node', ''), endpoint)
                res = requests.get(url, timeout=G.WAIT_TIME['register'], proxies=G.value('proxies', None))
                result = res.json()
                LOGGER.debug(
                    'consume_new_session_request - Endpoint: %s | Response json: %s',
                    endpoint,
                    json.dumps(result)
                )

                if result['code'] != 0:
                    LOGGER.warning(
                        '%s, %s, %s, FAILED - %s',
                        datetime.now().strftime('%H:%M:%S'),
                        visa_type,
                        location,
                        result['msg']
                    )
                    if result['msg'] == "Network Error":
                        SESSION_CACHE.mark_unavailable(visa_type, location)
                    else:
                        cls.check_crawler_server_connection()
                    continue

                # Generate new session object and update cache
                if session.sys == 'ais':
                    new_session = Session((result['session'], result['id']), sys='ais')
                    date_available = bool(len(result['msg']))
                elif session.sys == 'cgi':
                    new_session = Session(result['session'], sys='cgi')
                    date_available = bool(tuple([dt_seg for dt_seg in result['msg'].split('-')]))  # Always True

                if date_available:  # why this flag is needed?
                    LOGGER.info(
                        'consume_new_session_request - %s, %s, %s, SUCCESS - %s',
                        datetime.now().strftime('%H:%M:%S'),
                        visa_type,
                        location,
                        result['msg']
                    )
                    SESSION_CACHE.replace_session(visa_type, location, session, new_session)
            except requests.exceptions.ReadTimeout:
                LOGGER.debug(
                    'consume_new_session_request - request time out for endpoint: %s | %s-%s',
                    endpoint,
                    visa_type,
                    location
                )
                cls.check_crawler_server_connection()
            except Exception:
                LOGGER.error('an unexpected error occured', traceback.format_exc())


if __name__ == "__main__":
    init()
    start_threads()
    change_crawler_server()
