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


def time_out(times):
    """
    Метод задержки паузы
    :param times: время задержки
    :return:
    """

    if times:
        time.sleep(times)


def parsing(url, driver, type_list):
    """
    Функция тестирования парсинга
    :param drivers:
    :return:
    """
    translator = Translator()
    read_files = []
    json_dictionary = {}
    key = []
    value = []
    name_list = []
    data_list = []
    name_list_next = []
    data_list_next = []
    all_dictonary = []
    data_published_list = []
    page_number = 0
    count_data = 1
    button = change_using(driver, ".accordion-title")
    list_data = change_using(driver, ".accordion-content")
    buton_number = 0
    buton_number_next = 0

    while page_number < 13:
        print("Button number", buton_number)
        time.sleep(10)
        if buton_number != 0:
            time.sleep(25)
            button[buton_number].click()
            time.sleep(5)

        for i in list_data:
            if buton_number > 3:
                name_list_next.append(i.find_elements(By.CSS_SELECTOR, 'a'))
                data_list_next.append(i.find_elements(By.CSS_SELECTOR, ".myDate"))
            else:
                name_list.append(i.find_elements(By.CSS_SELECTOR, 'b'))
                data_list.append(i.find_elements(By.CSS_SELECTOR, '.myDate'))

        if buton_number <= 3:
            for k in range(len(name_list[buton_number])):
                key.extend(["name", "date_publish"])
                value.extend([name_list[buton_number][k].text, data_list[buton_number][k].text])
        else:
            for x in range(len(name_list_next[buton_number_next]) - 1):
                key.extend(["name", "date_publish"])
                value.extend([name_list_next[buton_number_next][x].get_attribute("title"),
                              data_list_next[buton_number_next][x].text])

            buton_number_next += 1

        count = 0
        print("Len Key", len(key))
        print("Len Value", len(value))
        chek = len(key)

        # for keys in key:
        #     print("Key:", keys)
        # for values in value:
        #     print("Values:", values)

        for s in range(len(key)):
            if count != 2:
                count += 1
                json_dictionary[key[s]] = value[s]
            else:
                json_dictionary['type'] = type_list
                json_dictionary['social_networks'] = ["", ]
                json_dictionary['links'] = ["", ]
                json_dictionary['source'] = "https://www.sec.gov.ph/investors-education-and-information/advisories/#gsc.tab=0"
                all_dictonary.append(json_dictionary)
                json_dictionary = {}
                count = 0
        value = []
        key = []
        page_number += 1
        buton_number += 1
        count_data += 1

    return all_dictonary
