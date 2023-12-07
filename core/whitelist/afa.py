import logging

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome

from core.utils.translate import translate
from models import BaseDataUnit


URL_START = 'https://www.afa.ad/ca/entitats-supervisades/entitats-financeres/entitats-financeres-dinversio/registre-dentitats-autoritzades'

NAME_SET = {
    'Commercial name',
    'Registered office',
    'Address',
    'Type',
    'Registration number',
    'Date of authorisation',
    'Link to website',
    'Financial Agents',
    'Authorisation end date',
}


def data_unit_iterator() -> BaseDataUnit:
    links_to_parse = {
        'Financial Investment Companies': 'https://www.afa.ad/en/entitats-supervisades/entitats-financeres/entitats-financeres-dinversio/registre-dentitats-autoritzades/societats-financeres-d2019inversio',
        'Financial Investment Agencies': 'https://www.afa.ad/en/entitats-supervisades/entitats-financeres/entitats-financeres-dinversio/registre-dentitats-autoritzades/agencies-financeres-d2019inversio',
        'Asset Management Companies': 'https://www.afa.ad/en/entitats-supervisades/entitats-financeres/entitats-financeres-dinversio/registre-dentitats-autoritzades/societats-gestores-de-patrimonis',
        'Investment Advisors': 'https://www.afa.ad/en/entitats-supervisades/entitats-financeres/entitats-financeres-dinversio/registre-dentitats-autoritzades/assessors-financers'
    }

    for key in links_to_parse:
        url = links_to_parse[key]

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument("--remote-debugging-port=9222")  # локально с этой строчкой не работает

        driver = Chrome(chrome_options)
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, features='lxml')

        results = soup.find('div', id='content-core')

        for _ in results:
            items_to_parse = results.find_all('ul')

            for item in items_to_parse:
                text_in_lines = item.text.split('\n')
                data_set_to_save = []
                for _item in NAME_SET:
                    for line in text_in_lines:
                        if line.lower().startswith(_item.lower()):
                            line_to_save = line[len(_item):].lstrip(':').strip()
                            data_set_to_save.append(line_to_save)
                            break
                    else:
                        data_set_to_save.append('')
                firm_as_dict = dict(zip(NAME_SET, data_set_to_save))
                name = firm_as_dict.get('Commercial name', None)
                if name:
                    try:
                        govkz_type_of_activity = firm_as_dict.get('Type', '')
                        govkz_type_of_activity = translate(govkz_type_of_activity)
                        cbr_license_id = firm_as_dict.get('Registration number', '')
                        cbr_license_revocation_date = firm_as_dict.get('Authorisation end date', '')
                        date_publish = firm_as_dict.get('Date of authorisation', '')
                        data_unit = BaseDataUnit(
                            name=name,
                            govkz_type_of_activity=govkz_type_of_activity,
                            cbr_license_id=cbr_license_id,
                            cbr_license_revocation_date=cbr_license_revocation_date,
                            date_publish=date_publish,
                            type='white_list',
                            source=URL_START,
                            country='Андорра',
                        )
                        yield data_unit.model_dump_json()
                    except Exception as e:
                        logging.error(e)
                        logging.error(f"Error while atempt to transform following row")
