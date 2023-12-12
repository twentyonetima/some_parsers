import logging
import time
import requests
from bs4 import BeautifulSoup
from googletrans import Translator

from models import BaseDataUnit


def change_using(soup, element_name):
    """
    Метод перехода по ссылкам
    :param element_name: имя селектора
    :param soup:
    :return:
    """
    find_elements = soup.select(element_name)
    return find_elements


def time_out(times):
    """
    Метод задержки паузы
    :param times: время задержки
    :return:
    """
    if times:
        time.sleep(times)


def data_unit_iterator():
    url = "https://www.sec.gov.ph/investors-education-and-information/advisories/#gsc.tab=0"
    type_list = 'black_list'
    # save = SaveHdd.save_json(test)  # save to file
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    page_number = 0

    while page_number < 13:
        print("Page number", page_number)
        time.sleep(10)

        list_data = change_using(soup, ".accordion-content")

        for i in list_data:
            names = i.select('b') if page_number <= 3 else i.select('a')
            dates = i.select('.myDate')

            for name, date in zip(names, dates):
                data = {
                    'name': name.text,
                    'date_publish': date.text,
                    'type': type_list,
                    'social_networks': ["", ],
                    'links': ["", ],
                    'source': url
                }
                try:
                    data_unit = BaseDataUnit(
                        **data
                    )
                    yield data_unit.model_dump_json()
                except Exception as e:
                    logging.error(e)
                    logging.error(f"Error while atempt to transform following row")

        page_number += 1
