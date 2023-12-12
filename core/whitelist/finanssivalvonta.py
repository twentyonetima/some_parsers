import logging

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium import webdriver

from time import sleep

from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    url = 'https://www.finanssivalvonta.fi/rekisterit/esiterekisteri/'

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    driver.find_element(By.ID, "declineButton").click()
    driver.find_element(By.ID, "prospectus-search-button").click()

    list_element = None
    while not list_element:
        list_element = driver.find_elements(By.CLASS_NAME, "prospectus-list")
        sleep(2)

    for element in driver.find_elements(By.CLASS_NAME, "prospectus-row"):
        element.click()

    file_text = driver.page_source
    soup = BeautifulSoup(file_text, features='lxml')
    all_firms = soup.find_all('tbody', 'info-visible')

    for firm in all_firms:
        try:
            one_firm = firm.findNext('tr', 'prospectus-row')
            firm_name = one_firm.findNext('td')
            date = firm_name.findNext('td')
            type_1 = date.findNext('td')
            number_or_date = type_1.findNext('td')

            if len(date.text) == len(number_or_date.text):
                before_num = firm.findNext('tr', 'prospectus-info-row')
                before_num1 = before_num.findNext('table')
                before_num2 = before_num1.findNext('tbody')
                empty = before_num2.findNext('td')
                issuer = empty.findNext('td')
                number_lic = issuer.findNext('td')
            else:
                number_lic = number_or_date

            name = firm_name.text.replace('\n', ' ')
            number_lic = number_lic.text.replace('\n', ' ')
            date = date.text

            data_unit = BaseDataUnit(
                name=name,
                govkz_license=number_lic,
                date_publish=date,
                country='Финляндия',
                source=url,
                type='white_list',
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row")

    driver.quit()
