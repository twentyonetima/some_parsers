from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import SaveHdd
import WorkWebSite

# поключаем driver
# region parametr Brauser
chrome_options = Options()
# chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--headless=new")  # for Chrome >= 109
# chrome_options.add_argument("--headless")
# chrome_options.headless = True # also works
driver = webdriver.Chrome()  # режим браузера:  options true безгаловый
url = "https://www.finanssivalvonta.fi/en/registers/warning-lists/warnings-concerning-unauthorised-service-providers/"
driver.get(url)
# endregion

# coike_file = WorkWebSite.click_button(driver, ".cookie-btn", 3)
# time.sleep(3)
test = WorkWebSite.test(url, driver, "black_list")
save = SaveHdd.save_json(test)



