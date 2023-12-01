import logging

import requests
from bs4 import BeautifulSoup
import re

from core.utils.translate import translate
from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    for page_number in range(1, 265):
        page_url = f"https://eservices.mas.gov.sg/fid/institution?page={page_number}"
        response = requests.get(page_url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            company_blocks = soup.find_all('div', class_='inner')

            for company_block in company_blocks:
                company_name_elem = company_block.find('h3', class_='header-inner-2')
                company_name = company_name_elem.text.strip() if company_name_elem is not None else ''

                phone_elem = company_block.find('a', href=True, string=re.compile(r'^\+\d+'))
                phone = phone_elem.text if phone_elem is not None else ''

                address_elem = company_block.find('td', class_='font-resize')
                address = address_elem.text.strip() if address_elem is not None else ''
                address = translate(address)
                address = address.capitalize()

                if company_name:
                    try:
                        data_unit = BaseDataUnit(
                            type='white_list',
                            source='https://eservices.mas.gov.sg/fid/institution',
                            name=company_name,
                            organizational_and_legal_form=address,
                            phones=phone,
                            country='Сингапур'
                        )
                        yield data_unit.model_dump_json()
                    except Exception as e:
                        logging.error(e)
                        logging.error(f"Error while atempt to transform following row")
