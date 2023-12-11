import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
# import SaveHdd


def get_dynamic_page_content(url):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)
    content = driver.page_source
    driver.quit()
    return content


def test(url, type_list):
    all_dictionary = []
    page_number = 1

    while page_number < 80:
        url_with_page = f"{url}?page={page_number}"
        content = get_dynamic_page_content(url_with_page)
        soup = BeautifulSoup(content, 'html.parser')

        list_data = soup.select(".mas-search-card")
        print()
        for item in list_data:
            print(item)
            key = []
            value = []

            data = item.select_one(".mas-ancillaries")
            name = item.select_one(".ola-field-button")

            if data:
                key.append('date_publish')
                value.append(data.get_text(strip=True).split(":")[1])

            items = name.get_text(strip=True)
            pattern = r"(?:https?:\/\/|ftps?:\/\/|www\.)(?:(?![.,?!;:()]*(?:\s|$))[^\s]){2,}"
            url2 = re.findall(pattern, items)

            if url2:
                key.append("name")
                value.append(url2[0])
                key.append("links")
                value.append([url2[0], ])
            else:
                key.append('name')
                value.append(name.get_text(strip=True))

            dynamic_data = item.select_one('.masx-toggle-content')
            if dynamic_data:
                for content_item in dynamic_data.select('.masx-toggle-content__item'):
                    show_title = content_item.select_one('h4')
                    show_p = content_item.select_one('p')
                    if show_title and show_p:
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

            json_dictionary = dict(zip(key, value))
            json_dictionary['type'] = type_list
            json_dictionary['source'] = url
            json_dictionary['Country'] = 'Singapore'
            print(json_dictionary)
            all_dictionary.append(json_dictionary)

        page_number += 1
        print("Page number", page_number)

    return all_dictionary  #Result of parsing


if __name__ == "__main__":
    url = "https://www.mas.gov.sg/investor-alert-list"
    type_list = "black_list"

    driver = webdriver.Chrome()
    test_data = test(url, type_list)
    # SaveHdd.save_json(test_data) # Save to json file
    driver.quit()
