from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from time import sleep
from imap_tools import MailBox, AND
import re, threading, random, string, requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager



def generate_random_string():
    length = random.randint(6, 10)
    letters = string.ascii_letters + string.digits  # Tập hợp các chữ cái và chữ số
    first_letter = random.choice(string.ascii_letters)  # Chọn chữ cái đầu tiên
    other_letters = ''.join(random.choices(letters, k=length-1))
    return first_letter + other_letters

def readCodeOutLook(email, password):
    with MailBox('outlook.office365.com').login(email, password) as mailbox:
        for msg in mailbox.fetch():
            if msg.subject == 'Snapchat Login Verification Code':
                data = msg.html.split('\n')
                code = data[31].strip()
                print(code)
                return code
        return None

user_agents = open('./data/user-agents.txt').read().splitlines()
# ua = open('user_agant.txt', 'w')

file = open('data/name.txt', 'r', encoding='utf-8')
lines = file.readlines()

#lấy danh sách outlook và phân chia cho 2 trình duyệt cùng chạy
outlooks = open('data/100out.txt').read().splitlines()

registered = open('reg.txt', 'a', encoding='utf-8')

# get proxy

def get_random_line():
    global lines
    random_line = random.choice(lines)
    return random_line.strip()

def get_proxys(n):
    url = f"https://tq.lunaproxy.com/getflowip?neek=1329474&num={n}&type=1&sep=1&regions=sa&ip_si=2&level=1&sb="
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the response data
        prxs = response.text.split('\n')
        return prxs
    else:
        print(f"Request failed with status code: {response.status_code}")
        return []


def main(n, distant):
    global user_agents, outlooks
    index = n * distant
    while index < index + distant:
        print(f"Thread {n}:{index} is running")
        # Configure Chrome options to use the proxy
        try:
            proxy = get_proxys(1)[0]
        except:
            sleep(10)
            continue
        print(proxy)

        user_agent = random.choice(user_agents)
        # print(user_agent)
        # break
        options = Options()
        options.add_argument(f"--proxy-server={proxy}")
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--window-size=300,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--display=:1")
        options.add_argument("--log-level=3")

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options,
        )

        #running
        driver.get("https://accounts.snapchat.com/accounts/v2/signup")
        # driver.get("https://whatismyipaddress.com/")

        # print(options.arguments)
        try:
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Accept All']"))
            )
            accept_button.click()
        except Exception as e:
            print("No cookie accept button found or an error occurred:")

        sleep(7)
        first_name = driver.find_element(By.CSS_SELECTOR, "input[name=first_name]")
        name = get_random_line()
        first_name.send_keys(name)
        
        name = get_random_line()
        last_name = driver.find_element(By.CSS_SELECTOR, "input[name=last_name]")
        last_name.send_keys(name)

        user_name = driver.find_element(By.CSS_SELECTOR, "input[name=username]")
        un = generate_random_string()
        user_name.send_keys(un)
        
        email = driver.find_element(By.CSS_SELECTOR, "input[name=email]")
        mail = outlooks[index]
        email.send_keys(mail.split('|')[0])
        print(f"Đăng đăng ký cho mail {mail.split('|')[0]} index: {index}")
        pw = driver.find_element(By.CSS_SELECTOR, "input[name=password]")
        pw.send_keys(mail.split('|')[1])

        month = driver.find_element(By.CSS_SELECTOR, "select[name=birthday_month]")
        select = Select(month)
        ran_month = random.randint(1, 12)
        select.select_by_value(str(ran_month))

        day = driver.find_element(By.CSS_SELECTOR, "input[name=birthday_day]")
        day.send_keys(random.randint(1, 28))

        year = driver.find_element(By.CSS_SELECTOR, "input[name=birthday_year]")
        year.send_keys(random.randint(1980, 2004))

        print(driver.current_url)

        submit = driver.find_element(By.CSS_SELECTOR, "button")
        submit.click()
        sleep(20)
        prefix = "https://accounts.snapchat.com/accounts/v2/signup/email_verification"
        
        res = submit_data(driver, n, distant, un, mail, prefix)
        if res == "Đăng ký thành công":
            index += 1
        elif res == "Chưa có mail":
            pass
        elif res == "Tên đã đăng ký":
            un = generate_random_string()
            user_name.send_keys(un)
            submit_data(driver, n, distant, un, mail, prefix)
        elif res == "Email đã đăng ký":
            n += 1
            pass
        elif res == "Proxy dính check capcha":
            pass
        driver.quit()
        # break
        # sleep(noo // distant + distant)

def submit_data(driver, n, distant, un, mail, prefix):
    global registered
    if driver.current_url.startswith(prefix):
            print("Nhập mã xác minh")
            code = readCodeOutLook(mail.split('|')[0], mail.split('|')[1])
            # print(code)
            if code:
                ip_code = driver.find_element(By.CSS_SELECTOR, "input[name=code]")
                ip_code.send_keys(code)
                submit = driver.find_element(By.CSS_SELECTOR, "button")
                submit.click()      
                registered.write(f'{un}|{mail.split('|')[1]}|{mail}\n')
                registered.flush()
                print("Đăng ký thành công, chuyển sang mail tiếp theo")
                return "Đăng ký thành công"
                
            else:
                print("Chưa có mail, thử chạy lại")
                return "Chưa có mail"
    else:
        sleep(5)
        if driver.page_source.find("Username is already taken") != -1:
            print(f"Tên {un} đã đăng ký, đang tạo lại username")
            return "Tên đã đăng ký"
        elif driver.page_source.find("Email address is already taken") != -1:
            print(f"Email {mail} đã đăng ký")
            return "Email đã đăng ký"
            # n += 1
        else:
            print(f"Proxy {n % distant} dính check capcha, đổi ip mới")
            return "Proxy dính check capcha"
        


n = len(outlooks)
notheads = int(input("Enter thread: "))
print("Total accounts: ", n)

dis = n // notheads

for i in range(notheads):
    threading.Thread(target=main, args=(i, dis)).start()
    sleep(2)
