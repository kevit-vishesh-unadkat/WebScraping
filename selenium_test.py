from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# This automatically downloads and matches the driver version to your browser version
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.get("https://google.com")
print(driver.title)
driver.quit()