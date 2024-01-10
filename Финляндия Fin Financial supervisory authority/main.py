import time

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
url = "https://www.finanssivalvonta.fi/en/registers/warning-lists/warnings-concerning-unauthorised-service-providers/"
driver.get(url)
# endregion

# coike_file = WorkWebSite.click_button(driver, ".cookie-btn", 3)
# time.sleep(3)
test = WorkWebSite.test(url, driver, "black_list")
save = SaveHdd.save_json(test)



