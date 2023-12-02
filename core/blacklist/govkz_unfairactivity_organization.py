import logging
import json
import re

import requests

from core.utils.consts import REGEX_URL
from models import BaseDataUnit
from bs4 import BeautifulSoup
import PyPDF2
import io

link_to_source = 'https://www.gov.kz/memleket/entities/ardfm/documents/details/318075?lang=ru'


def data_unit_iterator() -> BaseDataUnit:
    url = 'https://www.gov.kz/uploads/2023/9/1/a56061566f061ebe19c522bc1926c9ca_original.288597.PDF'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Language': 'ru',
    }

    pdf_content = io.BytesIO(requests.get(url).content)
    pdf_reader = PyPDF2.PdfReader(pdf_content)
    for page in pdf_reader.pages:
        strings = page.extract_text().split('\n')
        for ind, string in enumerate(strings):
            if 'Компаниялар атауы' in string:
                strings.remove(string)
                continue
            if not string[0].isnumeric():
                strings[ind - 1] += string
                strings.remove(string)
        for string in strings:
            if not string[0].isnumeric() or string == 'сайта':
                continue
            links = []
            name = ''
            if 'сайттың болуы туралы ақпарат жоқ / нет информации о наличии' in string:
                string = (string.replace('сайттың болуы туралы ақпарат жоқ / нет информации о наличии', '')
                          .replace(' сайта', '').strip())
                name = ' '.join(string.split(' ')[1:])
            else:
                string = string.replace('»', ' ').replace('«', '').split(' ')

                links, name = get_links(string[1:])
            try:
                data_unit = data_transformer(name, links)
                yield data_unit.model_dump_json()
            except Exception as e:
                logging.error(e)
                logging.error(f"Error while atempt to transform following row {string}")


def data_transformer(name, links) -> BaseDataUnit:
    data_unit = BaseDataUnit(
        type='black_list',
        country='Казахстан',
        source=link_to_source,
        name=name,
        links=links,
    )
    return data_unit


def get_links(record: list) -> (list, list):
    links = []
    name = ''
    for r in record:
        if re.search(REGEX_URL, r) or re.match('https|http|\/\/', r):
            if record.index(r) != 0:
                links.append(r)
                continue
        name += ' ' + r
    return links, name.replace(',', '').strip()
