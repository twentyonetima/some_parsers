import time
from googletrans import Translator
from bs4 import BeautifulSoup
import requests
import SaveHdd

def get_page(url):
    """
    Function to get the HTML content of a page using requests.
    :param url: URL of the page
    :return: HTML content
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to retrieve page. Status code: {response.status_code}")

def change_using(html_content, element_name):
    """
    Method for finding elements using BeautifulSoup.
    :param html_content: HTML content of the page
    :param element_name: Name of the element to find
    :return: List of found elements
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    find_elements = soup.select(element_name)
    return find_elements

def translate_text(text, dest="ru"):
    """
    Function to translate text using Google Translate.
    :param text: Text to translate
    :param dest: Destination language (default is Russian)
    :return: Translated text or original text if translation fails
    """
    translator = Translator()

    try:
        translation = translator.translate(text, dest=dest)
        translated_text = translation.text
    except Exception as e:
        print(f"Translation error for text: {text}")
        print(f"Error message: {str(e)}")
        translated_text = text  # Use the original text in case of an error

    return translated_text

def test(url, type_list):
    """
    Function to test the parser and perform further processing using BeautifulSoup.
    :param url: URL to scrape
    :param type_list: Type list parameter
    :return: List of dictionaries
    """
    html_content = get_page(url)
    soup = BeautifulSoup(html_content, 'html.parser')

    json_dictionary = {}
    all_dictionary = []

    # Handle cookie popup if necessary

    amount = 0
    for items in soup.select("tr")[1:]:
        key = "data_publish"
        val_dat = items.select_one(".RgCol_Center").get_text(strip=True)

        key = "name"
        val_nam = items.select_one(".RgCol_Left").get_text(strip=True)
        amount += 1
        print(amount)
        print(val_nam)

        translated_name = translate_text(val_nam)
        json_dictionary = {
            "data_publish": val_dat,
            "name": translated_name,
            "type": type_list,
            "source": url,
            "Country": 'Philippines'
        }

        all_dictionary.append(json_dictionary)

    return all_dictionary


url = "https://market.sec.or.th/public/idisc/en/Viewmore/invalert-head?PublicFlag=Y"
type_list = "black_list"

result = test(url, type_list)
save = SaveHdd.save_json(result)
print(result)
