import json
import logging
import re

import requests

from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    url = 'https://www.centralbank.ie/regulation/how-we-regulate/authorisation/unauthorised-firms/search-unauthorised-firms'

    response = requests.get(url)
    content = response.content.decode('utf-8')
    js_list = re.search(r'var\sappData\s=\s(\[[\s\S]*\]);\s*function\sdecodeTitle', content)
    if js_list:
        companies_list = js_list.group(1)
        companies_list = companies_list.replace('decodeTitle(', '').replace('")', '"').replace('	', '')
        companies_list = json.loads(companies_list)
        for company in companies_list:
            name = company.get('firmName', '')
            if name:
                name = name.strip()
                publish_date = company.get('warningDate', '')
                try:
                    data_unit = BaseDataUnit(
                        type='black_list',
                        name=name,
                        date_publish=publish_date,
                        country='Ирландия',
                        source=url,
                    )
                    yield data_unit.model_dump_json()
                except Exception as e:
                    logging.error(e)
                    print(e)
                    logging.error(f"Error while atempt to transform following row")
