import logging
import re

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    ua = UserAgent()
    header = {
        "Accept": "text/html",
        "User-Agent": ua.random
    }

    req = requests.get(
        'https://www.centralbank.cy/en/licensing-supervision/banks/register-of-credit-institutions-operating-in-cyprus',
        header)
    req = req.text
    soup = BeautifulSoup(req, 'html.parser')

    p = []

    for item in soup.find_all('span', {'style': 'color: rgb(0, 0, 255);'}):
        p.append(item.text)
    filtered_list = [re.sub(r'^\d+\.\s*|\s*$', '', item) for item in p if not re.search(r'[^\x00-\x7F]', item)]

    for item in filtered_list:
        try:
            data_unit = BaseDataUnit(
                name=item,
                type='white_list',
                source='https://www.centralbank.cy/en/licensing-supervision/banks'
                       '/register-of-credit-institutions-operating-in-cyprus',
                country='Кипр'
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
