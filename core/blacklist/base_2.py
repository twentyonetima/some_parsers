# 2
# черный - 19
# Новая Зеландия
# https://www.fma.govt.nz/scams/warnings-and-alerts/
# Название организации, Адрес, Веб-сайты, Электронная почта
#   "name": "Название организации", "entity name"
#   "addresses_of_exchange_offices": "Адрес", "address" translate
#   "link":"Веб-сайты", "websites"
#   "email":"Электронная почта", "email"
#   "type": "black_list",
#   "date_publish"
import logging

from bs4 import BeautifulSoup
import requests
import json
from selenium import webdriver
from slugify import slugify
from deep_translator import GoogleTranslator

from models import BaseDataUnit

URL_BASE = 'https://www.fma.govt.nz'
URL_START = '/scams/warnings-and-alerts/'

FILE_NAME = 'result.txt'
ref = 'black_list'

FULL_URL = URL_BASE + URL_START

NAME_SET = {
    'name': ['RESERVED_FOR_ENTITY'],
    'date_publish': ['RESERVED_FOR_DATE'],
    'type': ['RESERVED_FOR_B-W_LIST_REF'],
    'addresses_of_exchange_offices': ['address', 'addresses'],
    'link': ['websites', 'website'],
    'email': ['email', 'emails'],
}

temp_list_file = []


def translate(text_input):
    """works fine"""
    translator = GoogleTranslator(source='auto', target='ru')
    try:
        translation = translator.translate(text_input)
    except Exception as e:
        print(f'Error while translate: {e}')
        translation = text_input
    return translation


def append_save_as_data(data_set):
    global temp_list_file
    to_write = ';'.join(data_set)
    temp_list_file.append(to_write)


def catch_firm_name_and_date(section):
    """works fine"""
    entity_title = section.find('h3', 'results-list__result-title').text.strip()

    entity_title = entity_title.split(':')
    if type(entity_title) is list:
        entity_title = entity_title[0]
    entity_title = entity_title.split(' - ')
    if type(entity_title) is list:
        entity_title = entity_title[0]
    entity_title = entity_title.split(' – ')
    if type(entity_title) is list:
        entity_title = entity_title[0]

    date_publish = section.find('p', 'results-list__result-date').text.strip()

    return [entity_title, date_publish, '1']


def parse_text_between(text_to_parse, param, param1=None):
    value = text_to_parse[
            text_to_parse.lower().find(param) + len(param) + 1:text_to_parse.lower().find(param1) if param1 else None]
    return value.strip()


def parce_text_to_tags(entity_to_parce, parsing_tags):
    key_i = 0
    dict_2 = {}
    text_to_proceed = entity_to_parce.text[entity_to_parce.text.lower().find(parsing_tags[0]):]

    if text_to_proceed == '':
        text_to_proceed = entity_to_parce.text

    while key_i < len(parsing_tags):

        if key_i == len(parsing_tags) - 1:
            value = parse_text_between(text_to_proceed, parsing_tags[key_i])
        else:
            value = parse_text_between(text_to_proceed, parsing_tags[key_i], parsing_tags[key_i + 1])

        key = parsing_tags[key_i]

        key = key.strip(':')

        dict_2[key.strip()] = value

        key_i += 1

    data_set_2 = []

    for key in NAME_SET:
        if NAME_SET[key][0] in dict_2:
            data_set_2.append(dict_2[NAME_SET[key][0]])
        elif NAME_SET[key][-1] in dict_2:
            data_set_2.append(dict_2[NAME_SET[key][-1]])
        else:
            data_set_2.append('')

    return data_set_2


def parse_section(entity_url):
    chrome_options_2 = webdriver.ChromeOptions()
    prefs_2 = {'profile.managed_default_content_settings.images': 2}
    chrome_options_2.add_experimental_option('prefs', prefs_2)
    driver_2 = webdriver.Chrome(options=chrome_options_2)
    browser_2 = driver_2
    browser_2.get(URL_BASE + entity_url)
    file_text = browser_2.page_source
    soup_2 = BeautifulSoup(file_text, features='lxml')
    table = soup_2.find('div', 'col-auto col-lg-6 content-element__content')

    all_ps = table.find_all('p')
    parsing_tags = []
    entity_to_parce = ''
    all_strongs = []

    for item in all_ps:
        if item.find_all('strong'):
            all_strongs.append(item)
            if 'Entity name'.lower() in item.find('strong').text.lower():
                entity_to_parce = item
    if entity_to_parce == '':
        for item in all_ps[::-1]:

            if item.find('strong'):
                entity_to_parce = item
                break

    strongs = entity_to_parce.find_all('strong')

    for item in strongs:
        if not item.text.lower().strip() in parsing_tags:
            parsing_tags.append(item.text.lower().strip())

    data_set_3 = parce_text_to_tags(entity_to_parce, parsing_tags)[3:]

    return data_set_3


def start_parse(full_url):
    chrome_options_1 = webdriver.ChromeOptions()
    prefs_1 = {'profile.managed_default_content_settings.images': 2}
    chrome_options_1.add_experimental_option('prefs', prefs_1)
    driver_1 = webdriver.Chrome(options=chrome_options_1)
    browser_1 = driver_1

    url = full_url

    data_set_1 = ['no data parsed. check the parser']

    while url:

        browser_1.get(url)
        file_text = browser_1.page_source
        soup = BeautifulSoup(file_text, features='lxml')

        all_sections = soup.find_all('section')
        for section in all_sections:
            try:
                entity_url = section.find('h3').find('a', href=True)['href']
                data_set_1 = catch_firm_name_and_date(section)
                data_set_1 += parse_section(entity_url)
                append_save_as_data(data_set_1)
            except:
                pass
        try:
            url = URL_BASE + soup.find('a', 'next page-link', href=True)['href']
        except:
            url = None


def data_unit_iterator():
    start_parse(FULL_URL)
    """works fine"""
    name_set_to_save = [key for key in NAME_SET]

    for line in temp_list_file:
        data = line.strip().split(';')
        firm_as_dict = dict(zip(name_set_to_save, data))
        firm_as_dict['date_publish'] = translate(firm_as_dict['date_publish'])
        firm_as_dict['addresses_of_exchange_offices'] = translate(firm_as_dict['addresses_of_exchange_offices'])

        # print(firm_as_dict)
        # dict_to_save[url].append(firm_as_dict)

        try:
            data_unit = BaseDataUnit(
                name=firm_as_dict['name'],
                date_publish=firm_as_dict['date_publish'],
                type=firm_as_dict['type'],
                addresses_of_exchange_offices=firm_as_dict['addresses_of_exchange_offices'],
                social_networks=[firm_as_dict['link']],
                email=firm_as_dict['email'],
                source=FULL_URL,
                country='Новая Зеландия',
            )
            # print(
            #     {
            #     'name': firm_as_dict['name'],
            #     'date_publish': firm_as_dict['date_publish'],
            #     'type': firm_as_dict['type'],
            #     'addresses_of_exchange_offices': firm_as_dict['addresses_of_exchange_offices'],
            #     'social_networks': [firm_as_dict['link']],
            #     'email': firm_as_dict['email'],
            #     'source': FULL_URL,
            #     'country': 'Новая Зеландия',
            #     }
            # )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
