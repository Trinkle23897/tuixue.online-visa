import requests
from bs4 import BeautifulSoup
from . import global_var as g

def refresh(country_code, schedule_id, session):
    req = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
        "Referer": "https://ais.usvisa-info.com/%s/niv/schedule/%s/continue_actions" % (country_code, schedule_id),
        "Cookie": "_yatri_session=" + session
    }
    r = req.get("https://ais.usvisa-info.com/%s/niv/schedule/%s/payment" % (country_code, schedule_id), headers=headers)
    if r.status_code != 200:
        print("Error")
    soup = BeautifulSoup(r.text, "html.parser")
    time_table = soup.find("table", {"class": "for-layout"})

    result = []
    if time_table:
        for tr in time_table.find_all("tr"):
            tds = tr.find_all("td")
            if not len(tds) == 2:
                continue
            place = tds[0].text
            date_str = tds[1].text
            s = date_str.split()
            year, month, day = 0, 0, 0
            if len(s) >= 3:
                day_str, month_str, year_str = s[-3], s[-2].replace(",", ""), s[-1]
                year, month, day = int(year_str), g.MONTH[month_str], int(day_str)
            result.append([place, (year, month, day)])

    session = r.cookies["_yatri_session"]
    return result, session
