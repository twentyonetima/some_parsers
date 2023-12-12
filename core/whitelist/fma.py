import logging

import cloudscraper
from bs4 import BeautifulSoup

from core.utils.translate import translate
from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    scraper = cloudscraper.create_scraper()

    for page in range(1, 49):
        url = f"https://www.fma.gv.at/en/search-company-database/?cname=&place=&bic=&category=&per_page=100&submitted=1&to={page}"
        try:
            response = scraper.get(url)
        except Exception as e:
            print(f'Error while scrapping FMA: {e}')
            continue

        if response and getattr(response, 'status_code', 500) == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            companies = soup.find_all('a', {'class': 'company-details-toggle'})
            if companies:
                for company in companies:
                    try:
                        name = company.text.strip()
                        detail = company.parent.parent.find('div', {'class': 'company-details'})
                        if detail:
                            category = detail.find('strong', string='Category:').parent
                            address = detail.find('strong', string='Address:').parent
                            if category and address:
                                category_text = category.text
                                category_text = category_text.replace('Category:', '')
                                category_text = translate(category_text.strip())

                                address_text = address.text
                                address_text = address_text.replace('Address:', '').strip()
                                if address_text[0] == '|':
                                    address_text = address_text[1:]
                                address_text = translate(address_text.strip())

                                data_unit = BaseDataUnit(
                                    type='white_list',
                                    source='https://www.fma.gv.at/en/search-company-database',
                                    name=name,
                                    cbr_signs_of_illegal_activity=category_text,
                                    organizational_and_legal_form=address_text,
                                    country='Австрия'
                                )
                                yield data_unit.model_dump_json()
                    except Exception as e:
                        logging.error(e)
                        logging.error(f"Error while atempt to transform following row")
        else:
            print(f"Ошибка при выполнении запроса на странице {page}.")
