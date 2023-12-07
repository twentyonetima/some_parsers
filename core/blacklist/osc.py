import logging
from time import sleep

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from urllib3.exceptions import NewConnectionError, MaxRetryError

from core.utils.translate import translate
from models import BaseDataUnit


def extract_www(text):
    text_1 = text.split(' ')

    for item in text_1:
        if 'www.' in item:
            return item.strip(',')

    return ''


def data_unit_iterator() -> BaseDataUnit:
    url_main = 'https://www.osc.ca/en/investors/investor-warnings-and-alerts'
    start_page = 0

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--remote-debugging-port=9222")

    driver = Chrome(chrome_options)

    page = start_page

    driver.get(url_main)
    find_num_pages_text = driver.page_source
    pages = BeautifulSoup(find_num_pages_text, features='lxml')
    pages = pages.find('div', 'view-header').text
    pages.strip('\n')
    pages = pages.split(' ')
    num_of_pages = int(pages[-1].strip('\n')) // 20 + 1

    while page < num_of_pages + 1:
        url = f'{url_main}?page={page}'

        driver.get(url)
        file_text = driver.page_source

        soup = BeautifulSoup(file_text, features='lxml')
        soup = soup.find_all('div', 'container-fluid view-blocks__wrapper')

        data = soup[1].find_all('div', 'table-row table-row--default')

        for value in data:
            val_2_full = value.find('div', 'column-9')
            url_to_follow = val_2_full.find('a', href=True)['href']

            if val_2_full and url_to_follow:
                while True:
                    try:
                        driver.get('https://www.osc.ca' + url_to_follow)
                        file_text = driver.page_source
                        soup = BeautifulSoup(file_text, features='lxml')

                        name = soup.find('div', 'col-12 page-title__content').text.strip()
                        date = soup.find('time', 'datetime').text.strip()

                        to_check = soup.find('div', 'nodeInvestorWarnings__body')

                        left_side = to_check.find('div', 'nodeInvestorWarnings__left')

                        addresses_raw = left_side.find_all('div', 'addresses container mt-1 mb-4')
                        addresses = ''
                        for address in addresses_raw:
                            addresses_check = address.find_all('div', 'my-1')
                            for addr in addresses_check:
                                to_add = addr.text.replace('City:', '').replace('Country:', '').strip()
                                addresses += ', '
                                addresses += to_add
                                addresses.strip(' ').strip('\n').strip(' ').strip(',').strip(' ').strip('\n').strip(' ')

                        addresses = addresses.strip().strip(',').replace('  ', ' ').replace(' ,', ',').replace(',,',
                                                                                                               ',').strip().strip(
                            ',')
                        other_names_and_additional_info_box = to_check.find('div', 'nodeInvestorWarnings__right')
                        all_names_and_info = other_names_and_additional_info_box.find_all('div',
                                                                                          'info-card__table__row__value')
                        other_names_data, add_info_data = all_names_and_info
                        description_en = add_info_data.text.strip(' ').strip('\n')
                        description_ru = translate(description_en)
                        www = extract_www(description_en)
                        addresses = translate(addresses)
                        addresses = addresses.replace('\n', ' ').strip()
                        date = translate(date)
                        try:
                            data_unit = BaseDataUnit(
                                name=name,
                                govkz_type_of_activity=description_ru,
                                legal_entity_address=addresses,
                                social_networks=[www],
                                date_publish=date,
                                type='black_list',
                                source=url_main,
                                country='Канада',
                            )
                            yield data_unit.model_dump_json()
                        except Exception as e:
                            logging.error(e)
                            logging.error(f"Error while atempt to transform following row")
                        break
                    except ConnectionError:
                        sleep(60)
                    except OSError:
                        sleep(60)
                    except NewConnectionError:
                        sleep(60)
                    except MaxRetryError:
                        sleep(60)
        page += 1
