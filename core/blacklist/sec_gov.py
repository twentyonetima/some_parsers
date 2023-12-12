import logging
import time
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from models import BaseDataUnit


def change_using(soup, element_name):
    """
    Метод перехода по ссылкам
    :param element_name: имя селектора
    :param soup: BeautifulSoup object
    :return:
    """
    find_elements = soup.select(element_name)
    return find_elements


def data_unit_iterator():
    # region parameter Browser
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome()
    url = "https://www.sec.gov/enforce/public-alerts"
    driver.get(url)

    # Wait for a few seconds to let the JavaScript load the content
    time.sleep(5)

    # Get the page source after JavaScript execution
    page_source = driver.page_source

    # Close the browser
    driver.quit()
    # endregion

    # Use BeautifulSoup for parsing the page source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Call the parsing function with the URL, type_list, and soup
    type_list = 'black_list'
    translator = Translator()
    read_files = []
    json_dictionary = {}
    key = []
    value = []
    all_dictionary = []
    data_links = []
    count_organization = 0

    list_data = soup.select('.views-field-field-display-title')

    for cell in list_data:
        # Extract the link and name from each cell
        link = cell.find('a')

        # Skip this cell if there's no link
        if link is None:
            continue

        # Construct the absolute URL
        absolute_url = urljoin(url, link.get("href"))

        # Make the request using the absolute URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(absolute_url, headers=headers, timeout=20)
        time.sleep(2)
        sub_soup = BeautifulSoup(response.text, 'html.parser')


        # Find the name_organization element, handle None case
        name_organization = sub_soup.select_one('.article-title')
        if name_organization:
            key.append("name")
            value.append(name_organization.text)
        else:
            value.append("Name not found")

        value_items = sub_soup.select('.margin-20')
        for k in range(len(value_items)):
            template = value_items[k].text
            template = template.split("\n")

            for x in range(len(template)):
                template[x] = template[x].replace('\r', '').replace('\xa0', '').replace('\xa0\r', '').replace(' \\xa',
                                                                                                              '').replace(
                    '\xa0\xa0 \\xa0', '')

                items = (template[x].split(":"))

                if x != 0 and x <= 2 and len(items[0]) > 0:
                    if len(items) == 1 and len(template[x - 1].split(":")) == 1:
                        items_address = (template[x - 1] + " " + template[x])
                        key.append("legal_entity_address")
                        translation = translator.translate(items_address, dest='ru')
                        value.append(translation.text)
                    else:
                        items_address = (template[x - 1])
                        key.append("legal_entity_address")
                        translation = translator.translate(items_address, dest='ru')
                        value.append(translation.text)

                if len(items) > 1:
                    if items[0] == "Phone":
                        key.append("phones")
                        if items[1] == " None" or items[1] == "  None":
                            value.append("")
                        else:
                            value.append(items[1].strip())

                    elif items[0] == "Website":
                        key.append("links")
                        if items[1] == ' http':
                            value.append(['http:' + items[2], ])
                        elif items[1] == ' https':
                            value.append(['https:' + items[2], ])
                        else:
                            value.append([items[1], ])

                    elif items[0] == "Email":
                        key.append("email")
                        if items[1] == " None" or items[1] == "  None":
                            value.append("")
                        else:
                            value.append(items[1])
                    elif items[0] == "Fax":
                        key.append('fax')
                        if items[1] == " None" or items[1] == "  None":
                            value.append("")
                        else:
                            value.append(items[1])

        count = 1
        for s in range(len(key)):
            if count != len(key) + 1:
                count += 1
                json_dictionary[key[s]] = value[s]
                if count == len(key) + 1:
                    json_dictionary['type'] = type_list
                    json_dictionary['source'] = absolute_url
                    json_dictionary['country'] = "США"
                    try:
                        data_unit = BaseDataUnit(
                            **json_dictionary
                        )
                        yield data_unit.model_dump_json()
                    except Exception as e:
                        logging.error(e)
                        logging.error(f"Error while atempt to transform following row")

                    json_dictionary = {}
                    count = 0
                    value = []
                    key = []
        count_organization += 1
        # page_number += 1
