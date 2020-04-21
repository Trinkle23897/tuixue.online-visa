#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import base64
import argparse
import traceback
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.chrome.options import Options

from vcode import Captcha

base_url = 'https://cgifederal.secure.force.com'


def postprocess(raw):
    if raw == []:
        return "/"
    m = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
         'August', 'September', 'October', 'November', 'December'].index(
        raw[1]) + 1
    d = raw[2][:-1]
    y = raw[3][:-1]
    return '{}/{}/{}'.format(y, m, d)


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
    for k in s:
        if '2-' in k:
            orig[k] = min_date(orig.get(k, '/'), s[k])
        else:
            orig[k] = s[k]
    if cur not in orig.get('index', []):
        orig['index'] = [cur] + orig.get('index', [])
    open(fn, 'w').write(json.dumps(orig, ensure_ascii=False))


def login(driver, cracker, uri, info=''):
    while True:
        print('login', info)
        driver.get(base_url + uri)
        username = ''.join([chr(np.random.randint(26) + ord('a'))
                            for _ in range(15)]) + "@gmail.com"
        driver.find_element_by_id(
            "Registration:SiteTemplate:theForm:username"
        ).send_keys(username)
        driver.find_element_by_id(
            "Registration:SiteTemplate:theForm:firstname").send_keys(
            ''.join(np.random.permutation(' '.join('abcdef').split())))
        driver.find_element_by_id(
            "Registration:SiteTemplate:theForm:lastname").send_keys(
            ''.join(np.random.permutation(' '.join('qwerty').split())))
        passwd = ''.join(np.random.permutation(' '.join('12345qwert').split()))
        driver.find_element_by_id(
            "Registration:SiteTemplate:theForm:password").send_keys(passwd)
        driver.find_element_by_id(
            "Registration:SiteTemplate:theForm:confirmPassword"
        ).send_keys(passwd)
        driver.find_element_by_name(
            "Registration:SiteTemplate:theForm:j_id169").click()
        while True:
            html = bs(driver.page_source, 'html.parser')
            raw = html.find_all(id='Registration:SiteTemplate:theForm:theId')
            raw = raw[0].attrs['src'].replace('data:image;base64,', '')
            img = base64.b64decode(raw)
            if len(img) > 0:
                break
            time.sleep(0.1)
        gifname = 'try.gif'
        open(gifname, 'wb').write(img)
        open('gifname', 'w').write(gifname)
        captcha = cracker.solve(img).replace('1', 'l').lower()
        if len(captcha) == 0:
            open('state', 'w').write(
                '自动识别服务挂掉了，请到<a href="https://github.com/Trinkle23897/'
                'us-visa">GitHub</a>上提issue')
            # exit()
        driver.find_element_by_id(
            "Registration:SiteTemplate:theForm:recaptcha_response_field"
        ).send_keys(captcha)
        driver.find_element_by_id(
            "Registration:SiteTemplate:theForm:submit").click()
        if driver.page_source.find('无法核实验证码') == -1:
            os.system('mv %s log/%s.gif' % (gifname, captcha))
            break
        else:
            if not os.path.exists('fail'):
                os.makedirs('fail')
            os.system('mv %s fail/%s.gif' % (gifname, captcha))


def f_visa(driver, driver2):
    driver.get(base_url + '/selectvisatype')
    driver.find_element_by_id("j_id0:SiteTemplate:theForm:ttip:2").click()
    driver.find_element_by_xpath("//div[3]/div[3]/div/button/span").click()
    driver.find_element_by_name("j_id0:SiteTemplate:theForm:j_id176").click()
    name = ['北京', '成都', '广州', '上海', '沈阳']
    s = {'time': time.strftime('%Y/%m/%d %H:%M', time.localtime())}
    cur = time.strftime('%Y/%m/%d', time.localtime())
    print(s['time'])
    for i in range(len(name)):
        n = name[i] + '-' + cur
        n2 = name[i] + '2-' + cur
        driver.get(base_url + '/SelectPost')
        driver.find_element_by_id(
            "j_id0:SiteTemplate:j_id112:j_id165:{}".format(i)).click()
        driver.find_element_by_name(
            "j_id0:SiteTemplate:j_id112:j_id169").click()
        driver.find_element_by_id(
            "j_id0:SiteTemplate:j_id109:j_id162:1").click()
        driver.find_element_by_name(
            "j_id0:SiteTemplate:j_id109:j_id166").click()
        driver.find_element_by_id("selectedVisaClass").click()
        driver.find_element_by_name(
            "j_id0:SiteTemplate:theForm:j_id178").click()
        result = bs(driver.page_source, 'html.parser').findAll(
            class_='leftPanelText')
        if len(result):
            result = result[0].text.split()[1:]
        s[n] = s[n2] = postprocess(result)
        if s[n] != '/':
            path = 'F/' + n.replace('-', '/')
            os.makedirs('/'.join(path.split('/')[:-1]), exist_ok=True)
            open(path, 'a+').write(s['time'].split(' ')
                                   [-1] + ' ' + s[n] + '\n')
        print('F1/J1', n, s[n])

    driver2.get(base_url + '/SelectVisaCategory')
    driver2.find_element_by_id("j_id0:SiteTemplate:j_id109:j_id162:0").click()
    driver2.find_element_by_name("j_id0:SiteTemplate:j_id109:j_id166").click()
    driver2.find_element_by_id("selectedVisaClass").click()
    driver2.find_element_by_name("j_id0:SiteTemplate:theForm:j_id178").click()
    n = '香港' + '-' + cur
    n2 = '香港' + '2-' + cur
    result = bs(driver2.page_source, 'html.parser').findAll(
        class_='leftPanelText')
    if len(result):
        result = result[0].text.split()[1:]
    s[n] = s[n2] = postprocess(result)
    if s[n] != '/':
        path = 'F/' + n.replace('-', '/')
        os.makedirs('/'.join(path.split('/')[:-1]), exist_ok=True)
        open(path, 'a+').write(s['time'].split(' ')
                               [-1] + ' ' + s[n] + '\n')
    print('F1/J1', n, s[n])
    merge('../visa/visa.json', s, cur)


