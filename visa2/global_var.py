#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A thread-safe global variable getter-setter interface
"""

from threading import Lock

lock = Lock()


class GlobalVar:
    var_set = {}


def assign(var_name, var_value):
    lock.acquire()
    GlobalVar.var_set[var_name] = var_value
    lock.release()


def value(var_name, default_value):
    lock.acquire()
    if var_name not in GlobalVar.var_set:
        GlobalVar.var_set[var_name] = default_value
        lock.release()
        return default_value
    lock.release()
    return GlobalVar.var_set[var_name]


"""
Some constants
"""

BASE_URI = "https://cgifederal.secure.force.com/"
HOME_URI = "https://cgifederal.secure.force.com/ApplicantHome"
REG_URI = "https://cgifederal.secure.force.com/SiteRegister?country=China&language=zh_CN"
REG_HK_URI = "https://cgifederal.secure.force.com/SiteRegister?country=Hong%20Kong&language=zh_CN"
CANCEL_URI = "https://cgifederal.secure.force.com/appointmentcancellation"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Referer": "https://cgifederal.secure.force.com/apex/LoginLandingPage",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6"
}
COOKIES = {
    "lloopch_loid": "00DC0000000PhuP",
    "lloopch_lpid": "060C0000000QwL9",
    "oid": "00DC0000000PhuP",
    "BrowserId": "HS8xEl7yEeqtP0GMAZMjWw",
    "BrowserId_sec": "HS8xEl7yEeqtP0GMAZMjWw",
    "autocomplete": "1",
    "oinfo": "c3RhdHVzPUFDVElWRSZ0eXBlPTYmb2lkPTAwREMwMDAwMDAwUGh1UA==",
    "apex__aa-time": "j_2FDaJhhG0BVl0oB_2Bm9WXGA_3D_3D",
    "__utmc": "1",
    "__utma": "1.1687928180.1587273582.1587725039.1587728749.11",
    "__utmz": "1.1587728749.11.9.utmcsr=ustraveldocs.com|utmccn=(referral)|utmcmd=referral|utmcct=/cn_zh/index.html",
    "__utmt": "1",
    "__utmb": "1.18.10.1587728749",
    "sid": "whatever",
    "sid_Client": "h00000HzCj70000000PhuP",
    "clientSrc": "127.0.0.1",
    "inst": "APP_0h"
}
MONTH = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}
