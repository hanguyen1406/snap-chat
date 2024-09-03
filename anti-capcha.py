from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
# print(current_dir)

# Path to your unpacked extension folder
extension_folder_path = current_dir + '\\anticaptcha-plugin_v0.66'

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument(f'--load-extension={extension_folder_path}')

# Initialize the WebDriver with the options
driver = webdriver.Chrome(options=chrome_options)

# Open a webpage
driver.get('https://www.example.com')

# Your test actions go here...

time.sleep(60000)
# Close the browser
driver.quit()
