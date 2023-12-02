import json
import logging

import requests
from bs4 import BeautifulSoup

from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    url = "https://www.gov.kz/memleket/entities/afm/press/article/details/123696?lang=ru"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        tables = soup.find_all('table')  # all tables

        data_list = []
        for table in tables:
            category_title_tags = table.find_all_previous('p', limit=2)
            category_title_tags.reverse()

            category_title = ''
            for ct in category_title_tags:
                if ct.find('strong'):
                    category_title += ct.find('strong').text.strip()

            for row in table.find_all('tr')[1:]:
                columns = row.find_all('td')

                data_list.append([
                    columns[1].text.strip(),  # name
                    columns[2].text.strip() if len(columns) > 2 else '',  # date[govkz_license_decision_date]
                    category_title,  # cbr_license_revokation_reason
                ])

        for dl in data_list:
            try:
                data_unit = BaseDataUnit(
                    type='black_list',
                    name=dl[0],
                    govkz_license_decision_date=dl[1],
                    cbr_license_revokation_reason=dl[2],
                    source='https://www.asc.ca/en/Enforcement/Investment-Caution-List',
                    country='Казахстан',
                )
                yield data_unit.model_dump_json()
            except Exception as e:
                logging.error(e)
                logging.error(f"Error while atempt to transform following row")
