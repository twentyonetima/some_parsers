import datetime
import logging

import requests
from bs4 import BeautifulSoup
from models import BaseDataUnit
import pandas as pd


def data_unit_iterator() -> BaseDataUnit:
    SOURCE_URL = "https://www.nationalbank.kz/ru/news/licenziya-na-osushchestvlenie-obmennyh-operaciy-s-nalichnoy-inostrannoy-valyutoy-vydavaemaya-upolnomochenym-organizaciyam/rubrics/1930"
    response = requests.get(SOURCE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    actual_data_block = soup.find(class_='posts-files__item')
    excel_table_link = "https://www.nationalbank.kz/" + actual_data_block.find(class_='posts-files__info').find('a').get('href')
    df = pd.read_excel(excel_table_link)
    for index, row in df.iterrows():
        row_id = row.iloc[0]
        if not isinstance(row_id, int) and not isinstance(row_id, str):
            continue
        if isinstance(row_id, str) and not row_id.isdigit():
            continue
        if isinstance(row.iloc[2], datetime.datetime):
            row.iloc[2] = row.iloc[2].strftime('%d.%m.%y')
        try:
            data_unit = BaseDataUnit(
                type='white_list',
                name=row.iloc[3],
                nbok_license_issue_date=row.iloc[2],
                bin=str(row.iloc[4]),
                organizational_and_legal_form=row.iloc[5],
                legal_entity_address=row.iloc[6],
                addresses_of_exchange_offices=row.iloc[7],
                country='Казахстан',
                source=SOURCE_URL
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row {row}")
