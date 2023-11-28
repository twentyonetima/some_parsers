import re
import time

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
    Функция тестирования и запуска парсера
    :param drivers:
    :return:
    """

    json_dictionary = {}
    all_dictonary = []
    page_number = 1
    time.sleep(3)
    while page_number < 1:

        value = []
        key = []
        list_data = change_using(driver, ".mas-search-card")
        button = change_using(driver, ".mas-search-card button")
        data = driver.find_elements(By.CSS_SELECTOR, ".mas-ancillaries")
        name = driver.find_elements(By.CSS_SELECTOR, ".ola-field-button")
        buttn_number = 0

        for i in range(len(list_data)):
            # print(data[i].text)
            if i < len(data):
                key.append('date_publish')
                split_data = data[i].text.split(":")
                value.append(split_data[1])
            else:
                key.append('date_publish')
                value.append("")

            items = name[i].text
            pattern = r"(?:https?:\/\/|ftps?:\/\/|www\.)(?:(?![.,?!;:()]*(?:\s|$))[^\s]){2,}"
            url2 = re.findall(pattern, items)

            if url2:
                key.append("social_networks")
                value.append(url2[0])
            else:
                key.append('name')
                value.append(name[i].text)

            button_check = list_data[i].find_elements(By.CSS_SELECTOR, "button")
            if len(button_check) != 0:
                if buttn_number <= len(button):
                    time.sleep(5)
                    button[buttn_number].click()
                    # print(buttn_number)
                    time.sleep(5)
                    buttn_number += 1
                    show_title = list_data[i].find_element(By.CSS_SELECTOR, ".masx-toggle-content h4")
                    show_p = list_data[i].find_element(By.CSS_SELECTOR, ".masx-toggle-content p")
                    if show_title.text == "Website:":
                        key.append("social_networks")
                    elif show_title.text == "Email:":
                        key.append("email")
                    elif show_title.text == "Address:":
                        key.append("legal_entity_address")
                    else:
                        key.append(show_title.text)
                    value.append(show_p.text)
                    # print("h4", show_title.text)
                    # print("p", show_p.text)

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
                        json_dictionary['source'] = url
                        all_dictonary.append(json_dictionary)
                        json_dictionary = {}
                        count = 0

        page_number += 1
        print("Page number", page_number)
        print(url + "?page=" + str(page_number))
        driver.get(url + "?page=" + str(page_number))
        time.sleep(5)

    return all_dictonary
