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
    read_files = []
    json_dictionary = {}
    key = []
    value = []
    all_dictonary = []
    other_list = []
    page_number = 0
    time.sleep(5)
    button = driver.execute_script(" return document.querySelector('#MainContent_ucComfirmButton_btnSure')")
    button.click()
    time.sleep(10)
    # 12234 общее количество компаний
    while page_number < 12234:
        list_data = change_using(driver, "#MainContent_ucAlertList_rptAlert_lbtnMore_" + str(page_number))
        list_data[0].click()
        time.sleep(5)
        data_key = driver.find_elements(By.CSS_SELECTOR, ".register p label")
        data_value = driver.find_elements(By.CSS_SELECTOR, ".register p font")
        for i in range(len(data_key)):
            translators_key = translator.translate(data_key[i].text, dest="ru")
            translators_value = translator.translate(data_value[i].text, dest="ru")
            if translators_key.text == "Выдавшая организация:":
                key.append('organizational_and_legal_forms')
                value.append(translators_value.text)
            elif translators_key.text == "Дата выпуска:":
                key.append('date_publish')
                value.append(translators_value.text)
            elif translators_key.text == "Регион/Страна:":
                value.append(translators_value.text)
                key.append('addresses_of_exchange_offices')
            elif translators_key.text == "Участвующие организация/люди:":
                value.append(data_value[i].text)
                key.append('name')
            elif translators_key.text == "Соответствующая информация (информация для примечаний):":
                key.append('remarks')
                remarks_split = translators_value.text.split('\n')
                value.append(remarks_split[0])
            elif translators_key.text == "Другие:":
                key.append('other')
                value.append(translators_value.text)
            if i == 4:
                split_list = translators_value.text.split(":")
                split_list_2 = []
                for j in split_list:
                    items = j.replace("\n", " ")
                    split_list_2.append(items.split(" "))
                string = ''
                count = 0

                while count != len(split_list_2):
                    match count:
                        case 1:
                            key.append('name')
                        case 2:
                            key.append('organizational_and_legal_form')
                            for j in range(len(split_list_2[count])):
                                items = split_list_2[count][j]
                                if items != "Адрес":
                                    string += items + " "
                            value.append(string)
                            string = ""
                        case 3:
                            if len(split_list_2) == 8:
                                key.append("number")
                                for j in range(len(split_list_2[count])):
                                    items = split_list_2[count][j]
                                    if items != "Телефон":
                                        string += items + " "
                                value.append(string)
                                string = ""
                            else:
                                key.append("email")
                                for j in range(len(split_list_2[count])):
                                    items = split_list_2[count][j]
                                    if items != "Электронная" and items != "почта":
                                        string += items + " "
                                value.append(string)
                                string = ""
                        case 4:
                            if len(split_list_2) == 8:
                                key.append("email")
                                for j in range(len(split_list_2[count])):
                                    items = split_list_2[count][j]
                                    if items != "Электронная" and items != "почта":
                                        string += items + " "
                                value.append(string)
                                string = ""
                            else:
                                key.append('social_networks')
                                for j in range(len(split_list_2[count])):
                                    items = split_list_2[count][j]
                                    if items != "Сайт":
                                        string += items + " "
                                value.append(string)
                                string = ""
                        case 5:
                            if len(split_list_2) == 8:
                                key.append('social_networks')
                                for j in range(len(split_list_2[count])):
                                    items = split_list_2[count][j]
                                    if items != "Сайт":
                                        string += items + " "
                                value.append(string)
                                string = ""
                            else:
                                for j in range(len(split_list_2[count])):
                                    items = split_list_2[count][j]
                                    if items != " ":
                                        string += items + " "
                                value.append(string)
                                string = ""
                        case 6:
                            if len(split_list_2) == 8:
                                for j in range(len(split_list_2[count])):
                                    items = split_list_2[count][j]
                                    if items != " ":
                                        string += items + " "
                                value.append(string)
                                string = ""
                    count += 1

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
        print("Page number", page_number)
        button = driver.execute_script(" return document.querySelector('#MainContent_ucSearchResultButtons_btnBack')")
        button.click()
        time.sleep(5)

    return all_dictonary
