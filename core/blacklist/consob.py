import logging

import requests
from bs4 import BeautifulSoup

from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    url = 'https://www.consob.it/web/consob-and-its-activities/warnings?viewId=ultime_com_tutela'
    response = requests.get(url)
    response.encoding = 'utf-8'
    bs = BeautifulSoup(response.text, "lxml")

    td = bs.select('li b')
    names = []

    for i in td:
        name = i.text
        if name:
            names.append(name)
    for i in names:
        try:
            data_unit = BaseDataUnit(
                type='black_list',
                source='https://www.consob.it/web/consob-and-its-activities/warnings?viewId=ultime_com_tutela',
                name=i,
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
