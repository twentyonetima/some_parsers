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
url = "https://www.sec.gov.ph/investors-education-and-information/advisories/#gsc.tab=0"
driver.get(url)
# endregion

test = WorkWebSite.parsing(url, driver, "black_list")
save = SaveHdd.save_json(test)



