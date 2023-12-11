import time
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import SaveHdd


def change_using(soup, element_name):
    """
    Метод перехода по ссылкам
    :param element_name: имя селектора
    :param soup:
    :return:
    """
    find_elements = soup.select(element_name)
    return find_elements

def time_out(times):
    """
    Метод задержки паузы
    :param times: время задержки
    :return:
    """
    if times:
        time.sleep(times)

def parsing(url, type_list):
    """
    Функция тестирования парсинга
    :param url: URL страницы
    :param type_list: тип данных (например, "black_list")
    :return:
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    translator = Translator()
    read_files = []
    json_list = []

    page_number = 0
    count_data = 1

    while page_number < 13:
        print("Page number", page_number)
        time.sleep(10)

        button = change_using(soup, ".accordion-title")
        list_data = change_using(soup, ".accordion-content")

        for i in list_data:
            names = i.select('b') if page_number <= 3 else i.select('a')
            dates = i.select('.myDate')

            for name, date in zip(names, dates):
                data = {
                    'name': name.text,
                    'date_publish': date.text,
                    'type': type_list,
                    'social_networks': ["", ],
                    'links': ["", ],
                    'source': url
                }
                print(data)
                json_list.append(data)

        page_number += 1

    return json_list


if __name__ == '__main__':
    url = "https://www.sec.gov.ph/investors-education-and-information/advisories/#gsc.tab=0"
    test = parsing(url, "black_list")
    # save = SaveHdd.save_json(test)  # save to file
