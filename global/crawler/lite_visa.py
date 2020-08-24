#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import copy
import time
import json
import queue
import random
import logging
import argparse
import requests
import traceback
import threading
import subprocess
import numpy as np
import global_var as g
from bs4 import BeautifulSoup as bs
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import notify

replace_items = queue.Queue()

def add_session():
    while True:
        visa_type, place, replace = replace_items.get()
        ais = "-" in place
        # check if replaced
        if replace:
            session_list = g.value("session", {})
            if not visa_type in session_list:
                session_list[visa_type] = {}
            if not place in session_list[visa_type]:
                session_list[visa_type][place] = []
            if ais and not replace in [x[0] for x in session_list[visa_type][place]]:
                continue
            if not ais and not replace in session_list[visa_type][place]:
                continue
            logger.info("Update session " + replace)
        try:
            if ais:
                endpoint = g.value("crawler_node", "") + "/ais/register/?code=%s&email=%s&pswd=%s" % (place, g.value("ais_email_" + visa_type, None), g.value("ais_pswd_" + visa_type, None))
            else:
                endpoint = g.value("crawler_node", "") + "/register/?type=%s&place=%s" % (visa_type, place)
            r = requests.get(endpoint, timeout=40, proxies=g.value("proxies", None))
            result = r.json()
            if ais:
                schedule_id = result["id"]
                date = 1 if len(result["msg"]) > 0 else None
                sid = result["session"]
            else:
                date = tuple(map(int, result["msg"].split("-")))
                sid = result["session"]
            if not date:
                continue
            try:
                session_list = g.value("session", {})
                if not visa_type in session_list:
                    session_list[visa_type] = {}
                if not place in session_list[visa_type]:
                    session_list[visa_type][place] = []
                if replace:
                    if ais:
                        idx = [x[0] for x in session_list[visa_type][place]].index(replace)
                    else:
                        idx = session_list[visa_type][place].index(replace)
                    session_list[visa_type][place][idx] = ([sid, schedule_id] if ais else sid)
                else:
                    session_list[visa_type][place].append(([sid, schedule_id] if ais else sid))
                session_file = g.value("session_file", "session.json")
                with open(session_file, "w") as f:
                    f.write(json.dumps(session_list, ensure_ascii=False))
            except:
                logger.error(traceback.format_exc())
        except:
            logger.error(traceback.format_exc())


t = threading.Thread(
    target=add_session, 
    args=()
)
t.start()

class SessionOp():
    def init_cache(self):
        session_file = g.value("session_file", "session.json")
        session = {}
        if os.path.exists(session_file):
            with open(session_file, "r") as f:
                try:
                    session = json.load(f)
                except:
                    pass
        g.assign("session", session)

    def replace_session(self, visa_type, place, sess):
        # append to replace queue
        logger.debug("replace session: %s, %s, %s" % (visa_type, place, sess))
        replace_items.put((visa_type, place, sess))


    def replace_session_immediate(self, visa_type, place, sess, new_sess):
        ais = "-" in place
        session_list = g.value("session", {})
        if not visa_type in session_list:
            session_list[visa_type] = {}
        if not place in session_list[visa_type]:
            session_list[visa_type][place] = []
        if ais and not sess in [x[0] for x in session_list[visa_type][place]]:
            return
        if not ais and not sess in session_list[visa_type][place]:
            return

        if ais:
            idx = [x[0] for x in session_list[visa_type][place]].index(sess)
            session_list[visa_type][place][idx][0] = new_sess
        else:
            idx = session_list[visa_type][place].index(replace)
            session_list[visa_type][place][idx] = new_sess

        session_file = g.value("session_file", "session.json")
        with open(session_file, "w") as f:
            f.write(json.dumps(session_list, ensure_ascii=False))


    def get_session(self, visa_type, place):
        # get a session given visa type and place. return None if failed.
        session = g.value("session", {})
        if not visa_type in session or not place in session[visa_type]:
            return None
        idx = g.value("idx_%s_%s" % (visa_type, place), 0)
        sess_list = session[visa_type][place]
        if len(sess_list) == 0:
            return None
        sess = sess_list[idx % len(sess_list)]
        logger.debug("session: " + str(sess))
        g.assign("idx_%s_%s" % (visa_type, place), idx + 1)
        return sess


    def get_session_count(self, visa_type, place):
        session_list = g.value("session", {})
        if not visa_type in session_list:
            session_list[visa_type] = {}
        if not place in session_list[visa_type]:
            session_list[visa_type][place] = []
        return len(session_list[visa_type][place])


    def set_session_pool_size(self, visa_type, place, size, ais=False):
        session_list = g.value("session", {})
        if not visa_type in session_list:
            session_list[visa_type] = {}
        if not place in session_list[visa_type]:
            session_list[visa_type][place] = []
        cnt = len(session_list[visa_type][place])
        if cnt < size:
            for _ in range(size - cnt):
                rand_str = "".join([chr(np.random.randint(26) + ord('a')) for _ in range(15)])
                if ais:
                    session_list[visa_type][place].append(["placeholder_" + rand_str, "114514"])
                else:
                    session_list[visa_type][place].append("placeholder_" + rand_str)
        elif cnt > size:
            session_list[visa_type][place] = session_list[visa_type][place][:size]


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


