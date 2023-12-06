import logging

import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from urlextract import URLExtract

from models import BaseDataUnit

source = 'https://www.fca.org.uk/consumers/warning-list-unauthorised-firms'
extractor = URLExtract()


def data_unit_iterator():
    response = requests.get(
        url=f"{source}?page=0")
    soup = BeautifulSoup(response.text, "html.parser")
    last_page = soup.find_all("a", title="Go to last page")
    last_page = last_page[0].get("href")[6:]

    sites = []
    for page in range(71, int(last_page) + 1):
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

        for site in sites:
            response = requests.get(url=f"https://www.fca.org.uk{site[1]}")
            soup = BeautifulSoup(response.text, "lxml")
            main_text = soup.find_all("section", class_="copy-block default")
            try:
                paragrapths_blocks = main_text[1].text
            except:
                paragrapths_blocks = main_text[0].text
            paragrapths = paragrapths_blocks.split("\n")
            data = {}

            if "Name:" not in paragrapths_blocks:
                continue

            for paragraph in paragrapths:
                if "Name:" in paragraph:
                    data.update({"name": paragraph.split("Name:")[-1].strip()})
                elif "Address:" in paragraph:
                    data.update({"address": paragraph.split("Address:")[-1].strip()})
                elif "Website:" in paragraph:
                    data.update({"site": paragraph.split("Website:")[-1].strip().split(', ')})
                elif "Social Media Details:" in paragraph:
                    data.update({"media": paragraph.split("Social Media Details:")[-1]})
                else:
                    pass
            try:
                translator = Translator()
                note = translator.translate(paragrapths_blocks, dest="ru")
                data.update({"remarks": note.text})
            except:
                data.update({"remarks": paragrapths_blocks})
            try:
                name = data['name']
                links = data['site'] if 'site' in data else []
                name, links = remove_links_from_name(name, links)
                data_unit = BaseDataUnit(
                    type="black_list",
                    name=name,
                    links=links,
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


def remove_links_from_name(name: str, links: list):
    found_urls = extractor.find_urls(name)
    _name = name.split(' ')

    if len(_name) > 1:
        for fu in found_urls:
            _name = [x for x in _name if fu not in x]
            if not any(domain in fu for domain in links):
                links.append(fu)

        if _name[-1] in '/-':
            _name.pop(-1)

    return ' '.join(_name), links
