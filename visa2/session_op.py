#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Session operation
"""

import os
import copy
import json
import time
import queue
import base64
import logging
import requests
import traceback
import threading
import numpy as np
import global_var as g
from fast_visa import get_date
from bs4 import BeautifulSoup as bs

logger = logging.getLogger("fast_visa")

replace_items = queue.Queue(maxsize=30)

def init_cache():
    session_file = g.value("session_file", "session.json")
    session = {}
    if os.path.exists(session_file):
        with open(session_file, "r") as f:
            try:
                session = json.load(f)
            except:
                pass
    g.assign("session", session)


def add_session():
    while True:
        visa_type, place, replace = replace_items.get()
        # check if replaced
        if replace:
            session_list = g.value("session", {})
            if not visa_type in session_list:
                session_list[visa_type] = {}
            if not place in session_list[visa_type]:
                session_list[visa_type][place] = []
            if not replace in session_list[visa_type][place]:
                continue
            logger.info("Update session " + replace)
        try:
            cracker = g.value("cracker", None)
            username, passwd, sid = login(cracker, place)
            date = visa_select(visa_type, place, sid)
            if not date:
                continue
            try:
                session_list = g.value("session", {})
                if not visa_type in session_list:
                    session_list[visa_type] = {}
                if not place in session_list[visa_type]:
                    session_list[visa_type][place] = []
                if replace:
                    idx = session_list[visa_type][place].index(replace)
                    session_list[visa_type][place][idx] = sid
                else:
                    session_list[visa_type][place].append(sid)
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


def replace_session(visa_type, place, sess):
    # append to replace queue
    logger.debug("replace session: %s, %s, %s" % (visa_type, place, sess))
    replace_items.put((visa_type, place, sess))


def get_session(visa_type, place):
    # get a session given visa type and place. return None if failed.
    session = g.value("session", {})
    if not visa_type in session or not place in session[visa_type]:
        return None
    idx = g.value("idx_%s_%s" % (visa_type, place), 0)
    sess_list = session[visa_type][place]
    if len(sess_list) == 0:
        return None
    sess = sess_list[idx % len(sess_list)]
    logger.debug("session: " + sess)
    g.assign("idx_%s_%s" % (visa_type, place), idx + 1)
    return sess


def get_session_count(visa_type, place):
    session_list = g.value("session", {})
    if not visa_type in session_list:
        session_list[visa_type] = {}
    if not place in session_list[visa_type]:
        session_list[visa_type][place] = []
    return len(session_list[visa_type][place])


def set_session_pool_size(visa_type, place, size):
    session_list = g.value("session", {})
    if not visa_type in session_list:
        session_list[visa_type] = {}
    if not place in session_list[visa_type]:
        session_list[visa_type][place] = []
    cnt = len(session_list[visa_type][place])
    if cnt < size:
        for _ in range(size - cnt):
            rand_str = "".join([chr(np.random.randint(26) + ord('a')) for _ in range(15)])
            session_list[visa_type][place].append("placeholder_" + rand_str)
    elif cnt > size:
        session_list[visa_type][place] = session_list[visa_type][place][:size]


def login(cracker, place):
    proxies = g.value("proxies", None)

    # get register page
    REG_URI = "https://cgifederal.secure.force.com/SiteRegister?country=China&language=zh_CN"
    REG_HK_URI = "https://cgifederal.secure.force.com/SiteRegister?country=Hong%20Kong&language=zh_CN"
    r = requests.get(REG_HK_URI if place == "香港" else REG_URI, proxies=proxies)
    if r.status_code != 200:
        return None

    # In case of failure
    while True:
        soup = bs(r.text, "html.parser")
        view_state = soup.find(id="com.salesforce.visualforce.ViewState").get("value")
        view_state_version = soup.find(id="com.salesforce.visualforce.ViewStateVersion").get("value")
        view_state_mac = soup.find(id="com.salesforce.visualforce.ViewStateMAC").get("value")
        cookies = r.cookies

        # get recaptcha
        REG_CAPTCHA_URI = "https://cgifederal.secure.force.com/SiteRegister?refURL=https%3A%2F%2Fcgifederal.secure.force.com%2F%3Flanguage%3DChinese%2520%28Simplified%29%26country%3DChina"
        REG_CAPTCHA_HK_URI = "https://cgifederal.secure.force.com/SiteRegister?refURL=https%3A%2F%2Fcgifederal.secure.force.com%2F%3Flanguage%3DChinese%2520%28Simplified%29%26country%3DHong%20Kong"
        data = {
            "AJAXREQUEST": "_viewRoot",
            "Registration:SiteTemplate:theForm": "Registration:SiteTemplate:theForm",
            "Registration:SiteTemplate:theForm:username": "",
            "Registration:SiteTemplate:theForm:firstname": "",
            "Registration:SiteTemplate:theForm:lastname": "",
            "Registration:SiteTemplate:theForm:password": "",
            "Registration:SiteTemplate:theForm:confirmPassword": "",
            "Registration:SiteTemplate:theForm:response": "",
            "Registration:SiteTemplate:theForm:recaptcha_response_field": "",
            "com.salesforce.visualforce.ViewState": view_state,
            "com.salesforce.visualforce.ViewStateVersion": view_state_version,
            "com.salesforce.visualforce.ViewStateMAC": view_state_mac,
            "Registration:SiteTemplate:theForm:j_id177": "Registration:SiteTemplate:theForm:j_id177"
        }
        r = requests.post(REG_CAPTCHA_HK_URI if place == "香港" else REG_CAPTCHA_URI, data=data, cookies=cookies, proxies=proxies)
        if r.status_code != 200:
            return None

        soup = bs(r.text, "html.parser")
        view_state = soup.find(id="com.salesforce.visualforce.ViewState").get("value")
        view_state_version = soup.find(id="com.salesforce.visualforce.ViewStateVersion").get("value")
        view_state_mac = soup.find(id="com.salesforce.visualforce.ViewStateMAC").get("value")
        cookies = r.cookies

        raw = soup.find_all(id='Registration:SiteTemplate:theForm:theId')
        raw = raw[0].attrs['src'].replace('data:image;base64,', '')
        img = base64.b64decode(raw)
        gifname = 'try.gif'
        open(gifname, 'wb').write(img)
        open('gifname', 'w').write(gifname)
        captcha = cracker.solve(img)
        if len(captcha) == 0:
            open('state', 'w').write(
                '自动识别服务挂掉了，请到<a href="https://github.com/Trinkle23897/'
                'us-visa">GitHub</a>上提issue')
            return None

        # click and register
        username = ''.join([chr(np.random.randint(26) + ord('a')) for _ in range(15)]) + "@gmail.com"
        passwd = ''.join(np.random.permutation(' '.join('12345qwert').split()))
        data = {
            "Registration:SiteTemplate:theForm": "Registration:SiteTemplate:theForm",
            "Registration:SiteTemplate:theForm:username": username,
            "Registration:SiteTemplate:theForm:firstname": "Langpu",
            "Registration:SiteTemplate:theForm:lastname": "Te",
            "Registration:SiteTemplate:theForm:password": passwd,
            "Registration:SiteTemplate:theForm:confirmPassword": passwd,
            "Registration:SiteTemplate:theForm:j_id169": "on",
            "Registration:SiteTemplate:theForm:response": captcha,
            "Registration:SiteTemplate:theForm:recaptcha_response_field": "",
            "Registration:SiteTemplate:theForm:submit": "提交",
            "com.salesforce.visualforce.ViewState": view_state,
            "com.salesforce.visualforce.ViewStateVersion": view_state_version,
            "com.salesforce.visualforce.ViewStateMAC": view_state_mac
        }
        r = requests.post(REG_CAPTCHA_HK_URI if place == "香港" else REG_CAPTCHA_URI, data=data, cookies=cookies, proxies=proxies)
        if r.status_code != 200:
            return None
        front_door_uri = r.text.split("'")[-2]
        if front_door_uri.startswith("https"):
            os.system('mv %s log/%s.gif' % (gifname, captcha))
            break
        else:
            if not os.path.exists('fail'):
                os.makedirs('fail')
            os.system('mv %s fail/%s.gif' % (gifname, captcha))
            if hasattr(cracker, 'wrong'):
                cracker.wrong()

    # open front door
    r = requests.get(front_door_uri, cookies=cookies, proxies=proxies)
    cookies = r.cookies
    return username, passwd, cookies["sid"]

def visa_select(visa_type, place, sid):
    proxies = g.value("proxies", None)
    cookies = copy.deepcopy(g.COOKIES)
    cookies["sid"] = sid

    # select immigrant/nonimmigrant visa
    select_visa_type_uri = "https://cgifederal.secure.force.com/selectvisatype"
    r = requests.get(select_visa_type_uri, cookies=cookies, proxies=proxies)
    if r.status_code != 200:
        return None
    soup = bs(r.text, "html.parser")
    view_state = soup.find(id="com.salesforce.visualforce.ViewState").get("value")
    view_state_version = soup.find(id="com.salesforce.visualforce.ViewStateVersion").get("value")
    view_state_mac = soup.find(id="com.salesforce.visualforce.ViewStateMAC").get("value")
    view_state_csrf = soup.find(id="com.salesforce.visualforce.ViewStateCSRF").get("value")
    data = {
        "j_id0:SiteTemplate:theForm": "j_id0:SiteTemplate:theForm",
        "j_id0:SiteTemplate:theForm:ttip": "Nonimmigrant Visa",
        "j_id0:SiteTemplate:theForm:j_id176": "继续",
        "com.salesforce.visualforce.ViewState": view_state,
        "com.salesforce.visualforce.ViewStateVersion": view_state_version,
        "com.salesforce.visualforce.ViewStateMAC": view_state_mac,
        "com.salesforce.visualforce.ViewStateCSRF": view_state_csrf
    }
    r = requests.post(select_visa_type_uri, data=data, cookies=cookies, proxies=proxies)
    if r.status_code != 200:
        return None

    # select place
    if place != "香港":
        select_post_uri = "https://cgifederal.secure.force.com/selectpost"
        r = requests.get(select_post_uri, cookies=cookies, proxies=proxies)
        if r.status_code != 200:
            return None
        soup = bs(r.text, "html.parser")
        view_state = soup.find(id="com.salesforce.visualforce.ViewState").get("value")
        view_state_version = soup.find(id="com.salesforce.visualforce.ViewStateVersion").get("value")
        view_state_mac = soup.find(id="com.salesforce.visualforce.ViewStateMAC").get("value")
        view_state_csrf = soup.find(id="com.salesforce.visualforce.ViewStateCSRF").get("value")
        contact_id = soup.find(id="j_id0:SiteTemplate:j_id112:contactId").get("value")
        place2id = {
            "北京": "j_id0:SiteTemplate:j_id112:j_id165:0", 
            "成都": "j_id0:SiteTemplate:j_id112:j_id165:1", 
            "广州": "j_id0:SiteTemplate:j_id112:j_id165:2", 
            "上海": "j_id0:SiteTemplate:j_id112:j_id165:3", 
            "沈阳": "j_id0:SiteTemplate:j_id112:j_id165:4"
        }
        place_code = soup.find(id=place2id[place]).get("value")
        data = {
            "j_id0:SiteTemplate:j_id112": "j_id0:SiteTemplate:j_id112",
            "j_id0:SiteTemplate:j_id112:j_id165": place_code,
            "j_id0:SiteTemplate:j_id112:j_id169": "继续",
            "j_id0:SiteTemplate:j_id112:contactId": contact_id,
            "com.salesforce.visualforce.ViewState": view_state,
            "com.salesforce.visualforce.ViewStateVersion": view_state_version,
            "com.salesforce.visualforce.ViewStateMAC": view_state_mac,
            "com.salesforce.visualforce.ViewStateCSRF": view_state_csrf
        }
        r = requests.post(select_post_uri, data=data, cookies=cookies, proxies=proxies)
        if r.status_code != 200:
            return None

    # select visa category
    select_visa_category_uri = "https://cgifederal.secure.force.com/selectvisacategory"
    r = requests.get(select_visa_category_uri, cookies=cookies, proxies=proxies)
    if r.status_code != 200:
        return None
    soup = bs(r.text, "html.parser")
    view_state = soup.find(id="com.salesforce.visualforce.ViewState").get("value")
    view_state_version = soup.find(id="com.salesforce.visualforce.ViewStateVersion").get("value")
    view_state_mac = soup.find(id="com.salesforce.visualforce.ViewStateMAC").get("value")
    view_state_csrf = soup.find(id="com.salesforce.visualforce.ViewStateCSRF").get("value")
    contact_id = soup.find(id="j_id0:SiteTemplate:j_id109:contactId").get("value")
    prefix = "j_id0:SiteTemplate:j_id109:j_id162:"
    category2id = {
        "B": {"北京": 0, "成都": 0, "广州": 0, "上海": 0, "沈阳": 0, "香港": 1}, 
        "F": {"北京": 1, "成都": 1, "广州": 1, "上海": 1, "沈阳": 1, "香港": 0}, 
        "O": {"北京": 4, "成都": 2, "广州": 3, "上海": 4, "沈阳": 2, "香港": 3}, 
        "H": {"北京": 2, "广州": 3, "上海": 2, "香港": 3}, 
        "L": {"北京": 3, "广州": 2, "上海": 3, "香港": 3} 
    }
    category_code = soup.find(id=prefix + str(category2id[visa_type][place])).get("value")
    data = {
        "j_id0:SiteTemplate:j_id109": "j_id0:SiteTemplate:j_id109",
        "j_id0:SiteTemplate:j_id109:j_id162": category_code,
        "j_id0:SiteTemplate:j_id109:j_id166": "继续",
        "j_id0:SiteTemplate:j_id109:contactId": contact_id,
        "com.salesforce.visualforce.ViewState": view_state,
        "com.salesforce.visualforce.ViewStateVersion": view_state_version,
        "com.salesforce.visualforce.ViewStateMAC": view_state_mac,
        "com.salesforce.visualforce.ViewStateCSRF": view_state_csrf
    }
    r = requests.post(select_visa_category_uri, data=data, cookies=cookies, proxies=proxies)
    if r.status_code != 200:
        return None

    # select visa type
    select_visa_code_uri = "https://cgifederal.secure.force.com/selectvisacode"
    r = requests.get(select_visa_code_uri, cookies=cookies, proxies=proxies)
    if r.status_code != 200:
        return None
    soup = bs(r.text, "html.parser")
    view_state = soup.find(id="com.salesforce.visualforce.ViewState").get("value")
    view_state_version = soup.find(id="com.salesforce.visualforce.ViewStateVersion").get("value")
    view_state_mac = soup.find(id="com.salesforce.visualforce.ViewStateMAC").get("value")
    view_state_csrf = soup.find(id="com.salesforce.visualforce.ViewStateCSRF").get("value")
    type2id = {
        "F": 0, 
        "B": 2, 
        "H": 0, 
        "O": 10 if place == "香港" else (6 if place == "广州" else 0), 
        "L": 7 if place == "香港" else 1
    }
    inputs = soup.find_all("input")
    type_codes = [x.get("value") for x in inputs if x.get("name") == "selectedVisaClass"]
    type_code = type_codes[type2id[visa_type]]
    data = {
        "j_id0:SiteTemplate:theForm": "j_id0:SiteTemplate:theForm",
        "j_id0:SiteTemplate:theForm:j_id178": "继续",
        "selectedVisaClass": type_code,
        "com.salesforce.visualforce.ViewState": view_state,
        "com.salesforce.visualforce.ViewStateVersion": view_state_version,
        "com.salesforce.visualforce.ViewStateMAC": view_state_mac,
        "com.salesforce.visualforce.ViewStateCSRF": view_state_csrf
    }
    r = requests.post(select_visa_code_uri, data=data, cookies=cookies, proxies=proxies)
    if r.status_code != 200:
        return None

    # update data
    update_data_uri = "https://cgifederal.secure.force.com/updatedata"
    r = requests.get(select_visa_code_uri, cookies=cookies, proxies=proxies)
    if r.status_code != 200:
        return None
    date = get_date(r.text)
    logger.info("%s, %s, SUCCESS_N, %s" % (visa_type, place, date))
    if date:
        g.assign("status_%s_%s" % (visa_type, place), date)
    return date