def b_visa(driver, driver2):
    driver.get(base_url + '/selectvisatype')
    driver.find_element_by_id("j_id0:SiteTemplate:theForm:ttip:2").click()
    driver.find_element_by_xpath("//div[3]/div[3]/div/button/span").click()
    driver.find_element_by_name("j_id0:SiteTemplate:theForm:j_id176").click()
    name = ['北京', '成都', '广州', '上海', '沈阳']
    s = {'time': time.strftime('%Y/%m/%d %H:%M', time.localtime())}
    cur = time.strftime('%Y/%m/%d', time.localtime())
    print(s['time'])
    for i in range(len(name)):
        n = name[i] + '-' + cur
        n2 = name[i] + '2-' + cur
        driver.get(base_url + '/SelectPost')
        driver.find_element_by_id(
            "j_id0:SiteTemplate:j_id112:j_id165:{}".format(i)).click()
        driver.find_element_by_name(
            "j_id0:SiteTemplate:j_id112:j_id169").click()
        driver.find_element_by_id(
            "j_id0:SiteTemplate:j_id109:j_id162:0").click()
        driver.find_element_by_name(
            "j_id0:SiteTemplate:j_id109:j_id166").click()
        driver.find_element_by_xpath(
            "(//input[@id='selectedVisaClass'])[2]").click()
        driver.find_element_by_name(
            "j_id0:SiteTemplate:theForm:j_id178").click()
        result = bs(driver.page_source, 'html.parser').findAll(
            class_='leftPanelText')
        if len(result):
            result = result[0].text.split()[1:]
        s[n] = s[n2] = postprocess(result)
        if s[n] != '/':
            path = 'B/' + n.replace('-', '/')
            os.makedirs('/'.join(path.split('/')[:-1]), exist_ok=True)
            open(path, 'a+').write(s['time'].split(' ')
                                   [-1] + ' ' + s[n] + '\n')
        print('B1/B2', n, s[n])
    driver2.get(base_url + '/SelectVisaCategory')
    driver2.find_element_by_id("j_id0:SiteTemplate:j_id109:j_id162:1").click()
    driver2.find_element_by_name("j_id0:SiteTemplate:j_id109:j_id166").click()
    driver2.find_element_by_xpath("(//input[@id='selectedVisaClass'])[2]").click()
    driver2.find_element_by_name("j_id0:SiteTemplate:theForm:j_id178").click()
    n = '香港' + '-' + cur
    n2 = '香港' + '2-' + cur
    result = bs(driver2.page_source, 'html.parser').findAll(
        class_='leftPanelText')
    if len(result):
        result = result[0].text.split()[1:]
    s[n] = s[n2] = postprocess(result)
    if s[n] != '/':
        path = 'B/' + n.replace('-', '/')
        os.makedirs('/'.join(path.split('/')[:-1]), exist_ok=True)
        open(path, 'a+').write(s['time'].split(' ')
                               [-1] + ' ' + s[n] + '\n')
    print('B1/B2', n, s[n])
    merge('../visa/visa-b.json', s, cur)


