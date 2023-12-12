import time
from selenium.webdriver.support import expected_conditions as EC


from googletrans import Translator
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
import re

from selenium.webdriver.support.wait import WebDriverWait


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
    Функция тестирования парсинга
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

    click_button(driver, ".coi-banner__accept", 3)
    time.sleep(3)

    odd = change_using(driver, ".odd")
    even = change_using(driver, ".even")
    all_list = odd + even
    all_date = []
    count_data = 0

    while page_number < 21:
        time.sleep(3)
        for i in range(len(all_list)):
            # Re-find the elements inside the loop
            all_list = change_using(driver, ".odd") + change_using(driver, ".even")

            for j in range(3):
                all_date.append(all_list[i].find_elements(By.CSS_SELECTOR, "td")[j].text)
        print(all_date)
        for k in range(len(all_date)):

            if count_data == 0:
                key.append("date_publish")
                value.append(all_date[k])
                count_data += 1

            elif count_data == 1:
                items = all_date[k]
                pattern = r"(?:https?:\/\/|ftps?:\/\/|www\.)(?:(?![.,?!;:()]*(?:\s|$))[^\s]){2,}"
                url = re.findall(pattern, items)
                items2 = all_date[k].split(" ")
                count_data += 1
                if len(items2) == 2:
                    print(items2)
                    key.append("name")
                    value.append(items2[0].replace("\"", " "))
                    key.append("links")
                    if len(url) == 0:
                        value.append([remove_parentheses(items2[1]), ])
                    else:
                        value.append([url[0], ])
                else:
                    if url:
                        print(url)
                        key.append("name")
                        value.append(url[0])
                        key.append("links")
                        value.append([url[0], ])
                    else:
                        key.append("name")
                        text = all_date[k].replace("\"", "")
                        value.append(text)

            elif count_data == 2:
                key.append("remarks")
                translation = translator.translate(all_date[k], dest='ru')
                value.append(translation.text)
                count_data = 0

        count = 0
        print(len(key))
        print(len(value))
        chek = len(key)

        for s in range(len(key)):

            if count != 3:
                count += 1
                json_dictionary[key[s]] = value[s]
                print()

                if count == 3:
                    json_dictionary['type'] = type_list
                    json_dictionary['Country'] = 'Finland'
                    print(json_dictionary)
                    all_dictonary.append(json_dictionary)
                    json_dictionary = {}
                    count = 0
        key.clear()
        value.clear()
        all_date.clear()
            # Clicking the "Next" button
        next_button_selector = ".pagination .next a"
        click_button(driver, next_button_selector, 3)

        # Wait for the new page to load
        try:
            WebDriverWait(driver, 10).until(
                EC.url_changes(url)
            )
        except TimeoutException:
            print("Timed out waiting for page to load")

        # Increment the page number
        page_number += 1
        print("Page number", page_number)

    return all_dictonary


def remove_parentheses(input_string):
    # Remove "(" and ")"
    cleaned_string = input_string.replace("(", "").replace(")", "")
    return cleaned_string
