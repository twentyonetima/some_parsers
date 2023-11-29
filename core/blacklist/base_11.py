# 11
# Украина
# https://www.nssmc.gov.ua/activity/insha-diialnist/zakhyst-investoriv/#tab-2
# Название организации, Сайт


import json
import logging

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from slugify import slugify

from models import BaseDataUnit

ref = 'black_list'
URL_START = 'https://www.nssmc.gov.ua/activity/insha-diialnist/zakhyst-investoriv/#tab-2'
URL_PREFIX = 'https://www.osc.ca'

NAME_SET = ('name', 'social_networks', 'type')

temp_list_file = []


def append_save_as_data(data_set):
    global temp_list_file
    temp_list_file.append(';'.join(data_set))


def text_cleaner(text_to_clean):
    text_cleaned = text_to_clean.replace('\n', ' ').replace('  ', " ").replace(',,', ",").strip(',').replace('  ',
                                                                                                             " ").strip()
    return text_cleaned


def take_url(url):
    global ref

    service = Service(driver='/chromedriver/')
    # chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": "/"}
    # chrome_options.add_experimental_option("prefs", prefs)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver_1 = webdriver.Chrome(service=service, options=chrome_options)

    browser = driver_1
    browser.get(url)

    current_page = 1

    while current_page:

        file_text = browser.page_source
        soup = BeautifulSoup(file_text, features='lxml')
        data = soup.find('div', 'page-tab tab-2 page-tab_active')
        table_body = data.find('div', 'table-page')
        table_body_in = table_body.find('tbody', 'row-hover')

        table_rows = table_body.find_all('tr')

        for row in table_rows:
            try:
                name = text_cleaner(row.find('td', 'column-1').text)
                www = text_cleaner(row.find('td', 'column-2').text)
                append_save_as_data([name, www, ref])
            except:
                pass

        driver_1.find_element(By.ID, "tablepress-66_next").click()
        try:
            if soup.find('a', 'paginate_button next disabled'):
                current_page = 0
        except:
            current_page += 1


def data_unit_iterator():
    take_url(URL_START)
    global temp_list_file

    result_list = []
    for line in temp_list_file:
        data = line.strip().split(';')
        firm_as_dict = dict(zip(NAME_SET, data))

        if firm_as_dict in result_list:
            continue
        result_list.append(firm_as_dict)
        try:
            data_unit = BaseDataUnit(
                name=firm_as_dict['name'],
                social_networks=[firm_as_dict['social_networks']],
                type=firm_as_dict['type'],
                source=URL_START,
                country='Украина',
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
