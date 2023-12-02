import asyncio
import json
import logging
import time

import aiohttp
import requests
from bs4 import BeautifulSoup

from models import BaseDataUnit

source = 'https://moneysmart.gov.au/companies-you-should-not-deal-with'
api_for_json_data = 'https://static.moneysmart.gov.au/_data/investor-alert-list.json?v=1700597429996'


def data_unit_iterator() -> BaseDataUnit:
    response = requests.get(url=api_for_json_data, headers={
        'User-Agent': 'Mozilla/5.0(X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    })

    data = response.json()

    for d in data:
        try:
            address = ' '.join(d['addresses']) if d['addresses'] else ''
            links = d['websites'] if d['websites'] else []
            email = d['emails'] if d['emails'] else []
            phones = d['phones'] if d['phones'] else []
            data_unit = BaseDataUnit(
                type='black_list',
                source=source,
                country='Австралия',
                name=d['nameMandatory'],
                organizational_and_legal_form=address,
                links=links,
                email=email,
                phones=phones,
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")
