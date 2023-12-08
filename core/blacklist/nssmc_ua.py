# # 11
# # Украина
# # https://www.nssmc.gov.ua/activity/insha-diialnist/zakhyst-investoriv/#tab-2
# # Название организации, Сайт
#
#
import json
import logging
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from slugify import slugify

from models import BaseDataUnit

ref = 'black_list'
URL_START = 'https://www.nssmc.gov.ua/activity/insha-diialnist/zakhyst-investoriv/#tab-2'
URL_PREFIX = 'https://www.osc.ca'

NAME_SET = ('name', 'links', 'type')

temp_list_file = []


def text_cleaner(text_to_clean):
    text_cleaned = text_to_clean.replace('\n', ' ').replace('  ', " ").replace(',,', ",").strip(',').replace('  ',
                                                                                                             " ").strip()
    return text_cleaned


def data_unit_iterator():
    global ref

    service = Service(driver='/chromedriver/')

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver_1 = webdriver.Chrome(service=service, options=chrome_options)

    browser = driver_1
    browser.get(URL_START)

    current_page = 1

    while current_page:
        file_text = browser.page_source
        soup = BeautifulSoup(file_text, features='lxml')
        data = soup.find('div', 'page-tab tab-2 page-tab_active')
        table_body = data.find('div', 'table-page')
        table_body_in = table_body.find('tbody', 'row-hover')

        table_rows = table_body.find_all('tr')

        for row in table_rows:
            try:
                name = text_cleaner(row.find('td', 'column-1').text)
                www = text_cleaner(row.find('td', 'column-2').text)
                data = [name, www, ref]

                if name not in temp_list_file:
                    temp_list_file.append(name)
                    firm_as_dict = dict(zip(NAME_SET, data))

                    try:
                        data_unit = BaseDataUnit(
                            name=firm_as_dict['name'],
                            links=firm_as_dict['links'].split(' '),
                            type=firm_as_dict['type'],
                            source=URL_START,
                            country='Украина',
                        )
                        yield data_unit.model_dump_json()
                    except Exception as e:
                        logging.error(e)
                        logging.error(f"Error while atempt to transform following row")
            except:
                pass

        # try:
        # driver_1.find_element(By.ID, "tablepress-66_next").click()
        element = driver_1.find_element(By.ID, 'tablepress-66_next')
        driver_1.execute_script("arguments[0].click();", element)

        time.sleep(2)
        # except:
        #     print()

        try:
            if soup.find('a', 'paginate_button next disabled'):
                current_page = 0
        except:
            current_page += 1
