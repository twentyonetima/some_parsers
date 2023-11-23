import logging

import requests

from core.utils.translate import translate
from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    for page_num in range(1, 11):
        url = (f"https://www.bot.or.th/content/bot/en/involve-party-open/"
               f"jcr:content/root/container/involvepartyopenlist.InvolvePar"
               f"tyOpenListingResultsNonBank.10.p{page_num}.ascending.license0.status0.sk0.json")
        response = requests.get(url)
        data = response.json()
        results = data['results']

        for item in results:
            try:
                data_unit = BaseDataUnit(
                    type='white_list',
                    name=item['orgName'],
                    phones=item.get('tel', '').replace('n/a', ''),
                    organizational_and_legal_form=translate(item.get('addressThai', '').replace('n/a', '')),
                    link=item.get('webUrl', '').replace('n/a', ''),
                    source='bot.or.th',
                    country='Тайланд'
                )
                yield data_unit.model_dump_json()
            except Exception as e:
                logging.error(e)
                logging.error(f"Error while atempt to transform following row")
