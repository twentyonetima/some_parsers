from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import SaveHdd
import WorkWebSite

# поключаем driver
# region parametr Brauser
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--remote-debugging-port=9222')
driver = webdriver.Chrome(options=chrome_options)  # режим браузера:  options true безгаловый
url = "https://www.finma.ch/en/finma-public/warning-list/"
driver.get(url)
# endregion

test = WorkWebSite.test(url, driver, "black_list")
save = SaveHdd.save_json(test)



