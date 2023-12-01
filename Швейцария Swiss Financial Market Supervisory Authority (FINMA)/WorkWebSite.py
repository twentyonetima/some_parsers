import time
from googletrans import Translator, constants
from pprint import pprint
import re
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


def change_using(driver, element_name, ):
    """
    Метод перехода по ссылкам
    :param element_name: имя селектора
    :param driver:
    :return:
    """

    find_elements = driver.find_elements(By.CSS_SELECTOR, element_name)

    return find_elements


def click_button(driver, name_button, times=None):
    """
    Метод клика по кнопке
    :param name_button: имя кнопки
    :param times: время паузы
    :param driver: ссылка для клика
    :return: 
    """""
    button = None

    if name_button:
        time.sleep(times)
        button = driver.find_element(By.CSS_SELECTOR, name_button)
    print('Click')
    button.click()


def test(url, driver, type_list):
    """
    Функция тестирования парсинга  и запуска парсера
    :param drivers:
    :return:
    """
    translator = Translator()
    read_files = []
    json_dictionary = {}
    key = []
    value = []
    all_dictonary = []
    data_published_list = []
    page_number = 0
    count_organization = 0

    # click_button(driver, ".cookie-btn", 3)
    time.sleep(5)
    while page_number < 1:
        list_data = change_using(driver, ".text-link-std ")
        time.sleep(5)

        for i in list_data:
            read_files.append(i.get_attribute("href"))
        for j in read_files:
            driver.get(j)
            count_organization += 1
            print("Number organization", count_organization)
            value_items = driver.find_elements(By.CSS_SELECTOR, 'td')
            key_items = driver.find_elements(By.CSS_SELECTOR, 'th')

            for k in range(len(key_items)):
                if key_items[k].text == "Name":
                    key.append("name")
                    value.append(value_items[k].text)

                elif key_items[k].text == "Internet":
                    key.append("social_networks")
                    value.append(value_items[k].text)

                elif key_items[k].text == "Address":
                    key.append("legal_entity_address")
                    translation = translator.translate(value_items[k].text, dest='ru')
                    value.append(translation.text)

                elif key_items[k].text == "Commercial register":
                    key.append(key_items[k].text)
                    translation = translator.translate(value_items[k].text, dest='ru')
                    value.append(translation.text)

                elif key_items[k].text == "Remarks":
                    key.append(key_items[k].text)
                    if value_items[k].text == "-":
                        value.append("")
                    else:
                        value.append(value_items[k].text)
                elif key_items[k].text == "Domicile":
                    key.append(key_items[k].text)
                    if value_items[k].text == "-":
                        value.append("")
                    else:
                        value.append(value_items[k].text)

                else:
                    key.append(key_items[k].text)
                    value.append(value_items[k].text)

        count = 0
        # print("Len Key", len(key))
        # print("Len Value", len(value))
        chek = len(key)

        for s in range(len(key)):
            if count != 6:
                count += 1
                json_dictionary[key[s]] = value[s]
            else:
                json_dictionary['type'] = type_list
                json_dictionary['Country'] = 'Switzerland'
                all_dictonary.append(json_dictionary)
                json_dictionary = {}
                count = 0
        if count_organization >= 10:
            break
        page_number += 1

    return all_dictonary
