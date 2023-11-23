import json
import logging

import requests

from core.utils.translate import translate
from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    urls = [
        "https://www.cbb.gov.bh/cbbapi/CBBRegister.php?finder=rgstr;catid=401,sbcatid=341,insid=ALL",
        "https://www.cbb.gov.bh/cbbapi/CBBRegister.php?finder=rgstr;catid=401,sbcatid=343,insid=ALL",
        "https://www.cbb.gov.bh/cbbapi/CBBRegister.php?finder=rgstr;catid=402,sbcatid=345,insid=ALL",
        "https://www.cbb.gov.bh/cbbapi/CBBRegister.php?finder=rgstr;catid=402,sbcatid=346,insid=ALL",
        "https://www.cbb.gov.bh/cbbapi/CBBRegister.php?finder=rgstr;catid=403,sbcatid=349,insid=ALL",
        "https://www.cbb.gov.bh/cbbapi/CBBRegister.php?finder=rgstr;catid=403,sbcatid=350,insid=ALL",
        "https://www.cbb.gov.bh/cbbapi/CBBRegister.php?finder=rgstr;catid=403,sbcatid=351,insid=ALL",
        "https://www.cbb.gov.bh/cbbapi/CBBRegister.php?finder=rgstr;catid=403,sbcatid=352,insid=ALL",
        "https://www.cbb.gov.bh/cbbapi/CBBRegister.php?finder=rgstr;catid=403,sbcatid=353,insid=ALL"
    ]

    for url in urls:
        response = requests.get(url)

        if response.status_code == 200:
            data = json.loads(response.text)

            for item in data.get('items', []):
                institution_name = item.get('Institutionname', '')
                country_of_inc = item.get('Countryofinc', '') or ''
                date_of_establish = item.get('Dateofestablish', '') or ''
                telephone = item.get('Telephone', '') or ''
                fax = item.get('Fax', '') or ''
                address = item.get('Address', '') or ''
                link = item.get('Website') or ''
                link = '' if '@' in link else link

                try:
                    data_unit = BaseDataUnit(
                        type='white_list',
                        source='https://www.cbb.gov.bh/licensing-directory/#register',
                        name=institution_name,
                        country=translate(country_of_inc).capitalize(),
                        date_publish=translate(date_of_establish).capitalize(),
                        organizational_and_legal_form=translate(address).capitalize(),
                        phones=telephone,
                        fax=fax,
                        link=link
                    )
                    yield data_unit.model_dump_json()
                except Exception as e:
                    logging.error(e)
                    logging.error(f"Error while atempt to transform following row")
        else:
            logging.error(f"Ошибка при выполнении запроса по URL: {url}")
