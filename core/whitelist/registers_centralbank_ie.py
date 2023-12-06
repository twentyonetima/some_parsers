import logging

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver

from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    url = 'https://registers.centralbank.ie/FirmSearchPage.aspx'

    service = Service(driver='/chromedriver/')

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    browser = driver
    browser.get(url)

    driver.find_element(By.ID, "ctl00_cphRegistersMasterPage_btnFirmNameSearch").click()

    previous_ref = 0
    new_ref = 1

    while not previous_ref == new_ref:
        previous_ref = new_ref

        file_text = browser.page_source
        soup = BeautifulSoup(file_text, features='lxml')
        table = soup.find('div', id='content')
        table = table.find_all('tr')
        for item in table:
            try:
                number = item.find("td", "gvwColumn")
                name = item.find("td", "entityNameColumn")
                if number and name:
                    name = name.text.replace('\n', ' ').strip()
                    number = number.text.replace('\n', ' ').strip()
                    data_unit = BaseDataUnit(
                        name=name,
                        cbr_license_id=number,
                        type='white_list',
                        source=url,
                        country='Ирландия',
                    )
                    yield data_unit.model_dump_json()
            except Exception as e:
                logging.error(e)
                logging.error(f"Error while atempt to transform following row")

        try:
            new_ref += 1
            driver.find_element(By.ID, "ctl00_cphRegistersMasterPage_gvwSearchResults_ctl18_btnNext").click()
        except Exception as e:
            print(e)
            new_ref = previous_ref
