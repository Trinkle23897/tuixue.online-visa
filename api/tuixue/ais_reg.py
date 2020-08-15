import sys
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from . import global_var as g

wait_timeout = 60
refresh_interval = 30

chrome_options = Options()
chrome_options.add_argument("--headless")

def register(country_code, email, password):
    # Login
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://ais.usvisa-info.com/%s/niv/users/sign_in" % country_code)
    email_box = driver.find_element_by_id("user_email")
    email_box.clear()
    email_box.send_keys(email)
    password_box = driver.find_element_by_id("user_password")
    password_box.clear()
    password_box.send_keys(password)
    driver.execute_script("document.getElementById('policy_confirmed').click()")
    signin_button = driver.find_element_by_name("commit")
    signin_button.click()

    def wait_loading(xpath, option="locate"):
        try:
            if option == "locate":
                element_present = EC.presence_of_element_located((By.XPATH, xpath))
            elif option == "clickable":
                element_present = EC.element_to_be_clickable((By.XPATH, xpath))
            WebDriverWait(driver, wait_timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")

    # Continue
    continue_button_xpath = "//a[contains(text(), 'Continue')]"
    wait_loading(continue_button_xpath)
    continue_button = driver.find_element_by_xpath(continue_button_xpath)
    continue_button.click()

    # Choose action 
    pay_button_xpath = "//a[contains(text(), 'Pay Visa Fee')]"
    wait_loading(pay_button_xpath)
    banner = driver.find_element_by_tag_name('h5')
    banner.click()
    wait_loading(pay_button_xpath, option="clickable")
    pay_button = driver.find_element_by_xpath(pay_button_xpath)
    pay_button.click()

    # Collect result
    title_xpath = "//h2[contains(text(), 'MRV Fee Details')]"
    wait_loading(title_xpath)
    time_table = driver.find_element_by_class_name('for-layout')
    trs = time_table.find_elements_by_tag_name('tr')
    result = []
    for tr in trs:
        tds = tr.find_elements_by_tag_name('td')
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

    current_url = driver.current_url
    schedule_id = current_url.split("/")[-2]
    session = driver.get_cookie("_yatri_session")["value"]

    driver.quit()
    return result, session, schedule_id

