import logging

import requests

from bs4 import BeautifulSoup

from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    url = 'https://www.asc.ca/en/Enforcement/Investment-Caution-List'
    response = requests.get(url)

    bs = BeautifulSoup(response.text, "lxml")

    td = bs.find_all('td')
    text = []

    for i in td:
        text.append(i.text)
    while '\xa0' in text:
        index = text.index('\xa0')
        del text[index]

    text = [item.replace('\n', '') for item in text]
    text = [item.replace('\xa0', '') for item in text]

    link = text[::2]
    name = text[1::2]

    for name, link in zip(name[2:], link[1:]):
        try:
            data_unit = BaseDataUnit(
                type='black_list',
                name=name,
                source='https://www.asc.ca/en/Enforcement/Investment-Caution-List',
                country='Альберта(Канада)'
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
