import logging

import requests
from bs4 import BeautifulSoup
from googletrans import Translator

from core.utils.translate import translate
from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    response = requests.get('https://www.sca.gov.ae/en/open-data/violations-and-warnings.aspx')
    response.encoding = 'utf-8'
    bs = BeautifulSoup(response.text, "lxml")
    td = bs.find_all('td')
    text = []

    for i in td:
        text.append(i.text)

    text = text[4:]
    text = [text[i:i + 4] for i in range(0, len(text), 4)]

    for i in text:
        try:
            data_unit = BaseDataUnit(
                type='black_list',
                source='https://www.sca.gov.ae/en/open-data/violations-and-warnings.aspx',
                name=i[0],
                remarks=translate(i[2]),
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
