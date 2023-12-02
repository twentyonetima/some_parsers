# 9
# Андорра: Список
# https://www.afa.ad/ca/entitats-supervisades/entitats-financeres/entitats-financeres-dinversio/registre-dentitats-autoritzades
# "Наименование
# Тип
# Регистрационный номер
# Дата авторизации
# Дата прекращения"
import json
import logging

from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from slugify import slugify

from models import BaseDataUnit

ref = 'white_list'
URL_START = 'https://www.afa.ad/ca/entitats-supervisades/entitats-financeres/entitats-financeres-dinversio/registre-dentitats-autoritzades'
URL_PREFIX = 'https://www.afa.ad'
URL_START_ENG = 'https://www.afa.ad/en/entitats-supervisades/entitats-financeres/entitats-financeres-dinversio/registre-dentitats-autoritzades?set_language=en'

links_to_parse = {
    'Financial Investment Companies': 'https://www.afa.ad/en/entitats-supervisades/entitats-financeres/entitats-financeres-dinversio/registre-dentitats-autoritzades/societats-financeres-d2019inversio',
    'Financial Investment Agencies': 'https://www.afa.ad/en/entitats-supervisades/entitats-financeres/entitats-financeres-dinversio/registre-dentitats-autoritzades/agencies-financeres-d2019inversio',
    'Asset Management Companies': 'https://www.afa.ad/en/entitats-supervisades/entitats-financeres/entitats-financeres-dinversio/registre-dentitats-autoritzades/societats-gestores-de-patrimonis',
    'Investment Advisors': 'https://www.afa.ad/en/entitats-supervisades/entitats-financeres/entitats-financeres-dinversio/registre-dentitats-autoritzades/assessors-financers'
}

NAME_SET = {
    'Commercial name',
    'Registered office',
    'Address',
    'Type',
    'Registration number',
    'Date of authorisation',
    'Link to website',
    'Financial Agents',
    'Authorisation end date',
}

NAME_DICT = {
    'Commercial name': 'name',
    'Registered office': None,
    'Address': None,
    'Type': 'govkz_type_of_activity',
    'Registration number': 'cbr_license_id',
    'Date of authorisation': 'cbr_license_issue_date',
    'Link to website': None,
    'Financial Agents': None,
    'Authorisation end date': 'cbr_license_revocation_date',
    'date_publish': 'Date of authorisation',
}

temp_list_file = []


def translate(text_input):
    translator = GoogleTranslator(source='french', target='russian')
    try:
        translation = translator.translate(text_input)
    except Exception as e:
        print(f'Error while translate: {e}')
        translation = text_input
    return translation


def append_save_as_data(data_set):
    global temp_list_file
    temp_list_file.append(';'.join(data_set))


def proceed_text_data(text):
    text_in_lines = text.split('\n')
    data_set_to_save = []
    for item in NAME_SET:
        for line in text_in_lines:
            if line.lower().startswith(item.lower()):
                line_to_save = line[len(item):].lstrip(':').strip()
                data_set_to_save.append(line_to_save)
                break
        else:
            data_set_to_save.append('')

    return data_set_to_save


def take_main_url():
    global links_to_parse

    for key in links_to_parse:
        url = links_to_parse[key]

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

        soup = BeautifulSoup(browser.page_source, features='lxml')

        results = soup.find('div', id='content-core')

        for _ in results:
            items_to_parse = results.find_all('ul')

            for item in items_to_parse:
                data_set = proceed_text_data(item.text)
                append_save_as_data(data_set)


def data_unit_iterator():
    take_main_url()
    global temp_list_file

    result_list = []
    for line in temp_list_file:
        data = line.strip().split(';')
        firm_as_dict = dict(zip(NAME_SET, data))

        firm_to_save = {}
        for key in firm_as_dict:
            if NAME_DICT[key]:
                firm_to_save[NAME_DICT[key]] = firm_as_dict[key]

        firm_to_save['date_publish'] = firm_to_save['cbr_license_issue_date']

        firm_to_save['govkz_type_of_activity'] = translate(firm_to_save['govkz_type_of_activity'])

        if firm_as_dict in result_list:
            continue
        result_list.append(firm_as_dict)
        try:
            data_unit = BaseDataUnit(
                name=firm_as_dict['name'],
                cbr_license_id=firm_as_dict['cbr_license_id'],
                govkz_type_of_activity=firm_as_dict['govkz_type_of_activity'],
                cbr_license_revocation_date=firm_as_dict['cbr_license_revocation_date'],
                cbr_license_issue_date=firm_as_dict['cbr_license_issue_date'],
                date_publish=firm_as_dict['date_publish'],
                type='white_list',
                source=URL_START,
                country='Андорра',
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
