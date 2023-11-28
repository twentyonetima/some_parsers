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


def next_page(items_elemts: list, find_element: str, deleted_text: str):
    """
    Функция перехода на следущую страницу и поиска необоходимых элементов в ней
    :param items_elemts:  элементы на страницк
    :param find_element:  какой элемент ищем
    :param deleted_text:  что нужно убрать их текста
    :return:
    """
    read_files = []
    for item in items_elemts:
        for items2 in item.find_elements(By.CSS_SELECTOR, find_element):
            if len(items2.text) <= 0 or items2.text == deleted_text:
                read_files.append("")
            else:
                read_files.append(items2.text)
    return read_files


def test(url, driver, type_list):
    """
    Функция тестирования  парсера и дальнейщего запуска
    :param drivers:
    :return:
    """
    translator = Translator()
    json_dictionary = {}
    key = []
    value = []
    all_dictonary = []
    page_number = 0
    time.sleep(5)
    button = driver.execute_script(" return document.querySelector('.btnCookiepopup')")
    button.click()
    time.sleep(5)
    while page_number < 1:
        list_data = change_using(driver, "tr")
        print(len(list_data))

        for items in range(len(list_data)):
            if items != 0:
                key.append("data_publish")
                val_dat = list_data[items].find_elements(By.CSS_SELECTOR, ".RgCol_Center")
                value.append(val_dat[0].text)
                key.append("name")
                val_nam = (list_data[items].find_elements(By.CSS_SELECTOR, ".RgCol_Left"))
                translate_value = translator.translate(val_nam[0].text, dest="ru")
                value.append(translate_value.text)

            count = 0
            # print(len(key))
            # print(len(value))

            for s in range(len(key)):

                if count != len(key):
                    count += 1
                    json_dictionary[key[s]] = value[s]

                    if count == len(key):
                        json_dictionary['type'] = type_list
                        json_dictionary['source'] = url
                        all_dictonary.append(json_dictionary)
                        json_dictionary = {}
                        count += 1

            page_number += 1

    return all_dictonary