def merge(fn, s, cur, visa_type):
    status = g.value("merge_lock" + visa_type, 0)
    if status == 1:
        return
    g.assign("merge_lock" + visa_type, 1)
    orig = json.loads(open(fn).read()) if os.path.exists(fn) else {}
    open(fn.replace('.json', '-last.json'), 'w').write(json.dumps(orig, ensure_ascii=False))
    last = copy.deepcopy(orig)
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
    g.assign("merge_lock" + visa_type, 0)
    subprocess.check_call(['python3', 'notify.py', '--type', visa_type, '--js', json.dumps(orig, ensure_ascii=False), '--last_js', json.dumps(last, ensure_ascii=False)])
    # os.system('python3 notify.py --type ' + visa_type + ' &')


def init():
    global logger
    global session_op
    
    # get secret and proxy config
    parser = argparse.ArgumentParser()
    parser.add_argument('--proxy', type=int, help="local proxy port")
    parser.add_argument('--session', type=str, default="session.json", help="path to save sessions")
    parser.add_argument('--crawler', type=str, default="crawler.txt", help="crawler api list")
    parser.add_argument('--ais', type=str, default="ais.json", help="ais account in json format")
    parser.add_argument('--log_dir', type=str, default="./lite_visa", help="directory to save logs")
    args = parser.parse_args()

    ais_account = json.loads(open(args.ais, 'r').read())
    for key in ais_account:
        g.assign(key, ais_account[key])
    # config logging
    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir)
    log_path = os.path.join(args.log_dir, "lite_visa.log")
    logger = logging.getLogger("lite_visa")
    handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1)
    handler.suffix = "%Y%m%d"
    formatter = logging.Formatter("%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.info("Initialization...")

    proxies=dict(
        http='socks5h://127.0.0.1:' + str(args.proxy),
        https='socks5h://127.0.0.1:' + str(args.proxy)
    ) if args.proxy else None
    g.assign("proxies", proxies)
    g.assign("crawler_path", args.crawler)
    check_crawler_node()

    # read cached session pool (if any)
    g.assign("session_file", args.session)
    session_op = SessionOp()
    session_op.init_cache()

    # restore previous data
    for visa_type in ["F", "B", "H", "O", "L"]:
        fn = '../visa-%s.json' % visa_type.lower()
        orig = json.loads(open(fn).read()) if os.path.exists(fn) else {}
        if not "time" in orig:
            continue
        date = orig["time"].split()[0]
        data = {}
        for k, v in orig.items():
            if k.endswith("2-" + date):
                continue
            if k.endswith(date):
                place = k.split("-")[0]
                if v == "/":
                    y, m, d = 0, 0, 0
                else:
                    y, m, d = list(map(int, v.split("/")))
                data[place] = (y, m, d)
                g.assign("status_%s_%s" % (visa_type, place), (y, m, d))
        logger.info("%s, Restored date: %s" % (visa_type, str(data)))


def set_interval(func, visa_type, places, interval, rand, first_run=True, codes=None):
    def func_wrapper():
        set_interval(func, visa_type, places, interval, rand, first_run=False, codes=codes)
        func(visa_type, places, codes=codes)
    now_minute = datetime.now().minute
    if not codes and visa_type == "F" and now_minute >= 47 and now_minute <= 49:
        sec = 5
    else:
        sec = interval + random.randint(0, rand)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    if first_run:
        func(visa_type, places, codes=codes)
    return t


def start_thread():
    logger.info("Start threads...")

    places = ["金边", "新加坡", "首尔", "墨尔本", "珀斯", "悉尼", "伯尔尼"]
    cgi_config = {'F': (10, 60), 'B': (5, 120), 'H': (5, 180), 'O': (5, 180), 'L': (5, 180)}
    for visa_type, (number, interval) in cgi_config.items():
        for place in places:
            session_op.set_session_pool_size(visa_type, place, number)
        set_interval(crawler, visa_type, places, interval, 0)

    # ais-account: {'ais_email_F": xxx, "ais_pswd_F": xxx}
    codes = ["en-gb", "en-ca", "en-ae"]
    places = ["Belfast", "London",
              "Calgary", "Halifax", "Montreal", "Ottawa", "Quebec City", "Toronto", "Vancouver",
              "Abu Dhabi", "Dubai"]
    for visa_type in "FBHOL":
        for code in codes:
            session_op.set_session_pool_size(visa_type, code, 1, ais=True)
        set_interval(crawler_ais, visa_type, places, 60, 0, codes=codes)


def crawler_req(visa_type, place, start_time, requests):
    try:
        # prepare session
        sess = session_op.get_session(visa_type, place)
        if not sess:
            logger.warning("%s, %s, %s, FAILED, %s" % (start_time, visa_type, place, "No Session"))
            return
        refresh_endpoint = g.value("crawler_node", "") + "/refresh/?session=" + sess
        try:
            r = requests.get(refresh_endpoint, timeout=7, proxies=g.value("proxies", None))
        except:
            logger.warning("%s, %s, %s, FAILED, %s" % (start_time, visa_type, place, "Endpoint Timeout"))
            check_crawler_node()
            return
        if r.status_code != 200:
            logger.warning("%s, %s, %s, FAILED, %s" % (start_time, visa_type, place, "Endpoint Inaccessible"))
            check_crawler_node()
            return
        result = r.json()
        if result["code"] > 0:
            logger.warning("%s, %s, %s, FAILED, %s" % (start_time, visa_type, place, "Session Expired"))
            session_op.replace_session(visa_type, place, sess)
            return
        date = tuple(map(int, result["msg"].split("-")))
        logger.info("%s, %s, %s, SUCCESS, %s" % (start_time, visa_type, place, date))
        g.assign("status_%s_%s" % (visa_type, place), date)
    except:
        logger.error(traceback.format_exc())


def crawler_req_ais(visa_type, code, places, start_time, requests):
    try:
        # prepare session
        sess, scedule_id = session_op.get_session(visa_type, code)
        if not sess:
            logger.warning("%s, %s, %s, FAILED, %s" % (start_time, visa_type, code, "No Session"))
            return
        refresh_endpoint = g.value("crawler_node", "") + "/ais/refresh/?code=%s&id=%s&session=%s" % (code, scedule_id, sess)
        try:
            r = requests.get(refresh_endpoint, timeout=7, proxies=g.value("proxies", None))
        except:
            logger.warning("%s, %s, %s, FAILED, %s" % (start_time, visa_type, code, "Endpoint Timeout"))
            check_crawler_node()
            return
        if r.status_code != 200:
            logger.warning("%s, %s, %s, FAILED, %s" % (start_time, visa_type, code, "Endpoint Inaccessible"))
            check_crawler_node()
            return
        result = r.json()
        if result["code"] > 0:
            logger.warning("%s, %s, %s, FAILED, %s" % (start_time, visa_type, code, "Session Expired"))
            session_op.replace_session(visa_type, code, sess)
            return
        date_list = result["msg"]
        new_sess = result["session"]
        session_op.replace_session_immediate(visa_type, code, sess, new_sess)
        for place, date in date_list:
            if place not in places:
                continue
            logger.info("%s, %s, %s, %s, SUCCESS, %s" % (start_time, visa_type, code, place, date))
            g.assign("status_%s_%s" % (visa_type, place), date)
    except:
        logger.error(traceback.format_exc())


def crawler(visa_type, places, codes=None):
    localtime = time.localtime()
    s = {'time': time.strftime('%Y/%m/%d %H:%M:%S', localtime)}
    second = localtime.tm_sec
    cur = time.strftime('%Y/%m/%d', time.localtime())
    cur_time = time.strftime('%H:%M:%S', time.localtime())
    pool = []
    req = g.value(visa_type + "_req", requests.Session())
    for place in places:
        t = threading.Thread(
            target=crawler_req, 
            args=(visa_type, place, cur_time, req)
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
            time_hm = time.strftime('%H:%M', localtime)
            open(path, 'a+').write(time_hm + ' ' + s[n] + '\n')
    merge('../visa-%s.json' % visa_type.lower(), s, cur, visa_type)


def crawler_ais(visa_type, places, codes=[]):
    localtime = time.localtime()
    s = {'time': time.strftime('%Y/%m/%d %H:%M:%S', localtime)}
    second = localtime.tm_sec
    cur = time.strftime('%Y/%m/%d', time.localtime())
    cur_time = time.strftime('%H:%M:%S', time.localtime())
    pool = []
    req = g.value(visa_type + "_req", requests.Session())
    for code in codes:
        t = threading.Thread(
            target=crawler_req_ais, 
            args=(visa_type, code, places, cur_time, req)
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
            time_hm = time.strftime('%H:%M', localtime)
            open(path, 'a+').write(time_hm + ' ' + s[n] + '\n')
    merge('../visa-%s.json' % visa_type.lower(), s, cur, visa_type)


def check_crawler_node():
    if g.value("crawler_checking", False):
        return
    g.assign("crawler_checking", True)
    crawler_filepath = g.value("crawler_path", None)
    last_node = g.value("crawler_node", "")
    if not crawler_filepath:
        logger.warning("Crawler file not found")
        g.assign("crawler_checking", False)
        return
    with open(crawler_filepath, "r") as f:
        nodes = list(f.readlines())
    for node in nodes:
        node = node.strip()
        try:
            r = requests.get(node, timeout=5)
            if r.status_code == 200:
                if last_node != node:
                    g.assign("crawler_node", node)
                    logger.warning("Choose Crawler Node: " + node)
                g.assign("crawler_checking", False)
                return
        except:
            pass
    logger.error("All Crawler Nodes Failed")
    g.assign("crawler_checking", False)


def forever():
    while True:
        time.sleep(600)
        check_crawler_node()


if __name__ == '__main__':
    init()
    start_thread()
    forever()
