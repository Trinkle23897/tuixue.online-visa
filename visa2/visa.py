#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, tqdm, json, time, argparse, base64, traceback
from time import sleep
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

last_t = 3600

def postprocess(l):
    if l == []:
        return "/"
    m = 'January February March April May June July August September October November December'.split(' ').index(l[1]) + 1
    d = l[2][:-1]
    y = l[3][:-1]
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

def merge(fn, s, cur, keep):
    orig = json.loads(open(fn).read())
    last = {'time': orig['time']}
    for k in s:
        last[k] = orig.get(k, '/')
        if '2-' in k:
            orig[k] = min_date(orig.get(k, '/'), s[k])
        elif not (not keep and s[k] == '/' and orig.get(k, '/') != '/'):
            orig[k] = s[k]
    open('last.json', 'w').write(json.dumps(last, ensure_ascii=False))
    if cur not in orig['index']:
        orig['index'] = [cur] + orig['index']
    open(fn, 'w').write(json.dumps(orig, ensure_ascii=False))

def main():
    open('state', 'w').write('0')
    print(0)
    driver.get("https://cgifederal.secure.force.com/SiteRegister?country=&language=")
    Select(driver.find_element_by_id("Registration:SiteTemplate:theForm:accountId")).select_by_visible_text("China")
    driver.find_element_by_id("Registration:SiteTemplate:theForm:username").send_keys(''.join([chr(np.random.randint(26) + ord('a')) for _ in range(10)]) + "@gmail.com")
    driver.find_element_by_id("Registration:SiteTemplate:theForm:firstname").send_keys("jy")
    driver.find_element_by_id("Registration:SiteTemplate:theForm:lastname").send_keys("w")
    driver.find_element_by_id("Registration:SiteTemplate:theForm:password").send_keys("1q2w3e4r5t")
    driver.find_element_by_id("Registration:SiteTemplate:theForm:confirmPassword").send_keys("1q2w3e4r5t")
    driver.find_element_by_name("Registration:SiteTemplate:theForm:j_id169").click()
    while True:
        img = base64.b64decode(bs(driver.page_source, 'html.parser').find_all(id='Registration:SiteTemplate:theForm:theId')[0].attrs['src'].replace('data:image;base64,', ''))
        if len(img) > 0:
            break
        time.sleep(0.1)
    open('try.gif', 'wb').write(img)
    open('state', 'w').write('1')
    print(1)
    while True:
        captcha = open('state').read()
        if captcha != '1':
            break
        sleep(1)
    open('state', 'w').write('2')
    captcha = ''.join(captcha.split()).lower()
    print(2, captcha)
    driver.find_element_by_id("Registration:SiteTemplate:theForm:recaptcha_response_field").send_keys(captcha)
    driver.find_element_by_id("Registration:SiteTemplate:theForm:submit").click()
    if driver.page_source.find('无法核实验证码') != -1:
        return
    Select(driver.find_element_by_name("j_id0:SiteTemplate:j_id14:j_id15:j_id26:j_id27:j_id28:j_id30")).select_by_visible_text("Chinese (Simplified)")
    driver.find_element_by_name("j_id0:SiteTemplate:j_id14:j_id15:j_id26:j_id27:j_id28:j_id30").click()
    while True:
        try:
            driver.find_element_by_link_text(u"新的签证申请 / 安排面谈时间").click()
            break
        except:
            time.sleep(1)
    os.system('mv try.gif log/%s.gif' % captcha)
    driver.find_element_by_id("j_id0:SiteTemplate:theForm:ttip:2").click()
    driver.find_element_by_xpath("//div[3]/div[3]/div/button/span").click()
    driver.find_element_by_name("j_id0:SiteTemplate:theForm:j_id176").click()
    name = ['北京', '成都', '广州', '上海', '沈阳']
    s = {'time': time.strftime('%Y/%m/%d %H:%M', time.localtime())}
    cur = time.strftime('%Y/%m/%d', time.localtime())
    flag = 0
    print(s['time'])
    for i in range(len(name)):
        n = name[i] + '-' + cur
        n2 = name[i] + '2-' + cur
        driver.get('https://cgifederal.secure.force.com/SelectPost')
        driver.find_element_by_id("j_id0:SiteTemplate:j_id112:j_id165:{}".format(i)).click()
        driver.find_element_by_name("j_id0:SiteTemplate:j_id112:j_id169").click()
        driver.find_element_by_id("j_id0:SiteTemplate:j_id109:j_id162:1").click()
        driver.find_element_by_name("j_id0:SiteTemplate:j_id109:j_id166").click()
        driver.find_element_by_id("selectedVisaClass").click()
        driver.find_element_by_name("j_id0:SiteTemplate:theForm:j_id178").click()
        result = bs(driver.page_source, 'html.parser').findAll(class_='leftPanelText')
        if len(result):
            result = result[0].text.split()[1:]
        s[n] = s[n2] = postprocess(result)
        if s[n] != '/':
            flag += 1
            path = n.replace('-', '/')
            os.makedirs('/'.join(path.split('/')[:-1]), exist_ok=True)
            open(path, 'a+').write(s['time'].split(' ')[-1] + ' ' + s[n] + '\n')
        print(n, s[n])
    merge('../visa/visa.json', s, cur, flag > 1)
    global last_t
    if last_t == 3600:
        last_t = 200
    if flag <= 1:
        last_t = 3600
    next_t = time.time() + last_t
    open('state', 'w').write('3')
    open('next', 'w').write(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(next_t)))# + (' 被封ip了，等待解封中' if flag <= 1 else ''))
    print(3)
    time.sleep(last_t)

if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("--headless") # comment for looking its behavior
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--proxy-server=socks5://127.0.0.1:1080')
    chrome_options.add_argument('--disable-dev-shm-usage')
    while True:
        try:
            driver = webdriver.Chrome(chrome_options=chrome_options)
            main()
            driver.quit()
        except:
            print(traceback.format_exc())
            driver.quit()
