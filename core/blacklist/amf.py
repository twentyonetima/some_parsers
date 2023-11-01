import logging

import requests
from bs4 import BeautifulSoup
from googletrans import Translator

from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    translator = Translator()

    for j in range(148):
        response = requests.get(
            f'https://www.amf-france.org/fr/espace-epargnants/proteger-son-epargne/listes-noires-et-mises-en-garde?page={j}')
        response.encoding = 'utf-8'
        bs = BeautifulSoup(response.text, "lxml")
        h2 = bs.find_all('h2')
        td = bs.find_all('td', attrs={'data-mobile': 'Catégorie'})
        date = bs.find_all('div', 'date')
        h2_text = []
        td_text = []
        date_text = []
        for i in h2:
            h2_text.append(i.text)
        for i in td:
            try:
                td_text.append(translator.translate(i.find('span', 'tag').text, dest='ru').text)
            except:
                td_text.append(i.find('span', 'tag').text)
        for i in date:
            try:
                date_text.append(translator.translate(i.text, dest='ru').text)
            except:
                td_text.append(i.text)

        for i in range(len(h2_text)):
            try:
                data_unit = BaseDataUnit(
                    type='black_list',
                    source='https://www.amf-france.org/fr/espace-epargnants/proteger-son-epargne/listes-noires-et-mises-en-garde?',
                    name=h2_text[i],
                    remarks=td_text[i],
                )
                yield data_unit.model_dump_json()
            except Exception as e:
                logging.error(e)
                logging.error(f"Error while atempt to transform following row")
