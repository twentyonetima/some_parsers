import logging

import requests
from bs4 import BeautifulSoup
from googletrans import Translator

from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    url = 'https://www.sfc.hk/en/alert-list'
    headers = {
        'User-Agent': 'My User Agent 1.0',
    }

    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    bs = BeautifulSoup(response.text, "lxml")
    translator = Translator()

    td = bs.find_all('td')
    text = []

    for i in td:
        text.append(i.text)
    text = [text[i:i + 3] for i in range(0, len(text), 3)]
    for sublist in text:
        try:
            remarks = translator.translate(sublist[1], dest='ru').text
        except Exception as e:
            print(f'Error while translate: {e}')
            remarks = sublist[1]
        try:
            data_unit = BaseDataUnit(
                type='black_list',
                source='https://www.sfc.hk/en/alert-list',
                name=sublist[0].strip(),
                remarks=remarks,
                country='Гонконг'
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
