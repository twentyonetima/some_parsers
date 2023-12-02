import json
import logging

import requests
from bs4 import BeautifulSoup

from core.utils.translate import translate
from models import BaseDataUnit


def process_string(s: str):
    s = s.strip()
    s = s.replace("\'", "__^^^__")
    s = s.replace("\"", "__^^^__")
    s = s.replace("Å\xa0", "__^^^__")
    s = s.replace("â\x80\x99", "__^^^__")
    s = s.replace("â\x80\x9c", "__^^^__")
    s = s.replace("â\x80\x9d", "__^^^__")

    s = s.replace("Ã¤", "a")
    s = s.replace("Ã¡", "a")
    s = s.replace("Ä\x81", "a")
    s = s.replace("Ã\xa0", "a")
    s = s.replace("Ã\x81", "A")
    s = s.replace("Ã\x84", "A")
    s = s.replace("Ã\x85", "A")

    s = s.replace("Ä\x87", "c")
    s = s.replace("Ä\x8d", "c")
    s = s.replace("Ä\x8c", "C")

    s = s.replace("Ã©", "e")
    s = s.replace("Ä\x93", "e")
    s = s.replace("Ä\x97", "e")
    s = s.replace("Ä\x9b", "e")
    s = s.replace("Ã\x89", "E")

    s = s.replace("ï¬\x81", "f")

    s = s.replace("Ä«", "i")
    s = s.replace("Ã\x8c", "i")
    s = s.replace("Ã\xad", "i")
    s = s.replace("Ã\x8d", "I")

    s = s.replace("Å\x82", "l")

    s = s.replace("Î\x9c", "M")

    s = s.replace("Å\x84", "n")
    s = s.replace("Ã\x91", "N")

    s = s.replace("Ã¶", "o")
    s = s.replace("Ã³", "o")
    s = s.replace("Å\x91", "o")
    s = s.replace("Ã\x93", "O")
    s = s.replace("Ã\x96", "O")
    s = s.replace("Ã\x98", "O")
    s = s.replace("Î\x9f", "O")

    s = s.replace("Å\x99", "r")

    s = s.replace("Å¡", "s")
    s = s.replace("Ã\x9f", "ss")

    s = s.replace("Ãº", "u")
    s = s.replace("Å±", "u")
    s = s.replace("Ã\x9a", "u")
    s = s.replace("Ã\x9c", "U")

    s = s.replace("Â\xa0", " ")
    s = s.replace("â\x80\x93", "-")
    s = s.replace("â\x80\x94", "-")

    s = s.replace("Å¥", "t__^^^__")
    s = s.replace("Âº", "º")
    s = s.replace("Ã\x86", "AE")

    return s


def process_row_item(index: int, td: BeautifulSoup):
    data = None
    if index == 0:
        data = None

    elif index == 1:
        item = td.find_all("li")
        data = []
        if item is not None:
            for el in item:
                data.append(el.text.strip().replace("\'", "__^^^__"))

    elif index == 2:
        data = []
        for item in td.find_all("li"):
            data.append(item.text.replace("\'", "__^^^__"))

    elif index == 3:
        data = None

    elif index == 4:
        data = td.text.strip()

    return data


def process_data_from_link(link: str):
    url = "https://portal.mvp.bafin.de/database/InstInfo/" + link
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    content = soup.find("div", {"id": "content"})
    adress = ", ".join(
        content.find_all("p")[1].text.replace("\r\n", "").split("\t")[::-2]
    )
    adress = process_string(adress)

    return {"legal_entity_adress": adress}


def process_row(tr: BeautifulSoup):
    row_data = {
        "type": "white_list",
        "source": "https://portal.mvp.bafin.de/database/InstInfo/"
                  "sucheForm.do?&sucheButtonInstitut=Suche"
    }
    els = tr.find_all("a")
    name = process_string(els[0].text)
    row_data["name"] = name

    if els[1].attrs["href"] == "http://":
        row_data["social_networks"] = ""
    else:
        row_data["social_networks"] = els[1].attrs["href"]

    row_data.update(process_data_from_link(els[0].attrs["href"]))

    return row_data


def process_page(page: BeautifulSoup):
    tbody = page.find("tbody")
    if len(tbody.find("tr").find_all("a")) == 0:
        return None

    one_page = []
    for tr in tbody.find_all("tr"):
        row_data = process_row(tr)
        one_page.append(row_data)

    return one_page


def process_all_pages():
    i = 1
    end = False
    while not end:
        url = "https://portal.mvp.bafin.de/database/InstInfo/sucheForm.do?"
        url += f"d-4012550-p={i}&sucheButtonInstitut=Suche"

        page = requests.get(url)
        page = BeautifulSoup(page.text, "html.parser")

        page_data = process_page(page)
        if page_data is None:
            end = True
            continue
        print(f"page {i} is processed...")

        string_data = str(page_data).replace("\'", "\"")
        yield string_data.replace("__^^^__", "\'")

        i += 1


def data_unit_iterator() -> BaseDataUnit:
    for page_data in process_all_pages():
        page_data = json.loads(page_data)
        for data in page_data:
            try:
                data_unit = BaseDataUnit(
                    type='white_list',
                    name=translate(data.get('name')),
                    legal_entity_address=data.get('legal_entity_adress'),
                    source='https://portal.mvp.bafin.de/database/InstInfo/sucheForm.do?&sucheButtonInstitut=Suche'
                )
                yield data_unit.model_dump_json()
            except Exception as e:
                logging.error(e)
                logging.error(f"Error while atempt to transform following row {data}")
