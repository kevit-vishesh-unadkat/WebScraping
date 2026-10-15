# from selenium import webdriver
#
# driver=webdriver.Chrome()
#
# driver.get("https://www.python.org")
#
# print(driver.title)
# print(driver.current_url)
#
# driver.quit()



from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

options = Options()
options.binary_location = "/usr/bin/chromium"

service = Service("/usr/bin/chromedriver")

driver = webdriver.Chrome(
    service=service,
    options=options
)

driver.get("https://www.python.org")

print("Page title:", driver.title)

driver.quit()