def h_visa(driver, driver2):
    driver.get(base_url + '/selectvisatype')
    driver.find_element_by_id("j_id0:SiteTemplate:theForm:ttip:2").click()
    driver.find_element_by_xpath("//div[3]/div[3]/div/button/span").click()
    driver.find_element_by_name("j_id0:SiteTemplate:theForm:j_id176").click()
    name = {'北京': [0, 2], '广州': [2, 3], '上海': [3, 2]}
    s = {'time': time.strftime('%Y/%m/%d %H:%M', time.localtime())}
    cur = time.strftime('%Y/%m/%d', time.localtime())
    print(s['time'])
    for k in name:
        n = k + '-' + cur
        n2 = k + '2-' + cur
        driver.get(base_url + '/SelectPost')
        driver.find_element_by_id(
            "j_id0:SiteTemplate:j_id112:j_id165:{}".format(name[k][0])).click()
        driver.find_element_by_name(
            "j_id0:SiteTemplate:j_id112:j_id169").click()
        driver.find_element_by_id(
            "j_id0:SiteTemplate:j_id109:j_id162:{}".format(name[k][1])).click()
        driver.find_element_by_name(
            "j_id0:SiteTemplate:j_id109:j_id166").click()
        driver.find_element_by_id("selectedVisaClass").click()
        driver.find_element_by_name(
            "j_id0:SiteTemplate:theForm:j_id178").click()
        result = bs(driver.page_source, 'html.parser').findAll(
            class_='leftPanelText')
        if len(result):
            result = result[0].text.split()[1:]
        s[n] = s[n2] = postprocess(result)
        if s[n] != '/':
            path = 'H/' + n.replace('-', '/')
            os.makedirs('/'.join(path.split('/')[:-1]), exist_ok=True)
            open(path, 'a+').write(s['time'].split(' ')
                                   [-1] + ' ' + s[n] + '\n')
        print('H1B', n, s[n])
    driver2.get(base_url + '/SelectVisaCategory')
    driver2.find_element_by_id("j_id0:SiteTemplate:j_id109:j_id162:3").click()
    driver2.find_element_by_name("j_id0:SiteTemplate:j_id109:j_id166").click()
    driver2.find_element_by_id("selectedVisaClass").click()
    driver2.find_element_by_name("j_id0:SiteTemplate:theForm:j_id178").click()
    n = '香港' + '-' + cur
    n2 = '香港' + '2-' + cur
    result = bs(driver2.page_source, 'html.parser').findAll(
        class_='leftPanelText')
    if len(result):
        result = result[0].text.split()[1:]
    s[n] = s[n2] = postprocess(result)
    if s[n] != '/':
        path = 'H/' + n.replace('-', '/')
        os.makedirs('/'.join(path.split('/')[:-1]), exist_ok=True)
        open(path, 'a+').write(s['time'].split(' ')
                               [-1] + ' ' + s[n] + '\n')
    print('H1B', n, s[n])
    merge('../visa/visa-h.json', s, cur)


def main(driver, driver2, cracker):
    open('state', 'w').write('Login Hong Kong')
    login(driver2, cracker,
          '/SiteRegister?country=Hong%20Kong&language=zh_CN', 'Hong Kong')
    driver2.get(base_url + '/selectvisatype')
    driver2.find_element_by_id("j_id0:SiteTemplate:theForm:ttip:1").click()
    while True:
        try:
            driver2.find_element_by_xpath("//div[3]/div/a/span").click()
            break
        except:
            time.sleep(1)
    driver2.find_element_by_name("j_id0:SiteTemplate:theForm:j_id176").click()
    open('state', 'w').write('Login China Mainland')
    login(driver, cracker,
          '/SiteRegister?country=China&language=zh_CN', 'China Mainland')
    open('state', 'w').write('F1/J1 Visa Status Sync')
    f_visa(driver, driver2)
    if os.path.exists('notify.py'):
        os.system('python3 notify.py F &')
    if np.random.rand() < float(open('b_prob').read()):
        open('state', 'w').write('B1/B2 Visa Status Sync')
        b_visa(driver, driver2)
        if os.path.exists('notify.py'):
            os.system('python3 notify.py B &')
    open('state', 'w').write('H1B Visa Status Sync')
    h_visa(driver, driver2)
    if os.path.exists('notify.py'):
        os.system('python3 notify.py H &')
    driver.quit()
    driver2.quit()
    time.sleep(int(open('time').read()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--secret', type=str, default='')
    parser.add_argument('--proxy', type=int, default=1080)
    args = parser.parse_args()
    chrome_options = Options()
    if len(args.secret) == 0:
        cracker = args
        cracker.solve = lambda x: input('Captcha: ')
    else:
        cracker = Captcha(args.secret, 1080)
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument(
        '--proxy-server=socks5://127.0.0.1:%d' % args.proxy)
    chrome_options.add_argument('--disable-dev-shm-usage')
    while True:
        try:
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver2 = webdriver.Chrome(chrome_options=chrome_options)
            main(driver, driver2, cracker)
        except:
            print(traceback.format_exc())
            driver.quit()
            driver2.quit()
