import copy
import requests
from . import global_var as g
from bs4 import BeautifulSoup as bs

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

def check_alive(page):
    try:
        soup = bs(page, "html.parser")
        error_box = soup.find("ul", class_="error")
        if not error_box:
            return False
        if error_box.text.strip() == "List has no rows for assignment to SObject":
            return True
    except:
        pass
    return False

def do_login(sess):
    cookies = copy.deepcopy(g.COOKIES)
    cookies["sid"] = sess
    r = requests.get(g.CANCEL_URI, headers=g.HEADERS, cookies=cookies)
    if r.status_code != 200:
        return None
    page = r.text
    date = get_date(page)
    if not date:
        return None
    elif date == (0, 0, 0):
        if not check_alive(page):
            return None
    return date

