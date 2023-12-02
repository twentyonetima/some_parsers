import csv
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    service = Service(driver='/chromedriver/')
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": "/"}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://edesk.apps.cssf.lu/search-entities/search?&st=advanced&entType=IF")
    button = driver.find_element("xpath", "//button[contains( text(), 'Export as CSV')]")
    button.find_element(By.TAG_NAME, "a").get_attribute("download")

    text = []
    with open("filee.csv", encoding='utf-8') as r_file:
        # Создаем объект reader, указываем символ-разделитель ","
        file_reader = csv.reader(r_file, delimiter=",")
        # Счетчик для подсчета количества строк и вывода заголовков столбцов
        count = 0
        # Считывание данных из CSV файла
        for row in file_reader:
            if count == 0:
                # Вывод строки, содержащей заголовки для столбцов
                print(f'Файл содержит столбцы: {", ".join(row)}')
            else:
                # Вывод строк
                text.append({'name': f'{row[2]}', 'legal_enity_address': f'{row[3]}'})
            count += 1
        print(f'Всего в файле {count} строк.')
    print(text)
    with open('file.json', 'w') as f:
        json.dump(text, f)
