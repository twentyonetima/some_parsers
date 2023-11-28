import logging

import requests
from bs4 import BeautifulSoup

from core.utils.translate import translate
from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    url = 'https://www.fsa.go.jp/ordinary/chuui/mutouroku/04.html'
    response = requests.get(url)
    response.encoding = 'utf-8'
    bs = BeautifulSoup(response.text, "lxml")

    td = bs.find_all('td')
    text = []

    for i in td:
        text.append(i.text)

    text = [text[i:i + 5] for i in range(0, len(text), 5)]
    for i, sublist in enumerate(text):
        remarks = translate(sublist[1])
        try:
            data_unit = BaseDataUnit(
                type='black_list',
                source='https://www.fsa.go.jp/ordinary/chuui/mutouroku/04.html',
                name=sublist[0],
                remarks=remarks,
                country='Япония'
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
