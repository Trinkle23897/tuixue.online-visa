#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import copy
import time
import json
import random
import logging
import argparse
import requests
import traceback
import threading
import session_op
import global_var as g
from vcode import Captcha
from bs4 import BeautifulSoup as bs
from logging.handlers import TimedRotatingFileHandler


def min_date(a, b):
    if a == '/':
        return b
    if b == '/':
        return a
    i0, i1, i2 = a.split('/')
    i0, i1, i2 = int(i0), int(i1), int(i2)
    j0, j1, j2 = b.split('/')
    j0, j1, j2 = int(j0), int(j1), int(j2)
    if i0 > j0 or i0 == j0 and (i1 > j1 or i1 == j1 and i2 > j2):
        return b
    else:
        return a


def merge(fn, s, cur):
    orig = json.loads(open(fn).read()) if os.path.exists(fn) else {}
    open(fn.replace('.json', '-last.json'), 'w').write(json.dumps(orig, ensure_ascii=False))
    for k in s:
        if '2-' in k:
            orig[k] = min_date(orig.get(k, '/'), s[k])
        else:
            orig[k] = s[k]
    if cur not in orig.get('index', []):
        orig['index'] = [cur] + orig.get('index', [])
    orig['index'], o = orig['index'][:50], orig['index'][50:]
    rmkeys = [i for i in orig if i.split('-')[-1] in o]
    for r in rmkeys:
        orig.pop(r)
    open(fn, 'w').write(json.dumps(orig, ensure_ascii=False))


