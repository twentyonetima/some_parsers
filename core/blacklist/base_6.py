# 6
# Канада
# https://www.osc.ca/en/investors/investor-warnings-and-alerts
# Название организации, примечание, Адрес, сайт, дата добавления
import logging
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
import json
from deep_translator import GoogleTranslator
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from slugify import slugify
from urllib3.exceptions import NewConnectionError, MaxRetryError

from models import BaseDataUnit

ref = 'black_list'
URL_START = 'https://www.osc.ca/en/investors/investor-warnings-and-alerts'
URL_PREFIX = 'https://www.osc.ca'

NAME_SET = ('name', 'govkz_type_of_activity', 'legal_entity_address', 'social_networks', 'date_publish', 'type')

temp_list_file = []


def translate(text_input):
    translator = GoogleTranslator(source='auto', target='ru')
    try:
        translation = translator.translate(text_input)
    except Exception as e:
        print(f'Error while translate: {e}')
        translation = text_input
    return translation


def append_save_as_data(data_set):
    global temp_list_file
    temp_list_file.append(';'.join(data_set))


def take_firm_url(url):
    global ref

    chrome_options_1 = webdriver.ChromeOptions()
    prefs_1 = {'profile.managed_default_content_settings.images': 2}
    chrome_options_1.add_experimental_option('prefs', prefs_1)
    driver_1 = webdriver.Chrome(options=chrome_options_1)
    browser_1 = driver_1
    browser_1.get(url)
    file_text = browser_1.page_source
    soup = BeautifulSoup(file_text, features='lxml')

    name = soup.find('div', 'col-12 page-title__content').text.strip()
    date = soup.find('time', 'datetime').text.strip()

    to_check = soup.find('div', 'nodeInvestorWarnings__body')

    left_side = to_check.find('div', 'nodeInvestorWarnings__left')

    addresses_raw = left_side.find_all('div', 'addresses container mt-1 mb-4')
    addresses = ''
    for address in addresses_raw:
        addresses_check = address.find_all('div', 'my-1')
        for addr in addresses_check:
            to_add = addr.text.replace('City:', '').replace('Country:', '').strip()
            addresses += ', '
            addresses += to_add
            addresses.strip(' ').strip('\n').strip(' ').strip(',').strip(' ').strip('\n').strip(' ')

    addresses = addresses.strip().strip(',').replace('  ', ' ').replace(' ,', ',').replace(',,', ',').strip().strip(',')
    other_names_and_additional_info_box = to_check.find('div', 'nodeInvestorWarnings__right')
    all_names_and_info = other_names_and_additional_info_box.find_all('div', 'info-card__table__row__value')
    other_names_data, add_info_data = all_names_and_info
    description_en = add_info_data.text.strip(' ').strip('\n')
    description_ru = translate(description_en)
    www = extract_www(description_en)
    addresses = translate(addresses)
    date = translate(date)

    return name, description_ru, addresses, www, date, ref


def extract_www(text):
    text_1 = text.split(' ')

    for item in text_1:
        if 'www.' in item:
            return item.strip(',')

    return ''


def take_main_url(url):
    url_main = 'https://www.osc.ca/en/investors/investor-warnings-and-alerts'
    add_to_url = '?page='
    start_page = 0

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

    page = start_page

    browser.get(url_main)
    find_num_pages_text = browser.page_source
    pages = BeautifulSoup(find_num_pages_text, features='lxml')
    pages = pages.find('div', 'view-header').text
    pages.strip('\n')
    pages = pages.split(' ')
    num_of_pages = int(pages[-1].strip('\n')) // 20 + 1

    while page < num_of_pages + 1:

        url = url_main + add_to_url + str(page)

        browser.get(url)

        file_text = browser.page_source

        soup = BeautifulSoup(file_text, features='lxml')
        soup = soup.find_all('div', 'container-fluid view-blocks__wrapper')

        data = soup[1].find_all('div', 'table-row table-row--default')

        for value in data:
            val_2_full = value.find('div', 'column-9')
            url_to_follow = val_2_full.find('a', href=True)['href']

            if val_2_full and url_to_follow:

                while True:
                    try:
                        data_set = take_firm_url(URL_PREFIX + url_to_follow)
                        break
                    except ConnectionError:
                        sleep(60)
                    except OSError:
                        sleep(60)
                    except NewConnectionError:
                        sleep(60)
                    except MaxRetryError:
                        sleep(60)

                append_save_as_data(data_set)

        page += 1


def data_unit_iterator():
    take_main_url(URL_START)
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
                govkz_type_of_activity=firm_as_dict['govkz_type_of_activity'],
                legal_entity_address=firm_as_dict['legal_entity_address'],
                social_networks=[firm_as_dict['social_networks']],
                date_publish=firm_as_dict['date_publish'],
                type=firm_as_dict['type'],
                source=URL_START,
                country='Канада',
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
