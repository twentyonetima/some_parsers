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


def data_unit_iterator():
    global temp_list_file

    url = '/business/licensed-providers/'

    while url:
        data = requests.get(base_url + url)
        soup = BeautifulSoup(data.text, features='lxml')
        all_sections = soup.find_all('section')
        for section in all_sections:
            entity_url = section.find('h3').find('a', href=True)['href']
            org_type = section.find('div', 'result-list__result-term form-check-inline tag').text.strip()
            entity_title = section.find('h3', 'results-list__result-title').text.strip()
            date_publish = section.find('p', 'results-list__result-date').text.strip()

            if '(DBG)' in org_type:
                data = requests.get(base_url + entity_url)
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

                    if title not in temp_list_file:
                        try:
                            data_unit = BaseDataUnit(
                                name=title,
                                type=ref,
                                date_publish=translate(date_publish),
                                govkz_type_of_activity=translate(org_type),
                                source=full_url,
                                country='Новая Зеландия',
                            )
                            yield data_unit.model_dump_json()
                        except Exception as e:
                            logging.error(e)
                            logging.error(f"Error while atempt to transform following row")

                        temp_list_file.append(title)

            else:

                data = section.find('div', 'result--meta-description')
                if 'is NOT licensed' in data or 'license was cancelled' in data or 'SUSPENDED' in data:
                    title = ''
                elif ' (FSP' in entity_title:
                    title = str(entity_title[:entity_title.find(' (FSP')])
                elif ' (previously' in entity_title:
                    title = str(entity_title[:entity_title.find(' (previously')])
                elif ' (formally' in entity_title:
                    title = str(entity_title[:entity_title.find(' (formally')])
                else:
                    title = entity_title

                if title not in temp_list_file or title != '':
                    try:
                        data_unit = BaseDataUnit(
                            name=title,
                            type=ref,
                            date_publish=translate(date_publish),
                            govkz_type_of_activity=translate(org_type),
                            source=full_url,
                            country='Новая Зеландия',
                        )
                        yield data_unit.model_dump_json()
                    except Exception as e:
                        logging.error(e)
                        logging.error(f"Error while atempt to transform following row")

                    temp_list_file.append(title)

        next_step = requests.get(base_url + url)
        next_url = BeautifulSoup(next_step.text, features='lxml')
        try:
            url = next_url.find('a', 'next page-link', href=True)['href']
        except TypeError:
            break
