import time
from googletrans import Translator, constants
from selenium.webdriver.common.by import By


def change_using(driver, element_name, ):
    """
    Метод перехода по ссылкам
    :param element_name: имя селектора
    :param driver:
    :return:
    """

    find_elements = driver.find_elements(By.CSS_SELECTOR, element_name)

    return find_elements


def test(url, driver, type_list):
    """
    Функция тестирования  парсера и дальнейщего запуска
    :param drivers:
    :return:
    """
    translator = Translator()
    json_dictionary = {}
    all_dictonary = []
    link_number = 0
    page_number = 1
    time.sleep(3)
    buttn_click = driver.find_element(By.CSS_SELECTOR, ".js-cookie-consent-all-btn")
    buttn_click.click()

    while page_number < 165:
        time.sleep(3)
        value = []
        key = []
        all_links = []
        links = change_using(driver, ".register-result__title a")

        for link in links:
            all_links.append(link.get_attribute("href"))

        for i in range(len(all_links)):
            driver.get(all_links[link_number])
            print(link_number)
            link_number += 1
            # time.sleep(1)
            data = driver.find_elements(By.CSS_SELECTOR, ".page-meta__date")
            keys = driver.find_elements(By.CSS_SELECTOR, ".label")
            values = driver.find_elements(By.CSS_SELECTOR, ".value")
            contacts_list = driver.find_elements(By.CSS_SELECTOR, ".contact-details__address li span")
            for contact in range(len(contacts_list)):
                if contact % 2 == 0:
                    if contacts_list[contact].text == "Adress:":
                        key.append('addresses_of_exchange_offices')
                    elif contacts_list[contact].text == "Place of residence:":
                        key.append('legal_entity_address')
                    else:
                        key.append(contacts_list[contact].text)
                else:
                    value.append(contacts_list[contact].text)
            if i < len(data):
                key.append("data_publish")
                value.append(data[0].text)
            for items in range(len(keys)):
                if keys[items].text == "Statutory name:":
                    key.append('name')
                    value.append(values[items].text.replace("\"", ""))
                elif keys[items].text == "Statutory seat:":
                    key.append('addresses_of_exchange_officess')
                    value.append(values[items].text.replace("\"", ""))
                elif keys[items].text == "LEI code:":
                    key.append('сbr_license_id')
                    value.append(values[items].text.replace("\"", ""))
                elif keys[items].text == "URL:":
                    key.append('social_networks')
                    value.append(values[items].text.replace("\"", ""))
                elif keys[items].text == "Disclosure":
                    key.append('remarks')
                    translates = translator.translate(values[items].text, dest="ru")
                    value.append(translates.text.replace("/", ""))
                else:
                    key.append(keys[items].text)
                    value.append(values[items].text.replace("\"", ""))

            count = 0
            # print(len(key))
            # print(len(value))
            # chek = len(key)

            for s in range(len(key)):

                if count != len(key):
                    count += 1
                    json_dictionary[key[s]] = value[s]

                    if count == len(key):
                        json_dictionary['type'] = type_list
                        json_dictionary[
                            'source'] = f"https://www.dnb.nl/en/public-register/?p={str(page_number)}&l=20"
                        all_dictonary.append(json_dictionary)
                        json_dictionary = {}
                        count = 0

        page_number += 1
        link_number = 0
        print("Page number", page_number)
        driver.get(url)
        time.sleep(3)
        count_click = 1
        while count_click != page_number:
            time.sleep(2)
            driver.execute_script("return document.querySelector('.pagination__item--next-page button').click()")
            count_click += 1

    return all_dictonary
