import logging
import requests

from core.utils.consts import LIST_OF_SOCIAL_SITE_DOMAINS
from models import BaseDataUnit
import pandas as pd


def data_unit_iterator() -> BaseDataUnit:
    SOURCE_URL = "https://cbr.ru/Queries/UniDbQuery/DownloadCsv/123126?FromDate=10%2F27%2F2023&ToDate=10%2F27%2F2023&posted=False"
    try:
        df = pd.read_csv(SOURCE_URL, encoding="WINDOWS-1251", on_bad_lines='skip', sep=';')
        for index, row in df.iterrows():
            if not isinstance(row.iloc[0], str):
                row.iloc[0] = ""
            if not isinstance(row.iloc[1], str):
                row.iloc[1] = ""
            if not isinstance(row.iloc[2], str):
                row.iloc[2] = ""
            if not isinstance(row.iloc[3], str):
                row.iloc[3] = ""
            if not isinstance(row.iloc[4], str):
                row.iloc[4] = ""
            social_networks = []
            links = []
            for s in row['Site'].split(', '):
                if any(domain in s for domain in LIST_OF_SOCIAL_SITE_DOMAINS):  # Проверка на соц. сеть
                    social_networks.append(s)
                else:
                    links.append(s)
            data_unit = BaseDataUnit(
                type='black_list',
                cbr_license_revocation_date=row['DT'],
                name=row['Name'],
                legal_entity_address=row['ADDR'],
                links=links,
                social_networks= social_networks,
                cbr_license_revokation_reason=row['Sign'],
                source=SOURCE_URL,
                country='Россия'
            )
            yield data_unit.model_dump_json()
    except Exception as e:
        logging.error(e)
        logging.error(f"Error while atempt to transform following row {row}")
