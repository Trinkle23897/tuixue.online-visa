import os
import copy
import json
import base64
import requests
import numpy as np
from . import global_var as g
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
    ref = {"北京": "China", "上海": "China", "广州": "China", "成都": "China", "沈阳": "China", "香港": "Hong%20Kong", "台北": "Taiwan", "金边": "Cambodia", "新加坡": "Singapore", "墨尔本": "Australia", "珀斯": "Australia", "悉尼": "Australia", "首尔": "Korea", "伯尔尼": "Switzerland", "福冈": "Japan", "大坂": "Japan", "那霸": "Japan", "札幌": "Japan", "东京": "Japan", "加德满都": "Nepal", "曼谷": "Thailand", "清迈": "Thailand"}

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
    place2id = {
        "北京": "0", "成都": "1", "广州": "2", "上海": "3", "沈阳": "4",
        "墨尔本": "0", "珀斯": "1", "悉尼": "2",
        "福冈": "0", "大坂": "1", "那霸": "2", "札幌": "3", "东京": "4",
        "曼谷": "0", "清迈": "1"
    }
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
    category2id = {
        "B": {"北京": 0, "成都": 0, "广州": 0, "上海": 0, "沈阳": 0, "香港": 1, "台北": 1, "金边": 0, "新加坡": 1, "墨尔本": 0, "珀斯": 0, "悉尼": 3, "首尔": 4, "伯尔尼": 0, "福冈": 1, "大坂": 0, "那霸": 2, "札幌": 1, "东京": 4, "加德满都": 0, "曼谷": 4, "清迈": 3},
        "F": {"北京": 1, "成都": 1, "广州": 1, "上海": 1, "沈阳": 1, "香港": 0, "台北": 0, "金边": 1, "新加坡": 4, "墨尔本": 1, "珀斯": 0, "悉尼": 0, "首尔": 0, "伯尔尼": 3, "福冈": 0, "大坂": 1, "那霸": 1, "札幌": 0, "东京": 2, "加德满都": 1, "曼谷": 0, "清迈": 0},
        "O": {"北京": 4, "成都": 2, "广州": 3, "上海": 4, "沈阳": 2, "香港": 3, "台北": 3, "金边": 2, "新加坡": 3, "墨尔本": 2, "珀斯": 0, "悉尼": 3, "首尔": 2, "伯尔尼": 1, "福冈": 1, "大坂": 0, "那霸": 2, "札幌": 0, "东京": 5, "加德满都": 0, "曼谷": 1, "清迈": 1},
        "H": {"北京": 2, "广州": 3, "上海": 2, "香港": 3, "台北": 3, "金边": 2, "新加坡": 3, "墨尔本": 2, "珀斯": 0, "悉尼": 3, "首尔": 1, "伯尔尼": 1, "福冈": 1, "大坂": 0, "那霸": 2, "札幌": 1, "东京": 1, "加德满都": 0, "曼谷": 1, "清迈": 1},
        "L": {"北京": 3, "广州": 2, "上海": 3, "香港": 3, "台北": 3, "金边": 2, "新加坡": 3, "墨尔本": 2, "珀斯": 0, "悉尼": 3, "首尔": 1, "伯尔尼": 1, "福冈": 1, "大坂": 2, "那霸": 2, "札幌": 1, "东京": 1, "加德满都": 0, "曼谷": 1, "清迈": 1}
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
        "B": {"北京": 2, "成都": 2, "广州": 2, "上海": 2, "沈阳": 2, "香港": 2, "台北": 2, "金边": 2, "新加坡": 0, "墨尔本": 2, "珀斯": 2, "悉尼": 2, "首尔": 2, "伯尔尼": 2, "福冈": 1, "大坂": 1, "那霸": 0, "札幌": 1, "东京": 1, "加德满都": 1, "曼谷": 1, "清迈": 1},
        "F": {"北京": 0, "成都": 0, "广州": 0, "上海": 0, "沈阳": 0, "香港": 0, "台北": 0, "金边": 0, "新加坡": 0, "墨尔本": 0, "珀斯": 3, "悉尼": 0, "首尔": 0, "伯尔尼": 0, "福冈": 0, "大坂": 0, "那霸": 0, "札幌": 0, "东京": 0, "加德满都": 0, "曼谷": 0, "清迈": 0},
        "O": {"北京": 0, "成都": 0, "广州": 6, "上海": 0, "沈阳": 0, "香港": 10, "台北": 10, "金边": 10, "新加坡": 8, "墨尔本": 7, "珀斯": 14, "悉尼": 10, "首尔": 0, "伯尔尼": 10, "福冈": 14, "大坂": 8, "那霸": 10, "札幌": 6, "东京": 0, "加德满都": 13, "曼谷": 10, "清迈": 10},
        "H": {"北京": 0, "广州": 0, "上海": 0, "香港": 0, "台北": 0, "金边": 0, "新加坡": 0, "墨尔本": 0, "珀斯": 7, "悉尼": 3, "首尔": 0, "伯尔尼": 0, "福冈": 7, "大坂": 3, "那霸": 3, "札幌": 3, "东京": 0, "加德满都": 3, "曼谷": 0, "清迈": 0},
        "L": {"北京": 1, "广州": 1, "上海": 1, "香港": 7, "台北": 7, "金边": 7, "新加坡": 6, "墨尔本": 5, "珀斯": 12, "悉尼": 8, "首尔": 5, "伯尔尼": 7, "福冈": 12, "大坂": 0, "那霸": 8, "札幌": 8, "东京": 5, "加德满都": 9, "曼谷": 7, "清迈": 7}
    }
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

    # update data
    update_data_uri = "https://cgifederal.secure.force.com/updatedata"
    r = requests.get(update_data_uri, cookies=cookies, proxies=proxies)
    if r.status_code != 200:
        return None
    date = get_date(r.text)
    if date:
        g.assign("status_%s_%s" % (visa_type, place), date)
    return date
