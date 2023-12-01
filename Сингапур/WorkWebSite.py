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
    while page_number < 4:

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
                key.append("links")
                value.append([url2[0], ])
            else:
                key.append('name')
                value.append(name[i].text)
            print()
            button_check = list_data[i].find_elements(By.CSS_SELECTOR, "button")
            if len(button_check) != 0:
                if buttn_number <= len(button):
                    time.sleep(5)
                    button[buttn_number].click()
                    # print(buttn_number)
                    time.sleep(5)
                    buttn_number += 1
                    a2 = list_data[i].text
                    parent_div = list_data[i].find_element(By.CLASS_NAME, 'masx-toggle-content')
                    a1 = parent_div.text
                    content_items = parent_div.find_elements(By.CLASS_NAME, 'masx-toggle-content__item')

                    # Iterate through each content item
                    for item in content_items:
                        # Find the <h4> element within the current content item
                        show_title = item.find_element(By.TAG_NAME, 'h4')
                        a = show_title.text
                        # Find the <p> element within the current content item
                        show_p = item.find_element(By.TAG_NAME, 'p')
                        b = show_p.text
                        print(a, b)
                        if show_title.text == "Phone Number:":
                            key.append("phone")
                            value.append(show_p.text)
                        elif show_title.text == "Website:":
                            links = re.findall(r'https?://\S+|www\.\S+|http?://\.\S+', show_p.text)
                            for link in links:
                                if 'instagram' in link or 'facebook' in link or 'twitter' in link or 't.me' in link:
                                    value_list = []
                                    value_list.append(link)
                                    key.append("social_networks")
                                    value.append(value_list)
                                else:
                                    value_list = []
                                    value_list.append(link)
                                    key.append("links")
                                    value.append(value_list)
                        elif show_title.text == "Email:":
                            key.append("email")
                            value.append(show_p.text)
                        elif show_title.text == "Address:":
                            key.append("legal_entity_address")
                            if "\n" in show_p.text:
                                address = show_p.text.replace("\n", ' ')
                                value.append(address)
                            else:
                                value.append(show_p.text)
                        else:
                            key.append(show_title.text)
                            value.append(show_p.text)
                    if "phone" not in key:
                        key.append("phone")
                        value.append("")
                    if "email" not in key:
                        key.append("email")
                        value.append("")
                    if "legal_entity_address" not in key:
                        key.append("legal_entity_address")
                        value.append("")
                    # show_title = list_data[i].find_element(By.CSS_SELECTOR, ".masx-toggle-content h4")
                    # show_p = list_data[i].find_element(By.CSS_SELECTOR, ".masx-toggle-content p")
                    # for element in elements:
                    #     show_title = element.find_elements(By.TAG_NAME,'h4')
                    #     show_p = element.find_elements(By.TAG_NAME,'p')
                    #     if show_title.text == "Phone Number:":
                    #         key.append("phone")
                    #         value.append(show_p.text)
                    #     elif show_title.text == "Website:":
                    #         key.append("links")
                    #         value.append([show_p.text, ])
                    #     elif show_title.text == "Email:":
                    #         key.append("email")
                    #         value.append(show_p.text)
                    #     elif show_title.text == "Address:":
                    #         key.append("legal_entity_address")
                    #         if "\n" in show_p.text:
                    #             address = show_p.text.replace("\n", ' ')
                    #             value.append(address)
                    #         else:
                    #             value.append(show_p.text)
                    #     else:
                    #         key.append(show_title.text)
                    #         value.append(show_p.text)
                    #     print("h4", show_title.text)
                    #     print("p", show_p.text)

            count = 0
            print(len(key))
            print(len(value))
            chek = len(key)

            for s in range(len(key)):

                if count != len(key):
                    count += 1
                    val_key = key[s]
                    val_val = value[s]
                    print(val_key, val_val)
                    json_dictionary[key[s]] = value[s]

                    if count == len(key):
                        json_dictionary['type'] = type_list
                        json_dictionary['source'] = url
                        json_dictionary['Country'] = 'Singapore'
                        all_dictonary.append(json_dictionary)
                        json_dictionary = {}
                        count = 0
                        key.clear()
                        value.clear()
        page_number += 1
        print("Page number", page_number)
        print(url + "?page=" + str(page_number))
        driver.get(url + "?page=" + str(page_number))
        time.sleep(5)

    return all_dictonary
