import logging

import requests
from bs4 import BeautifulSoup
from urlextract import URLExtract

from core.utils.translate import translate
from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    url = 'https://www.consob.it/web/consob-and-its-activities/warnings?viewId=ultime_com_tutela'
    response = requests.get(url, verify=False)
    response.encoding = 'utf-8'
    bs = BeautifulSoup(response.text, "lxml")
    extractor = URLExtract()

    td = bs.select('li b')
    items = []

    for i in td:
        date = None
        parent = i
        while not date:
            parent = parent.parent
            date = parent.find('div', {'class': 'date'})
        date = translate(date.text)
        name = i.text
        link_text = str(i.next_sibling) or str(i.previous_sibling)
        links = extractor.find_urls(link_text)

        if name and not name.isdigit():
            name = name.replace('"', '')
            if name[0] == '-':
                name = name[1:]
            name = name.strip()
            ulr_name = extractor.find_urls(name)
            if ulr_name:
                links = ulr_name
            items.append({
                'name': name,
                'links': links,
                'date': date
            })

    for item in items:
        try:
            data_unit = BaseDataUnit(
                type='black_list',
                source='https://www.consob.it/web/consob-and-its-activities/warnings?viewId=ultime_com_tutela',
                name=item.get('name'),
                links=item.get('links', []),
                date_publish=item.get('date'),
                country='Италия'
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
