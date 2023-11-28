import logging
import json
import re

import requests
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
        for string in strings:
            if not string[0].isnumeric() or string == 'сайта':
                continue
            links = []
            if 'сайттың болуы туралы ақпарат жоқ / нет информации о наличии' in string:
                string = string.replace('сайттың болуы туралы ақпарат жоқ / нет информации о наличии', '').strip()
                name = string
            else:
                string = string.split(' ')
                # record = [" ".join(string[1:-1]), string[-1]]
                links, record = get_links(string)
                name = ' '.join(record)
            print(name, links)
            try:
                data_unit = data_transformer(record)
                yield data_unit.model_dump_json()
            except Exception as e:
                logging.error(e)
                logging.error(f"Error while atempt to transform following row {record}")


def data_transformer(record) -> BaseDataUnit:
    data_unit = BaseDataUnit(
        type='black_list',
        country='Казахстан',
        source=link_to_source,
        name=record[0],
        social_networks=record[1],
    )
    return data_unit


def get_links(record: list) -> (list, list):
    links = []

    for r in record:
        if re.match('https|http|\/\/', r) or re.match('\w{2,}.\w{2,}', r):
            record.pop(r)
            r = r.replace(',', '')
            links.append(r)
    return links, record
