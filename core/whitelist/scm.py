import logging

from bs4 import BeautifulSoup
import requests
from googletrans import Translator

from core.utils.consts import LIST_OF_SOCIAL_SITE_DOMAINS
from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    url = 'https://www.sc.com.my/regulation/enforcement/investor-alerts/sc-investor-alerts/investor-alert-list'

    response = requests.get(url)
    bs = BeautifulSoup(response.text, "lxml")

    name = bs.find_all('div', 'a-inner-text')
    _list = []
    for i in name:
        _list.append(i.text)
    _list = _list[14:-5]
    del _list[_list.index("alpha numeric")]

    for i in range(2):
        index = _list.index("DIGITAL ASSETS")
        del _list[index:index + 4]
    index = _list.index("DIGITAL ASSETS")
    del _list[index]

    while "search by alphabet:" in _list:
        index = _list.index("search by alphabet:")
        del _list[index]
    while "alphanumeric" in _list:
        index = _list.index("alphanumeric")
        del _list[index]
    while "Remarks" in _list:
        index = _list.index("Remarks")
        del _list[index]

    _list = [x for x in _list if len(x) != 1]
    _list = [_list[i:i + 5] for i in range(0, len(_list), 5)]

    translator = Translator()

    for i in _list:
        social_networks = []
        links = []
        if i[2].lower() == 'n/a':
            links = []
        else:
            for _l in [x.strip() for x in i[2].strip().split('|') if x != ''] if i[2] != '' else '':
                if any(domain in _l for domain in LIST_OF_SOCIAL_SITE_DOMAINS):  # Проверка на соц. сеть
                    social_networks.append(_l)
                else:
                    links.append(_l)

        try:
            text = translator.translate(i[4], dest='ru').text
        except Exception as e:
            print(f'Error while translate {i[4]}: {e}')
            text = i[4]

        try:
            data_unit = BaseDataUnit(
                type='black_list',
                name=i[0],
                links=links,
                social_networks=social_networks,
                year=i[3],
                remarks=text,
                source='https://www.sc.com.my/regulation/enforcement/investor-alerts/sc-investor-alerts/investor-alert-list',
                country='Малайзия'
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row {i}")
