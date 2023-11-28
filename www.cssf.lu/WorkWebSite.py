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
    data_published_list = []
    page_number = 1

    click_button(driver, ".cookie-btn", 3)
    time.sleep(3)
    while page_number < 23:
        list_data = change_using(driver, ".library-element__title")
        for i in list_data:
            read_files.append(i.find_element(By.CSS_SELECTOR, 'a').get_attribute("href"))

        for j in read_files:
            driver.get(j)
            data_published = driver.find_element(By.CSS_SELECTOR, ".single-news__date").text
            data_published_list.append(data_published)
            items = driver.find_elements(By.CSS_SELECTOR, 'td')

            for k in range(len(items)):
                if items[k].text != "":
                    if items[k].text == 'Official contact details of the company':
                        key.append("name")
                        value.append(items[k + 2].text)
                        break
                    if k % 2 == 0:
                        if items[k].text == "Company name used:" or items[k].text == "Company name:":
                            key.append("name")
                        elif items[k].text == "Email address used:" or items[k].text == "Email address:"\
                                or items[k].text == "Email addresses used:" or items[k].text == "Email addresses:":
                            key.append("email")
                        elif items[k].text == "Phone number used:" or items[k].text == "Phone number:":
                            key.append("phones")
                        elif items[k].text == "Website used:" or items[k].text == "Website:" \
                                or items[k].text == "Websites:" or items[k].text == "Websites used:":
                            key.append("social_networks")
                        elif items[k].text == "Alleged registered office:":
                            key.append("legal_entity_address")
                        else:
                            key.append(items[k].text)

                    if k % 2 != 0:
                        if items[k - 1].text == "Note:":
                            translation = translator.translate(items[k].text, dest='ru')
                            value.append(translation.text)
                        else:
                            value.append(items[k].text.replace("\n", " "))
                        # print("Value", items[k].text)

        count = 0
        print(len(key))
        print(len(value))
        chek = len(key)

        for s in range(len(key)):

            if s == 0:
                if key[s] != "Warning:":
                    json_dictionary[key[s]] = value[s]
            else:
                if key[s] != "Warning:":
                    json_dictionary[key[s]] = value[s]
                    if s == chek - 1:
                        json_dictionary['data published'] = data_published_list[count]
                        json_dictionary['type'] = type_list
                        all_dictonary.append(json_dictionary)
                        json_dictionary = {}
                        count += 1
                else:
                    key.append("type")
                    value.append(type_list)
                    json_dictionary['data published'] = data_published_list[count]
                    json_dictionary['type'] = type_list
                    all_dictonary.append(json_dictionary)
                    json_dictionary = {}
                    count += 1

        for x in all_dictonary:
            print(x.items())
        page_number += 1
        print("Page number", page_number)
        print(url + "page/" + str(page_number))
        time.sleep(3)
        driver.get(url + "page/" + str(page_number))

    return all_dictonary
