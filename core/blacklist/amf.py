import io
import logging

import requests
from bs4 import BeautifulSoup
from googletrans import Translator

import PyPDF2
from urlextract import URLExtract

from models import BaseDataUnit
import datefinder

site_link = 'https://www.amf-france.org'
source = 'https://www.amf-france.org/fr/espace-epargnants/proteger-son-epargne/listes-noires-et-mises-en-garde'

extractor = URLExtract()


def read_categories():
    pdfs_list = []
    translator = Translator()

    response = requests.get(
        f'{source}?page=0')

    response.encoding = 'utf-8'
    bs = BeautifulSoup(response.text, "lxml")

    modal = bs.find('div', {'id': 'popin-download'})
    all_pdf_links = modal.find_all('li')

    for li in all_pdf_links:
        pdf_content = io.BytesIO(requests.get(site_link + li.find('a')['href']).content)
        pdf_reader = PyPDF2.PdfReader(pdf_content)

        list_of_sites = []
        for page in pdf_reader.pages:
            page_data = page.extract_text().split('\n')
            for d in page_data:
                if 'la liste' in d.lower() or 'amf-france.org' in d or ' of ' in d or 'le site internet' in d or "d'inscription" in d:
                    continue
                try:
                    date = [x for x in datefinder.find_dates(d, source=True)][0][1]
                except:
                    date = ''
                d = d.replace(date, '')
                list_of_sites.append({'date': date.strip(), 'url': d.replace(' / ', '&&&').replace(' ', '').strip()})

        pdfs_list.append({
            'all_sites': list_of_sites.copy(),
            'category_title': translator.translate(li.text.strip(), dest='ru').text
        })
        list_of_sites = None

    return pdfs_list


def data_unit_iterator() -> BaseDataUnit:
    list_of_categories_from_pdf = read_categories()

    translator = Translator()
    index = 0
    end = False
    while not end:
        response = requests.get(
            f'{source}?page={index}')

        response.encoding = 'utf-8'
        bs = BeautifulSoup(response.text, "lxml")
        h2 = bs.find_all('h2')
        td = bs.find_all('td', attrs={'data-mobile': 'Catégorie'})

        if len(td) == 0:
            end = True
            continue
        # print(f"page {index} is processing...")
        index += 1

        date = bs.find_all('div', 'date')
        h2_text = []
        td_text = []
        date_text = []
        for i in h2:
            h2_text.append(i.text)
        for i in td:
            try:
                td_text.append(translator.translate(i.find('span', 'tag').text, dest='ru').text)
            except:
                td_text.append(i.find('span', 'tag').text)
        for i in date:
            try:
                date_text.append(translator.translate(i.text, dest='ru').text)
            except:
                date_text.append(i.text)

        for i in range(len(h2_text)):
            s_name = h2_text[i].strip()
            name = ''
            _url = ''
            if ' / ' in s_name:
                name = s_name.split(' / ')[1]
                _url = s_name.split(' / ')[0]
            else:
                if extractor.find_urls(s_name):
                    name = _url = s_name
                else:
                    name = s_name
            cbr_signs_of_illegal_activity = ''
            if _url != '':
                for _index, category_object in enumerate(list_of_categories_from_pdf):
                    for site_data in category_object['all_sites']:
                        if _url in site_data['url'] or site_data['url'] in _url:
                            cbr_signs_of_illegal_activity = category_object['category_title']
                            list_of_categories_from_pdf[_index]['all_sites'].remove(site_data)
                            break
            try:
                data_unit = BaseDataUnit(
                    type='black_list',
                    source=source,
                    country='Франция',
                    name=name,
                    email=name if '@' in name else '',
                    links=[_url] if _url != '' else [],
                    remarks=td_text[i],
                    date_publish=date_text[i],
                    cbr_signs_of_illegal_activity=cbr_signs_of_illegal_activity
                )
                yield data_unit.model_dump_json()
            except Exception as e:
                logging.error(e)
                logging.error(f"Error while atempt to transform following row")
    for category_object in list_of_categories_from_pdf:
        cbr_signs_of_illegal_activity = category_object['category_title']
        for site_data in category_object['all_sites']:
            url = site_data['url']
            if '%%%' in url:
                name = site_data['url'].split('%%%')[1]
                url = site_data['url'].split('%%%')[0]
            else:
                name = site_data['url']
            try:
                data_unit = BaseDataUnit(
                    type='black_list',
                    source=source,
                    country='Франция',
                    name=name,
                    date_publish=site_data['date'],
                    email=url if '@' in url else '',
                    links=[url] if '@' not in url else [],
                    cbr_signs_of_illegal_activity=cbr_signs_of_illegal_activity
                )
                yield data_unit.model_dump_json()
            except Exception as e:
                logging.error(e)
                logging.error(f"Error while atempt to transform following row")
