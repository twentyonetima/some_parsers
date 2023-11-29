import json
import asyncio
import logging

import aiohttp
import requests
from googletrans import Translator
from bs4 import BeautifulSoup

from models import BaseDataUnit

source = 'https://www.fca.org.uk/consumers/warning-list-unauthorised-firms'


# Emails НЕ ВИДНЫ. Mojet dobavim otdelno email i phones

def data_unit_iterator():
    response = requests.get(
        url=f"{source}?page=0")
    soup = BeautifulSoup(response.text, "html.parser")
    last_page = soup.find_all("a", title="Go to last page")
    last_page = last_page[0].get("href")[6:]

    sites = []
    for page in range(int(last_page) + 1):
        print('page---', page)
        response1 = requests.get(
            url=f"{source}?page={page}")
        soup = BeautifulSoup(response1.text, "html.parser")
        body = soup.find_all("tbody")[0]
        rows = body.find_all("tr")
        for row in rows:
            info = row.find_all("td")
            name = info[0].text
            url = info[0].find_all("a")[0].get("href")
            data = info[1].text.strip()
            sites.append([name, url, data])

        result = []
        # with open("result.json", "w") as json_file:
        for site in sites:
            response = requests.get(url=f"https://www.fca.org.uk{site[1]}")
            soup = BeautifulSoup(response.text, "lxml")
            main_text = soup.find_all("section", class_="copy-block default")
            paragrapths_blocks = main_text[1].text
            paragrapths = paragrapths_blocks.split("\n")
            data = {}

            for paragraph in paragrapths:
                if "Name:" in paragraph:
                    data.update({"name": paragraph.split("Name:")[-1].strip()})
                elif "Address:" in paragraph:
                    data.update({"address": paragraph.split("Address:")[-1].strip()})
                elif "Website:" in paragraph:
                    data.update({"site": [paragraph.split("Website:")[-1].strip()]})
                elif "Social Media Details:" in paragraph:
                    data.update({"media": paragraph.split("Social Media Details:")[-1]})
                else:
                    pass
            translator = Translator()
            note = translator.translate(paragrapths_blocks, dest="ru")
            data.update({"remarks": note.text})

            try:
                data_unit = BaseDataUnit(
                    type="black_list",
                    name=data['name'],
                    links=data['site'] if 'site' in data else [],
                    social_networks=[data['media']] if 'media' in data else [],
                    remarks=data['remarks'],
                    date_publish=site[2],
                    country='Великобритания',
                    source=source,
                )
                yield data_unit.model_dump_json()
            except Exception as e:
                logging.error(e)
                logging.error(f"Error while atempt to transform following row")
        sites = []
        # json.dump(data, json_file, ensure_ascii=False)
