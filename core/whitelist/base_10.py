# 10
# Франция
# https://www.amf-france.org/fr/espace-professionnels/fintech/mes-relations-avec-lamf/obtenir-un-enregistrement-un-agrement-psan#Liste_des_PSAN_enregistrs_auprs_de_lAMF
# Наименование, дата регистрации, регистрационный номер, вид услуги


import json
import logging
from time import sleep
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from selenium import webdriver
from slugify import slugify

from models import BaseDataUnit

ref = 'white_list'

URL_START = 'https://www.amf-france.org/fr/espace-professionnels/fintech/mes-relations-avec-lamf/obtenir-un-enregistrement-un-agrement-psan#Liste_des_PSAN_enregistrs_auprs_de_lAMF'
URL_PREFIX = 'https://www.amf-france.org'

NAME_SET = ['name', 'date_publish', 'govkz_type_of_activity', 'cbr_license_id', 'type']

temp_list_file = []


def translate(text_input):
    translator = GoogleTranslator(source='french', target='russian')
    try:
        translation = translator.translate(text_input)
    except Exception as e:
        print(f'Error while translate: {e}')
        translation = text_input
    return translation


def text_cleaner(text_to_clean):
    text_cleaned = text_to_clean.replace('\n', ', ').replace('  ', " ").replace(',,', ",").strip(',').replace('  ',
                                                                                                              " ").strip()
    return text_cleaned


def append_save_as_data(data_set):
    global temp_list_file
    temp_list_file.append(';'.join(data_set))


def parse_as_extended(item, param=None):
    global ref
    one_entry = item.find_all('td')
    data_set = []
    for i, item in enumerate(one_entry):
        if i == 1:
            try:
                item_to_add = item.find('p')
                to_add = text_cleaner(item_to_add.text)
            except:
                to_add = text_cleaner(item.text)
        else:
            to_add = text_cleaner(item.text)
        data_set.append(to_add)
    if param:
        to_add = []
        additional = param.find_all('td')
        for add_to in additional:
            index23 = text_cleaner(add_to.text)
            to_add.append(index23)

        result_set = [data_set[0], data_set[1]]
        add_as_3 = data_set[2] + ', ' + to_add[0]
        result_set.append(add_as_3)
        add_as_4 = data_set[3] + ', ' + to_add[1]
        result_set.append(add_as_4)
        result_set.append(data_set[4])

        data_set = result_set[:]

    data_set.append(ref)
    data_set.insert(3, translate(data_set.pop(3)))

    append_save_as_data(data_set[1:])


def main_url_proceed(url):
    chrome_options_1 = webdriver.ChromeOptions()
    prefs_1 = {'profile.managed_default_content_settings.images': 2}
    chrome_options_1.add_experimental_option('prefs', prefs_1)
    driver_1 = webdriver.Chrome(options=chrome_options_1)
    browser_1 = driver_1
    browser_1.get(url)
    sleep(10)
    file_text = browser_1.page_source

    soup = BeautifulSoup(file_text, features='lxml')

    data_to_parse = soup.find('div', 'table-responsive')
    table_no_titles = data_to_parse.find('tbody')
    trs = table_no_titles.find_all('tr')

    for i, item in enumerate(trs):

        if i < len(trs):
            if i + 1 < len(trs):
                if trs[i + 1] == 2:
                    parse_as_extended(item, trs[i + 1])
                elif len(item) == 5:
                    parse_as_extended(item)
            elif len(item) == 5:
                parse_as_extended(item)


def data_unit_iterator():
    main_url_proceed(URL_START)
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
                date_publish=firm_as_dict['date_publish'],
                govkz_type_of_activity=firm_as_dict['govkz_type_of_activity'],
                cbr_license_id=firm_as_dict['cbr_license_id'],
                type=firm_as_dict['type'],
                source=URL_START,
                country='Франция',
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
