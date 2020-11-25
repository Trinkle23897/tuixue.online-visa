import os
import copy
import json
import base64
import requests
import numpy as np
from . import global_var as g
from . import config
from . import vcode2
from bs4 import BeautifulSoup as bs

def do_register(visa_type, place):
    cracker = vcode2.Captcha()
    req = requests.Session()
    username, passwd, sid = login(cracker, place, req)
    date = visa_select(visa_type, place, sid, req)
    return sid, date

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

def login(cracker, place, requests):
    proxies = g.value("proxies", None)
    ref = config.get("ref")

    # get register page
    REG_URI = "https://cgifederal.secure.force.com/SiteRegister?country=%s&language=zh_CN" % ref[place]
    r = requests.get(REG_URI, proxies=proxies)
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
        REG_CAPTCHA_URI = "https://cgifederal.secure.force.com/SiteRegister?refURL=https%3A%2F%2Fcgifederal.secure.force.com%2F%3Flanguage%3DChinese%2520%28Simplified%29%26country%3D" + ref[place]
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
        r = requests.post(REG_CAPTCHA_URI, data=data, cookies=cookies, proxies=proxies)
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
        #gifname = 'try.gif'
        #open(gifname, 'wb').write(img)
        #open('gifname', 'w').write(gifname)
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
        r = requests.post(REG_CAPTCHA_URI, data=data, cookies=cookies, proxies=proxies)
        if r.status_code != 200:
            return None
        front_door_uri = r.text.split("'")[-2]
        if front_door_uri.startswith("https"):
            #os.system('mv %s log/%s.gif' % (gifname, captcha))
            break
        else:
            #if not os.path.exists('fail'):
            #    os.makedirs('fail')
            #os.system('mv %s fail/%s.gif' % (gifname, captcha))
            if hasattr(cracker, 'wrong'):
                cracker.wrong()

    # open front door
    r = requests.get(front_door_uri, cookies=cookies, proxies=proxies)
    cookies = r.cookies
    return username, passwd, cookies["sid"]

def visa_select(visa_type, place, sid, requests):
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
    place2id = config.get("place2id")
    if sum([place == x for x in place2id.keys()]) > 0:
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
        target_id = "j_id0:SiteTemplate:j_id112:j_id165:" + place2id[place]
        place_code = soup.find(id=target_id).get("value")
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
    category2id = config.get("category2id")
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
    type2id = config.get("type2id")
    inputs = soup.find_all("input")
    type_codes = [x.get("value") for x in inputs if x.get("name") == "selectedVisaClass"]
    type_code = type_codes[type2id[visa_type][place]]
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

    # select visa priority
    priority = config.get("priority")
    if place in priority:
        select_prior_code_uri = "https://cgifederal.secure.force.com/selectvisapriority"
        r = requests.get(select_prior_code_uri, cookies=cookies, proxies=proxies)
        if r.status_code != 200:
            return None
        soup = bs(r.text, "html.parser")
        view_state = soup.find(id="com.salesforce.visualforce.ViewState").get("value")
        view_state_version = soup.find(id="com.salesforce.visualforce.ViewStateVersion").get("value")
        view_state_mac = soup.find(id="com.salesforce.visualforce.ViewStateMAC").get("value")
        view_state_csrf = soup.find(id="com.salesforce.visualforce.ViewStateCSRF").get("value")
        choose_option = priority[place]
        inputs = soup.find_all("input")
        type_codes = [x.get("value") for x in inputs if x.get("name") == "j_id0:SiteTemplate:theForm:SelectedVisaPriority"]
        type_code = type_codes[choose_option[visa_type]]
        data = {
            "j_id0:SiteTemplate:theForm": "j_id0:SiteTemplate:theForm",
            "j_id0:SiteTemplate:theForm:j_id170": "继续",
            "j_id0:SiteTemplate:theForm:SelectedVisaPriority": type_code,
            "com.salesforce.visualforce.ViewState": view_state,
            "com.salesforce.visualforce.ViewStateVersion": view_state_version,
            "com.salesforce.visualforce.ViewStateMAC": view_state_mac,
            "com.salesforce.visualforce.ViewStateCSRF": view_state_csrf
        }
        r = requests.post(select_prior_code_uri, data=data, cookies=cookies, proxies=proxies)
        if r.status_code != 200:
            return None

    # update data
    update_data_uri = "https://cgifederal.secure.force.com/updatedata"
    r = requests.get(update_data_uri, cookies=cookies, proxies=proxies)
    if r.status_code != 200:
        return None
    date = get_date(r.text)
    if date:
        g.assign("status_%s_%s" % (visa_type, place), date)
    return date
