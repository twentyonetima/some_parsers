# 3
# Финляндия: Поисковик
# https://www.finanssivalvonta.fi/rekisterit/esiterekisteri/
# Наименование, Идентификатор брошюры/номер
import logging

from bs4 import BeautifulSoup
import json

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from slugify import slugify
from selenium import webdriver

from time import sleep

from models import BaseDataUnit

# TODO - решить проблему с автоматизацией!!!!

ref = 'white_list'

start_url = 'https://www.finanssivalvonta.fi/rekisterit/esiterekisteri/'

temp_list_file = []


def from_main_url(url):
    # service = Service(driver='/snap/bin/chromium.chromedriver')
    # chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": "/"}
    # chrome_options.add_experimental_option("prefs", prefs)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-setuid-sandbox")

    chrome_options.add_argument("--remote-debugging-port=9222")  # this

    chrome_options.add_argument("--disable-dev-shm-using")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    driver = webdriver.Chrome(options=chrome_options)
    browser = driver
    browser.get(url)

    driver.find_element(By.ID, "declineButton").click()
    driver.find_element(By.ID, "prospectus-search-button").click()

    sleep(30)

    # table = driver.find_elements(By.ID, 'prospectus-table')

    for element in driver.find_elements(By.CLASS_NAME, "prospectus-row"):
        sleep(1)
        element.click()
    #
    # all_rows = driver.find_element(By.CLASS_NAME, "prospectus-row")
    # for element in all_rows:
    #     element.find_element("td").click()

    file_text = browser.page_source
    soup = BeautifulSoup(file_text, features='lxml')
    all_firms = soup.find_all('tbody', 'info-visible')

    for firm in all_firms:
        one_firm = firm.findNext('tr', 'prospectus-row')
        firm_name = one_firm.findNext('td')
        date = firm_name.findNext('td')
        type_1 = date.findNext('td')
        number_or_date = type_1.findNext('td')

        if len(date.text) == len(number_or_date.text):
            before_num = firm.findNext('tr', 'prospectus-info-row')
            before_num1 = before_num.findNext('table')
            before_num2 = before_num1.findNext('tbody')
            empty = before_num2.findNext('td')
            issuer = empty.findNext('td')
            number_lic = issuer.findNext('td')
        else:
            number_lic = number_or_date

        save_to_file('result.txt', firm_name.text.replace('\n', ' '), number_lic.text.replace('\n', ' '), date.text)


def save_to_file(param, text, text1, text2):
    global temp_list_file
    temp_list_file.append(f'{text};{text1};{text2}')


def data_unit_iterator():
    from_main_url(start_url)
    global temp_list_file

    for line in temp_list_file:
        data = line.strip().split(';')
        if len(data) == 0:
            continue

        try:
            data_unit = BaseDataUnit(
                name=data[0],
                govkz_license=data[1],
                date_publish=data[2],
                type=ref,
                country='Финляндия',
                source=start_url
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
