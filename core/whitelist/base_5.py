# 5
# Ирландия: Поисковик
# https://registers.centralbank.ie/FirmSearchPage.aspx
# Наименование, номер
import json
import logging

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from slugify import slugify

from models import BaseDataUnit

ref = 'white_list'
start_url = 'https://registers.centralbank.ie/FirmSearchPage.aspx'

NAME_SET = ['cbr_license_id', 'name', 'type']

temp_list_file = []


def append_save_as_data(data_set):
    global temp_list_file
    temp_list_file.append(';'.join(data_set))


def parse_list(text_to_parce):
    global ref

    table = text_to_parce.find_all('tr')
    for item in table:
        number = item.find("td", "gvwColumn")
        name = item.find("td", "entityNameColumn")
        if number and name:
            data_to_save = [number.text.replace('\n', ' ').strip(), name.text.replace('\n', ' ').strip(), ref]
            append_save_as_data(data_to_save)


def from_main_url(url):
    service = Service(driver='/chromedriver/')
    # chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": "/"}
    # chrome_options.add_experimental_option("prefs", prefs)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    browser = driver
    browser.get(url)

    driver.find_element(By.ID, "ctl00_cphRegistersMasterPage_btnFirmNameSearch").click()

    previous_ref = 0
    new_ref = 1

    while not previous_ref == new_ref:

        previous_ref = new_ref

        file_text = browser.page_source
        soup = BeautifulSoup(file_text, features='lxml')
        table = soup.find('div', id='content')

        parse_list(table)

        try:
            new_ref += 1
            driver.find_element(By.ID, "ctl00_cphRegistersMasterPage_gvwSearchResults_ctl18_btnNext").click()
        except:
            new_ref = previous_ref


def data_unit_iterator():
    from_main_url(start_url)
    global temp_list_file

    # dict_to_save = {
    #     url: []
    # }

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
                cbr_license_id=firm_as_dict['cbr_license_id'],
                type=firm_as_dict['type'],
                source=start_url,
                country='Ирландия',
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
