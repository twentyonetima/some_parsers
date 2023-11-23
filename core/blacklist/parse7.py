import asyncio
import json
import logging

import aiohttp
import requests
from bs4 import BeautifulSoup

from models import BaseDataUnit


source = 'https://www.fsma.be/en/warnings/companies-operating-unlawfully-in-belgium'


def data_unit_iterator():
    num_of_pages = 1
    response = requests.get(
        url="https://www.fsma.be/en/warnings/companies-operating-unlawfully-in-belgium")
    soup = BeautifulSoup(response.text, "html.parser")
    pagination = soup.find_all("ul", class_="pagination")[0]
    last_page = pagination.find_all("li")[-3]
    num_of_pages = int(last_page.text)

    result = []

    for page in range(num_of_pages):
        response = requests.get(
            url=f"{source}?page={page}")
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.find_all("tbody")[0]
        all_obj = body.find_all("td")
        current = 0
        for i in range(len(all_obj) // 5):
            title = all_obj[current].text.strip()
            # urls = all_obj[current + 2].text.strip()
            urls = [x.text for x in all_obj[current + 2].findAll('li')] if all_obj[current + 2].findAll('li') else []

            note = all_obj[current + 3].text.strip()
            data = all_obj[current + 4].text.strip()
            current += 5

            try:
                data_unit = BaseDataUnit(
                    type="black_list",
                    name=title,
                    links=urls,
                    remarks=note,
                    date_publish=data,
                    country='Бельгия',
                    source=source,
                )
                yield data_unit.model_dump_json()
            except Exception as e:
                logging.error(e)
                logging.error(f"Error while atempt to transform following row")
