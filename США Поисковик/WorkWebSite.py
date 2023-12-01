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


def parsing(url, driver, type_list):
    """
    Функция тестирования  и запуска парсера
    :param drivers:
    :return:
    """
    translator = Translator()
    read_files = []
    json_dictionary = {}
    key = []
    value = []
    all_dictonary = []
    data_published_link = []
    data_links = []
    page_number = 0
    count_organization = 0
    # click_button(driver, ".cookie-btn", 3)
    time.sleep(5)
    list_data = change_using(driver, ".views-field-field-display-title ")

    for i in list_data:
        data_published_link.append(i.find_elements(By.TAG_NAME, 'a'))

    for j in range(len(data_published_link)):
        if j != 0:
            data_links.append(data_published_link[j][0].get_attribute("href"))

    while page_number < 10:       #10 для тестов
        print(data_links[page_number])
        driver.get(data_links[page_number])
        count_organization += 1
        print("Number organization", count_organization)
        value_items = driver.find_elements(By.CSS_SELECTOR, '.margin-20')
        name_organization = driver.find_element(By.CSS_SELECTOR, '.article-title')
        key.append("name")
        value.append(name_organization.text)

        for k in range(len(value_items)):
            template = value_items[k].text
            template = template.split("\n")

            for x in range(len(template)):
                items = (template[x].split(":"))

                if x != 0 and x <= 1:
                    if len(items) == 1 and len(template[x - 1].split(":")) == 1:
                        items_adress = (template[x - 1] + " " + template[x])
                        key.append("legal_entity_address")
                        translation = translator.translate(items_adress, dest='ru')
                        print(translation.text)
                        value.append(translation.text)
                    else:
                        items_adress = (template[x - 1])
                        key.append("legal_entity_address")
                        translation = translator.translate(items_adress, dest='ru')
                        print(translation.text)
                        value.append(translation.text)

                if len(items) > 1:
                    if items[0] == "Phone":
                        key.append("phones")
                        if items[1] == " None" or items[1] == "  None":
                            value.append("")
                        else:
                            value.append(items[1].strip())

                    elif items[0] == "Website":
                        key.append("links")
                        if items[1] == ' http':
                            value.append(['http' + items[2], ])
                        elif items[1] == ' https':
                            value.append(['https' + items[2], ])
                        else:
                            value.append([items[1], ])

                    elif items[0] == "Email":
                        key.append("email")
                        if items[1] == " None" or items[1] == "  None":
                            value.append("")
                        else:
                            value.append(items[1])
                    elif items[0] == "Fax":
                        key.append('fax')
                        if items[1] == " None" or items[1] == "  None":
                            value.append("")
                        else:
                            value.append(items[1])




        count = 1
        print("Len Key", len(key))
        # print("Len Value", len(value))
        # chek = len(key)

        # for keys in key:
        #     print("Key:", keys)
        # for values in value:
        #     print("Values:", values)

        for s in range(len(key)):
            if count != len(key) + 1:
                count += 1
                json_dictionary[key[s]] = value[s]
                if count == len(key) + 1:
                    json_dictionary['type'] = type_list
                    json_dictionary['source'] = \
                        'https://www.sec.gov/enforce/public-alerts/' \
                        'impersonators-genuine-firms/12-west-capital-management'
                    json_dictionary['Country'] = "United States"
                    all_dictonary.append(json_dictionary)
                    json_dictionary = {}
                    count = 0
                    value = []
                    key = []
        page_number += 1

    return all_dictonary