def init():
    global logger
    
    # get secret and proxy config
    parser = argparse.ArgumentParser()
    parser.add_argument('--secret', type=str, default='', help="Fateadm secret file")
    parser.add_argument('--proxy', type=int, help="local proxy port")
    parser.add_argument('--session', type=str, default="session.json", help="path to save sessions")
    parser.add_argument('--log_dir', type=str, default="./fast_visa", help="directory to save logs")
    args = parser.parse_args()

    # config logging
    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir)
    log_path = os.path.join(args.log_dir, "fast_visa.log")
    logger = logging.getLogger("fast_visa")
    handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1)
    handler.suffix = "%Y%m%d"
    formatter = logging.Formatter("%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.info("Initialization...")

    # config cracker
    if len(args.secret) == 0:
        cracker = args
        cracker.solve = lambda x: input('Captcha: ')
    else:
        cracker = Captcha(args.secret, args.proxy)
    proxies=dict(
        http='socks5h://127.0.0.1:' + str(args.proxy),
        https='socks5h://127.0.0.1:' + str(args.proxy)
    ) if args.proxy else None
    g.assign("proxies", proxies)
    g.assign("cracker", cracker)

    # read cached session pool (if any)
    g.assign("session_file", args.session)
    session_op.init_cache()


def set_interval(func, visa_type, places, interval, rand, first_run=True):
    # just like setInterval() in JavaScript
    def func_wrapper():
        set_interval(func, visa_type, places, interval, rand, first_run=False)
        func(visa_type, places)
    sec = interval + random.randint(0, rand)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    if first_run:
        func(visa_type, places)
    return t


def start_thread():
    logger.info("Start threads...")
    visa_type = "F"
    places = ["沈阳", "成都", "广州", "上海", "北京", "香港"]
    for place in places:
        session_op.set_session_pool_size(visa_type, place, 10)
    set_interval(crawler, visa_type, places, 60, 0)
    visa_type = "B"
    places = ["沈阳", "成都", "广州", "上海", "北京", "香港"]
    for place in places:
        session_op.set_session_pool_size(visa_type, place, 5)
    set_interval(crawler, visa_type, places, 120, 0)
    visa_type = "H"
    places = ["广州", "上海", "北京", "香港"]
    for place in places:
        session_op.set_session_pool_size(visa_type, place, 5)
    set_interval(crawler, visa_type, places, 180, 0)
    visa_type = "O"
    places = ["沈阳", "成都", "广州", "上海", "北京", "香港"]
    for place in places:
        session_op.set_session_pool_size(visa_type, place, 5)
    set_interval(crawler, visa_type, places, 180, 0)
    visa_type = "L"
    places = ["广州", "上海", "北京", "香港"]
    for place in places:
        session_op.set_session_pool_size(visa_type, place, 5)
    set_interval(crawler, visa_type, places, 180, 0)


def crawler_req(visa_type, place):
    try:
        # prepare session
        sess = session_op.get_session(visa_type, place)
        if not sess:
            logger.warning("%s, %s, FAILED, %s" % (visa_type, place, "No Session"))
            return
        cookies = copy.deepcopy(g.COOKIES)
        cookies["sid"] = sess
        # send request
        r = requests.get(g.HOME_URI, headers=g.HEADERS, cookies=cookies, proxies=g.value("proxies", None))
        if r.status_code != 200:
            logger.warning("%s, %s, FAILED, %s" % (visa_type, place, "Session Expired"))
            session_op.replace_session(visa_type, place, sess)
            return
        # parse HTML
        page = r.text
        date = get_date(page)
        if not date:
            logger.warning("%s, %s, FAILED, %s" % (visa_type, place, "Session Expired"))
            session_op.replace_session(visa_type, place, sess)
            return
        elif date == (0, 0, 0):
            logger.warning("%s, %s, FAILED, %s" % (visa_type, place, "Date Not Found"))
            last_status = g.value("status_%s_%s" % (visa_type, place), (0, 0, 0))
            if last_status != (0, 0, 0):
                session_op.replace_session(visa_type, place, sess)
            elif random.random() < (float(open('miss_prob').read()) if os.path.exists('miss_prob') else 0.02):
                session_op.replace_session(visa_type, place, sess)
                return
        if date != (0, 0, 0):
            logger.info("%s, %s, SUCCESS, %s" % (visa_type, place, date))
        g.assign("status_%s_%s" % (visa_type, place), date)
    except:
        logger.error(traceback.format_exc())


def crawler(visa_type, places):
    open(visa_type + '_state', 'w').write('1')
    localtime = time.localtime()
    s = {'time': time.strftime('%Y/%m/%d %H:%M', localtime)}
    second = localtime.tm_sec
    cur = time.strftime('%Y/%m/%d', time.localtime())
    pool = []
    for place in places:
        t = threading.Thread(
            target=crawler_req, 
            args=(visa_type, place)
        )
        t.start()
        pool.append(t)
    for t in pool:
        t.join()

    # write to file
    for place in places:
        n = place + '-' + cur
        n2 = place + '2-' + cur
        y, m, d = g.value("status_%s_%s" % (visa_type, place), (0, 0, 0))
        s[n] = s[n2] = '{}/{}/{}'.format(y, m, d) if y > 0 else "/"
        if s[n] != '/':
            path = visa_type + '/' + n.replace('-', '/')
            os.makedirs('/'.join(path.split('/')[:-1]), exist_ok=True)
            open(path, 'a+').write(s['time'].split(' ')[-1] + ' ' + s[n] + '\n')
    merge('../visa/visa.json' if visa_type == "F" else '../visa/visa-%s.json' % visa_type.lower(), s, cur)
    open(visa_type + '_state', 'w').write('0')
    os.system('python3 notify.py --type ' + visa_type + ' &')


def get_date(page):
    if "Authorization Required" in page:
        return None
    try:
        soup = bs(page, "html.parser")
        text = soup.find_all(class_="leftPanelText")[-1].text
        s = text.split()
        if len(s) >= 3:
            month_str, day_str, year_str = s[-3], s[-2].replace(",", ""), s[-1].replace(".", "")
            year, month, day = int(year_str), g.MONTH[month_str], int(day_str)
            return (year, month, day)
    except:
        return (0, 0, 0)


def forever():
    while True:
        time.sleep(600)


if __name__ == '__main__':
    init()
    start_thread()
    forever()
