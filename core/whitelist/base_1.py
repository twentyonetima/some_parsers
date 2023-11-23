# 1
# белый - 28
# Новая Зеландия: Лицензированные и подотчетные лица
# https://www.fma.govt.nz/business/licensed-providers/
# Наименование, тип
#   "name": "Наименование",
#   "govkz_type_of_activity": "тип",
#   "type": "white_list",
import logging

import requests
from bs4 import BeautifulSoup
import json
from slugify import slugify
from deep_translator import GoogleTranslator

from models import BaseDataUnit

FILE_NAME = 'result.txt'
ref = 'white_list'

base_url = 'https://www.fma.govt.nz'
url_start = '/business/licensed-providers/'

full_url = base_url + url_start

temp_list_file = []


def translate(text_input):
    translator = GoogleTranslator(source='auto', target='ru')
    try:
        translation = translator.translate(text_input)
    except Exception as e:
        print(f'Error while translate: {e}')
        translation = text_input
    return translation


def parse_table(dbg_url, org_type, date_publish):
    data = requests.get(base_url + dbg_url)
    soup = BeautifulSoup(data.text, features='lxml')
    table = soup.find('table')
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    preliminary = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        preliminary.append([cols])

    for row in preliminary[1:]:
        title = row[0][0]

        save_to_file(entity_type=org_type, entity_name=title, date_publish=date_publish)

    return 0


def parse_section(section_data):
    entity_url = section_data.find('h3').find('a', href=True)['href']
    org_type = section_data.find('div', 'result-list__result-term form-check-inline tag').text.strip()
    entity_title = section_data.find('h3', 'results-list__result-title').text.strip()
    date_publish = section_data.find('p', 'results-list__result-date').text.strip()

    if '(DBG)' in org_type:
        parse_table(entity_url, org_type, date_publish)
    else:

        data = section_data.find('div', 'result--meta-description')

        if 'is NOT licensed' in data or 'license was cancelled' in data or 'SUSPENDED' in data:
            pass
        elif ' (FSP' in entity_title:
            title = str(entity_title[:entity_title.find(' (FSP')])
        elif ' (previously' in entity_title:
            title = str(entity_title[:entity_title.find(' (previously')])
        elif ' (formally' in entity_title:
            title = str(entity_title[:entity_title.find(' (formally')])
        else:
            title = entity_title

            save_to_file(entity_type=org_type, entity_name=title, date_publish=date_publish)

    return 0


def parse_list_page(start_url):
    data = requests.get(start_url)
    soup = BeautifulSoup(data.text, features='lxml')
    all_sections = soup.find_all('section')
    for section in all_sections:
        parse_section(section)

    return 0


def save_to_file(entity_type, entity_name, date_publish):
    global temp_list_file
    temp_list_file.append(f'{entity_name};{entity_type};{date_publish}'.replace('\xa0', ' ').replace('\u00a0', ' '))


def parse_part_one():
    url = '/business/licensed-providers/'

    while url:

        parse_list_page(base_url + url)
        next_step = requests.get(base_url + url)
        next_url = BeautifulSoup(next_step.text, features='lxml')
        try:
            url = next_url.find('a', 'next page-link', href=True)['href']
        except TypeError:
            break


def data_unit_iterator():
    parse_part_one()  # Запуск паринга

    global temp_list_file

    to_del_duplicates = {}

    for line in temp_list_file:
        data = line.strip().split(';')

        if data[0] in to_del_duplicates:
            if data[1] == 'Designated Business Group (DBG)':
                continue
        to_del_duplicates[data[0]] = [data[1], data[2]]

    for key in to_del_duplicates:

        try:
            data_unit = BaseDataUnit(
                name=key,
                type=ref,
                date_publish=translate(to_del_duplicates[key][1]),
                govkz_type_of_activity=translate(to_del_duplicates[key][0]),
                source=full_url,
                country='Новая Зеландия',
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
