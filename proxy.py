import time
from threading import Thread
import pyautogui
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

# 170.106.104.242:12233:user-khoi01-region-sa-sessid-aeglnwcyq7g27m5mt7-sesstime-2:khoi01
hostname = "170.106.104.242"
port = "12233"
proxy_username = "user-khoi01-region-sa-sessid-aeglnwcyq7g27m5mt7-sesstime-2"
proxy_password = "khoi01"

chrome_options = Options()
chrome_options.add_argument('--proxy-server={}'.format(hostname + ":" + port))
driver = webdriver.Chrome(options=chrome_options)


def enter_proxy_auth(proxy_username, proxy_password):
    time.sleep(1)
    pyautogui.typewrite(proxy_username)
    pyautogui.press('tab')
    pyautogui.typewrite(proxy_password)
    pyautogui.press('enter')


def open_a_page(driver, url):
    driver.get(url)

    time.sleep(40)
    driver.quit()

while 1:
    a = Thread(target=open_a_page, args=(driver, "https://accounts.snapchat.com/accounts/v2/signup"))
    b = Thread(target=enter_proxy_auth, args=(proxy_username, proxy_password))
    
    a.start()
    b.start() 
    a.join()
    b.join()

