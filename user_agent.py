from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager

chromedriver_path = "chromedriver.exe"

chrome_options = webdriver.ChromeOptions()

service = Service(chromedriver_path)

driver = webdriver.Chrome(ChromeDriverManager().install(),service=service, options=chrome_options)

try:
    driver.get("https://www.example.com")
    time.sleep(5)
    print("Title:", driver.title)

    example_element = driver.find_element(By.XPATH, '//h1')

    print("Element Text:", example_element.text)
finally:
    driver.quit()
