from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time, requests, random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

mails = open("./dist/mail.txt", "r").readlines()

window_width = 220
window_height = 700

def get_proxys_free():
    try:
        url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=protocolipport&format=text&timeout=20000"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.text.split('\n')
            random_proxy = random.choice(data)
            return random_proxy.strip()
        else:
            print(f"Error fetching the proxy list: {response.status_code}")
            return None
    except requests.RequestException as err:
        print(f"Error fetching the proxy list: {err}")
        return None

options = Options()
# options.add_argument(f"--proxy-server={get_proxys_free()}")
options.add_argument(f"--window-size={window_width},{window_height}")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
print(options.arguments)
driver = webdriver.Chrome(options=options)



driver.get("https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=157&ct=1722703115&rver=7.0.6738.0&wp=MBI_SSL&wreply=https%3a%2f%2foutlook.live.com%2fowa%2f%3fnlp%3d1%26cobrandid%3dab0455a0-8d03-46b9-b18b-df2f57b9e44c%26culture%3dvi-vn%26country%3dvn%26RpsCsrfState%3d6e64d1dc-8896-37f0-65f4-934eab8651ca&id=292841&aadredir=1&CBCXT=out&lw=1&fl=dob%2cflname%2cwld&cobrandid=ab0455a0-8d03-46b9-b18b-df2f57b9e44c")
time.sleep(15)

while 1:
    try:
        # Wait up to 10 seconds until an element with a specific ID is present
        print("Đang load element")
        element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.NAME, "loginfmt"))
        )
        if element: break
        print("Page is fully loaded")
    except Exception as e:
        print(f"An error occurred")

emailInput = driver.find_element(By.NAME, "loginfmt")
emailInput.send_keys(mails[0].split("|")[0])

submitButton = driver.find_elements(By.CSS_SELECTOR, "button")
# print(submitButton)
submitButton[0].click()
time.sleep(15)

passwordInput = driver.find_element(By.NAME, "passwd")
passwordInput.send_keys(mails[0].split("|")[1])
time.sleep(3)
submitButton = driver.find_elements(By.CSS_SELECTOR, "button")
print(submitButton)
submitButton[1].click()
time.sleep(15)

#click search input
searchIcon = driver.find_element(By.XPATH, "//i[@data-icon-name='Search']")
searchIcon.click()
time.sleep(3)
code = None




print(code)


time.sleep(200)
print(driver.title)

driver.quit()
