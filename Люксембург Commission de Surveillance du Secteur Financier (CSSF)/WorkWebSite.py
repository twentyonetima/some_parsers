import time
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import SaveHdd


def change_using(soup, element_name):
    find_elements = soup.select(element_name)
    return find_elements


def time_out(times):
    if times:
        time.sleep(times)


def click_button(soup, name_button, times=None):
    button = None
    if name_button:
        time.sleep(times)
        button = soup.select_one(name_button)
    print('Click')


def next_page(items_elements, find_element, deleted_text):
    read_files = []
    for item in items_elements:
        for items2 in item.select(find_element):
            if len(items2.text) <= 0 or items2.text == deleted_text:
                read_files.append("")
            else:
                read_files.append(items2.text)
    return read_files


def test(url, soup, type_list):
    translator = Translator()
    read_files = []
    json_dictionary = {}
    key = []
    value = []
    all_dictionary = []
    data_published_list = []
    page_number = 1

    click_button(soup, ".cookie-btn", 3)
    time.sleep(3)

    while page_number < 28:
        response = requests.get(url + "page/" + str(page_number))
        soup = BeautifulSoup(response.content, 'html.parser')
        list_data = change_using(soup, ".library-element__title")
        for i in list_data:
            href = i.select_one('a')['href']
            read_files.append(href)

        for j in read_files:
            try:
                response = requests.get(j)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching URL {j}: {e}")
                continue
            inner_soup = BeautifulSoup(response.content, 'html.parser')
            try:
                data_published = inner_soup.select_one(".single-news__date").text
            except:
                data_published = ""
            data_published_list.append(data_published)
            items = inner_soup.select('td')

            time_out(3)
            for k in range(0, len(items), 2):
                if items[k].text != "":
                    if k + 1 < len(items):
                        key_val = items[k].text
                        value_val = items[k + 1].text

                        if key_val == "Official contact details of the company":
                            key_val = items[k + 1].text
                            value_val = items[k + 2].text
                        if key_val == "Warning:":
                            key.append("Warning")
                            value.append(value_val)
                        if key_val == "Company name used:" or key_val == "Company name:" or key_val == "Name":
                            key.append("name")
                            value.append(value_val)
                        elif key_val == "Email address used:" or key_val == "Email address:"\
                                or key_val == "Email addresses used:" or key_val == "Email addresses:":
                            key.append("email")
                            value.append(value_val)
                        elif (key_val == "Phone number used:" or key_val == "Phone number:" or
                              key_val == "Phone numbers used:"):
                            key.append("phones")
                            value.append(value_val)
                        elif key_val == "Website used:" or key_val == "Website:" \
                                or key_val == "Websites:" or key_val == "Websites used:":
                            key.append("links")
                            if '\n' in value_val:
                                link_list = value_val.split('\n')
                                link_list = [link.strip() for link in link_list if link.strip()]
                            else:
                                link_list = []
                                link_list.append(value_val)
                            value.append(link_list)
                        elif key_val == "Alleged registered office:":
                            key.append("legal_entity_address")
                            value.append(value.append(value_val))
                        elif key_val == "Note:":
                            key.append("remarks")
                            try:
                                translation = translator.translate(value_val, dest='ru')
                                value.append(translation.text)
                            except Exception as e:
                                print(f"Translation failed: {e}")
                                value.append(value_val)

        mylist = [x for x in value if x is not None]
        print(len(key))
        print(len(mylist))

        count = 0

        for keys, values in zip(key, mylist):
            if keys == 'Warning':
                if json_dictionary:
                    del json_dictionary['Warning']
                    json_dictionary['type'] = type_list
                    json_dictionary['Country'] = 'Luxembourg'
                    correct_date = data_published_list[count].split('Published on ')[1]
                    json_dictionary['data published'] = correct_date
                    all_dictionary.append(json_dictionary)
                    count += 1
                    json_dictionary = {}

            json_dictionary[keys] = values

        all_dictionary.append(json_dictionary)
        count = 0
        key.clear()
        value.clear()
        mylist.clear()

        page_number += 1
        print("Page number", page_number)
        print(url + "page/" + str(page_number))
        time.sleep(3)

    return all_dictionary


if __name__ == "__main__":
    url = "https://www.cssf.lu/en/warnings/"

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        result = test(url, soup, "black_list")
        save = SaveHdd.save_json(result)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

