from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from time import sleep
import re, threading, random, string, requests, imaplib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox
from PyQt6 import QtTest
import sys, os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import poplib, email
from email.header import decode_header
from pathlib import Path
import subprocess, platform, signal  # <-- thêm

# ========= Helper: luôn trỏ tới thư mục chứa file .py khi dev, và thư mục chứa .exe khi build =========
def resource_path(relative_path: str) -> str:
    """
    Trả về đường dẫn tới resource nằm cạnh file .py (dev) hoặc cạnh .exe (PyInstaller --onefile).
    -> Không lấy từ _MEIPASS, để anh chỉ cần copy file phụ cạnh .exe là chạy.
    """
    if getattr(sys, 'frozen', False):  # chạy .exe
        base_dir = os.path.dirname(sys.executable)
    else:  # chạy .py
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)

outlooks = []
names = open("./name.txt", encoding='utf-8').readlines()
user_names = open("./username.txt", encoding='utf-8').readlines()
passwords = open("./passwords.txt", encoding='utf-8').readlines()
nothreads = 0
stop_event = threading.Event()
# ====== Các file phụ lấy từ cùng thư mục với script/exe ======
user_agents_path = resource_path('user-agents.txt')
registered_path  = resource_path('reg_success.txt')
mail_used_path   = resource_path('mail_used.txt')
reg_fail_path    = resource_path('reg_fail.txt')
proxy_file_path  = resource_path('proxy.txt')

# Đọc & mở file
user_agents = open(user_agents_path, encoding='utf-8').read().splitlines()
registered = open(registered_path, 'a', encoding='utf-8')
mail_used  = open(mail_used_path, 'a', encoding='utf-8')
reg_fail   = open(reg_fail_path, 'a', encoding='utf-8')  # 'a' an toàn hơn khi chạy nhiều lần

# Kích thước và khoảng cách giữa các cửa sổ
gap = 0
window_width = 220
window_height = 700
end_thread = []

class HotMail:
    def __init__(self, email_address, password, protocol="imap"):
        self.email = email_address
        self.password = password
        self.protocol = protocol.lower()
        
        if self.protocol == "imap":
            self.server = "outlook.office365.com"
            self.port = 993
            if "gmail.com" in self.email:
                self.server = "imap.gmail.com"
            self.mail = imaplib.IMAP4_SSL(self.server, self.port)
            self.mail.login(self.email, self.password)
        elif self.protocol == "pop3":
            self.server = "outlook.office365.com"
            self.port = 995
            if "gmail.com" in self.email:
                self.server = "pop.gmail.com"
            self.mail = poplib.POP3_SSL(self.server, self.port)
            self.mail.user(self.email)
            self.mail.pass_(self.password)
        else:
            raise ValueError("Protocol must be either 'imap' or 'pop3'")

    def load_imap(self):
        self.mail.select("inbox")
        result, data = self.mail.search(None, "ALL")
        email_ids = data[0].split()[-6:][::-1]  # lấy 6 email gần nhất
        for email_id in email_ids:
            result, msg_data = self.mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
            
            if "Snapchat Login Verification" in subject:
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                else:
                   body = msg.get_payload(decode=True).decode()
                code = body.split('\n')[36].strip()
                return code
        return None        

    def load(self):
        return self.load_imap()
        

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(802, 624)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 10, 71, 61))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(100, 10, 71, 61))
        self.pushButton_2.setObjectName("pushButton_2")
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(500, 60, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(500, 10, 91, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.pushButton_4 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(690, 10, 93, 61))
        self.pushButton_4.setObjectName("pushButton_4")
        self.tableWidget = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 80, 781, 481))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.label_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(500, 35, 101, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.pushButton_5 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(190, 40, 81, 35))
        self.pushButton_5.setObjectName("pushButton_5")
        self.lineEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(270, 40, 211, 34))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(270, 10, 211, 34))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.pushButton_6 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_6.setGeometry(QtCore.QRect(190, 10, 81, 35))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton.raise_()
        self.pushButton_2.raise_()
        self.label.raise_()
        self.label_2.raise_()
        self.pushButton_4.raise_()
        self.label_3.raise_()
        self.pushButton_5.raise_()
        self.lineEdit.raise_()
        self.lineEdit_2.raise_()
        self.pushButton_6.raise_()
        self.tableWidget.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 802, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # --- runtime state ---
        self.running = False
        self.stop_event = threading.Event()
        self.threads = []
        self.drivers = []
        self.drivers_lock = threading.Lock()
        self._pids = set()  # <-- lưu PID chromedriver để kill theo PID

        # kết nối nút Bắt đầu <-> Dừng lại
        try:
            self.pushButton_4.clicked.disconnect()
        except Exception:
            pass
        self.pushButton_4.clicked.connect(self.toggle_run)

    def get_random_ten(self):
        global names
        random_line = random.choice(names)
        return random_line.strip()

    def get_random_ho(self):
        global names
        random_line = random.choice(names)
        return random_line.strip()
    
    def get_proxys(self, n, url):
        atr = url.split('&')
        atr[1] = 'num=' + str(n)
        link = '&'.join(atr)
        response = requests.get(link)
        if response.status_code == 200:
            prxs = response.text.split('\n')
            return prxs
        else:
            print(f"Request failed with status code: {response.status_code}")
            return []

    def get_proxys_free(self):
        try:
            url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=protocolipport&format=text&timeout=1000"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.text.split('\n')
                random_proxy = random.choice(data)
                return random_proxy
            else:
                print(f"Error fetching the proxy list: {response.status_code}")
                return None
        except requests.RequestException as err:
            print(f"Error fetching the proxy list: {err}")
            return None

    def get_proxy_in_file(self):
        with open(proxy_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return 'http://' + random.choice(lines).strip()

    def main(self, j, distant, nothreads, x_pos, y_pos):
        global user_agents, outlooks, window_width, window_height, end_thread, reg_fail
        loop_cnt = 0
        while 1:
            print(f"Thread {j % nothreads + 1} : ({j} is running)")     
            # kiểm tra mail đã dùng hay chưa
            check_mail = open(mail_used_path, encoding='utf-8').read().splitlines()
            mail = outlooks[j].strip()
            print(mail)
            if mail in check_mail:
                print("Mail đã sử dụng")
                end_thread[j % nothreads] = 1
                self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem("Mail đã sử dụng, chuyển sang mail tiếp"))
                break
            else:
                # Configure Chrome options to use the proxy
                try:
                    # kiểm tra nếu button stop thì thoát
                    if not self.pushButton_4.text() == "Dừng lại":
                        # end_thread[j % nothreads] = 1
                        break
                    proxy = self.get_proxys(1, self.lineEdit_2.text())[0]
                    # proxy = self.get_proxy_in_file()
                    if proxy and proxy[0] == '{': 
                        self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem("Lấy proxy lỗi, đang thử lại..."))
                        print("Get proxy lỗi", end="\r")
                        for i in range(10, -1, -1):
                            print(f"Get proxy lỗi, chờ {i}s", end="\r")
                            self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem(f"Get proxy lỗi, vui lòng chờ {i}s"))
                            self.ui_sleep(1)
                        self.count_down_ui(j, 5)
                        continue
                    else:
                        self.tableWidget.setItem(j, 1, QtWidgets.QTableWidgetItem(proxy))
                except Exception as e:
                    print(e)
                    print("Proxy mạng chậm")
                    self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem("Proxy mạng chậm"))
                    self.count_down_ui(j, 7)
                    loop_cnt += 1
                    if loop_cnt == 3: 
                        end_thread[j % nothreads] = 1
                        return
                    else:
                        self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem("Get lại proxy"))
                        self.count_down_ui(j, 10)
                        continue

                if proxy and 'http' not in proxy:
                    proxy = 'http://' + proxy
                print(proxy)
                
                user_agent = random.choice(user_agents)

                # === Chrome portable, chromedriver và extension nằm cạnh .exe ===
                chrome_binary = Path(resource_path("GoogleChromePortable64/App/Chrome-bin/chrome.exe"))
                driver_path   = Path(resource_path("chromedriver/chromedriver.exe"))
                ext_dir       = Path(resource_path("anticaptcha-plugin_v0.67"))

                assert chrome_binary.exists(), f"Không tìm thấy Chrome portable: {chrome_binary}"
                assert driver_path.exists(),   f"Không tìm thấy chromedriver: {driver_path}"
                assert (ext_dir / "manifest.json").exists(), f"Thiếu manifest.json trong: {ext_dir}"
                options = Options()
                options.binary_location = str(chrome_binary)
                options.page_load_strategy = 'none'
                options.add_argument("--lang=en")
                options.add_argument(f"--proxy-server={proxy}")
                options.add_argument("--disable-features=DisableLoadExtensionCommandLineSwitch")
                options.add_argument(f'--load-extension={ext_dir}')
                options.add_argument(f'user-agent={user_agent}')
                options.add_argument(f"--window-size={window_width},{window_height}")
                options.add_experimental_option('excludeSwitches', ['enable-automation'])
                prefs = {
                    "credentials_enable_service": False,      # tắt Google Smart Lock
                    "profile.password_manager_enabled": False # tắt Password Manager của Chrome
                }
                options.add_experimental_option("prefs", prefs)
                options.add_argument("--disable-save-password-bubble")
                service = Service(executable_path=str(driver_path))
                driver = webdriver.Chrome(service=service, options=options)
                with self.drivers_lock:
                    self.drivers.append(driver)
                # --- lưu PID chromedriver để kill theo PID ---
                try:
                    if hasattr(driver, "service") and driver.service and driver.service.process:
                        self._pids.add(driver.service.process.pid)
                except Exception:
                    pass
            
                driver.set_window_position(x_pos, y_pos)
                driver.set_page_load_timeout(80)

                try:
                    driver.get("https://accounts.snapchat.com/v2/signup?continue=%2Faccounts%2Fsso%3Fclient_id%3Dlens-studio-web")
                except Exception:
                    print(f"Proxy không phản hồi hoặc đã dừng")
                    self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem(f"Proxy không phản hồi"))
                    driver.quit()
                    continue

                try:
                    accept_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='Accept All']"))
                    )
                    accept_button.click()
                except Exception:
                    print("No cookie accept button found or an error occurred:")
                
                try:
                    accept_button = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name=firstName]"))
                    )
                    accept_button.click()
                except Exception:
                    print("Proxy không phản hồi, đổi proxy khác hoặc đã dừng")
                    self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem("Proxy không phản hồi, đổi proxy khác"))
                    driver.quit()
                    continue

                self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem("Nhập dữ liệu"))
                self.ui_sleep(7)
                first_name = driver.find_element(By.CSS_SELECTOR, "input[name=firstName]")
                name = self.get_random_ten()
                self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem("Nhập first name: "+name))
                first_name.send_keys(name)
                
                self.ui_sleep(5)
                name = self.get_random_ho()
                last_name = driver.find_element(By.CSS_SELECTOR, "input[name=lastName]")
                self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem(f"Nhập last name: {name}"))
                last_name.send_keys(name)

                self.ui_sleep(5)
                user_name = driver.find_element(By.CSS_SELECTOR, "input[name=username]")
                un = self.generate_random_string()
                self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem(f"Nhập username: {un}"))
                user_name.send_keys(un)
                
                self.ui_sleep(5)
                email_ip = driver.find_element(By.CSS_SELECTOR, "input[name=email]")               
                self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem(f"Nhập email: {mail.split('|')[0]}"))
                email_ip.send_keys(mail.split('|')[0])

                self.ui_sleep(5)
                pw = driver.find_element(By.CSS_SELECTOR, "input[name=password]")
                password = self.generate_password()
                self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem(f"Nhập password: {password}"))
                pw.send_keys(password)

                self.ui_sleep(5)
                self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem("Nhập ngày sinh"))
                month = driver.find_element(By.CSS_SELECTOR, "select[name=month]")
                select = Select(month)
                ran_month = random.randint(1, 12)
                select.select_by_value(str(ran_month))

                day = driver.find_element(By.CSS_SELECTOR, "input[name=day]")
                day.send_keys(random.randint(1, 28))

                year = driver.find_element(By.CSS_SELECTOR, "input[name=year]")
                year.send_keys(random.randint(1980, 2004))
                
                print(driver.current_url)
                submit = driver.find_element(By.CSS_SELECTOR, "button")
                driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", submit)
                try:
                    submit.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", submit)

                submit.click()
                self.count_down_ui(j, 50)
                prefix = "https://accounts.snapchat.com/accounts/v2/signup/email_verification"
                
                try:
                    exit_loop = False
                    loop_code= 0
                    while 1:
                        res = self.submit_data(driver, j, distant, un, mail, prefix, x_pos, y_pos, password)
                        self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem(res))

                        if res == "Đăng ký thành công":
                            end_thread[j % nothreads] = 1
                            exit_loop = True
                        elif res == "Đăng nhập thất bại":
                            end_thread[j % nothreads] = 1
                            self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem("Đăng nhập gmail thất bại"))
                            reg_fail.write(mail + '\n')
                            reg_fail.flush()
                            exit_loop = True
                        elif res == "Chưa có mail":
                            self.count_down_ui(j, 10)
                            try:
                                resend = driver.find_element(By.CSS_SELECTOR, 'div[class*="EmailConfirmation_resendEmailEnabled"]')
                                resend.click()
                            except Exception:
                                pass
                            self.count_down_ui(j, 30)
                            loop_code += 1   
                            if loop_code > 2:
                                end_thread[j % nothreads] = 1
                                self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem("Không có code"))
                                reg_fail.write(mail + '\n')
                                reg_fail.flush()
                                exit_loop = True
                                # break
                            else:
                                self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem(f"Get lại code lần {loop_code}"))
                                continue
                        elif res.find('Ten da dang ky') >= 0:
                            un = self.generate_random_string()
                            user_name.clear()
                            user_name.send_keys(un)
                            submit.click()
                            self.count_down_ui(j, 60)   
                            continue
                        elif res == "Email đã đăng ký":
                            end_thread[j % nothreads] = 1
                            exit_loop = True
                        elif res == "Proxy dính check capcha":
                            loop_code += 1   
                            if loop_code <= 2:
                                self.count_down_ui(j, 50)
                                continue
                            # exit_loop = True
                        break
                except Exception as e:
                    print(f"Error: {e}")
                finally:
                    # loop_cnt += 1
                    try:
                        driver.quit()
                        if exit_loop:
                            self.count_down_ui(j, 15)
                            self.tableWidget.setItem(j, 2, QtWidgets.QTableWidgetItem(res))
                            break
                    except Exception as e:
                        print(e)

    def count_down_ui(self, index, x):
        for i in range(x, 0, -1):
            self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem(f"Còn {i}s"))
            self.ui_sleep(1)

    def submit_data(self, driver, n, distant, un, mail, prefix, x_pos, y_pos, password):
        global registered, mail_used
        try:
            error_ele = driver.find_element(By.CSS_SELECTOR, 'p[data-testid="error-text"]')
            msg = error_ele.get_attribute("textContent").strip()
            if "Username is already taken" in msg or "اسم المستخدم مأخوذ سابقًا" in msg:
                print(f"Tên {un} đã đăng ký, đang tạo lại username")
                return "Ten da dang ky"
            elif "Email address is already taken" in msg or "إن عنوان البريد الإلكتروني مستخدم بالفعل. سجل" in msg:
                print(f"Email {mail} đã đăng ký")
                mail_used.write(f'{mail}\n')
                mail_used.flush()
                return "Email đã đăng ký"
        except Exception as e:
            error_ele = None
            print(f"error: {e}")
        
        try:
            otp = driver.find_element(By.CSS_SELECTOR, "input[name=otpCode]")
        except Exception as e:
            print(f"Error: {e}")
            otp = None

        if otp:
            try:
                email_viewer = HotMail(mail.split('|')[0], mail.split('|')[3])
                code = email_viewer.load()
            except:
                code = 1
            
            if code is None:
                print("chưa có mail")
                return "Chưa có mail"
            elif code == 1:
                print("Đăng nhập thất bại")
                return "Đăng nhập thất bại"
            else:
                self.tableWidget.setItem(n, 2, QtWidgets.QTableWidgetItem(f"Lấy được mã {code} thành công"))
                ip_code = driver.find_element(By.CSS_SELECTOR, "input[name=otpCode]")
                ip_code.send_keys(code)
                self.ui_sleep(3)
                submit = driver.find_element(By.CSS_SELECTOR, "button")
                submit.click()
                self.count_down_ui(n, 50)
                url = driver.execute_script("return window.location.href;")
                if url.startswith("https://my-lenses.snapchat.com"):
                    registered.write('{0}|{1}|{2}\n'.format(un, password, mail.strip()))
                    mail_used.write(f'{mail.strip()}\n')
                    registered.flush()
                    mail_used.flush()
                    print("Đăng ký thành công")
                    return "Đăng ký thành công"
                else:
                    return "Chưa có mail"    
        else:
            return "Proxy dính check capcha"
            
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Import\nGmail"))
        self.pushButton_2.setText(_translate("MainWindow", "Import\nName"))
        self.pushButton_2.setVisible(False)
        self.pushButton_2.setStyleSheet("QPushButton { background-color : green }")
        self.label.setText(_translate("MainWindow", "Số acc gmail:"))
        self.label_2.setText(_translate("MainWindow", "Số name:"))
        self.pushButton_4.setText(_translate("MainWindow", "Bắt đầu"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "EMAIL"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "PROXY"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "TRẠNG THÁI"))
        self.tableWidget.setColumnWidth(0, 250)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 220)
        self.label_3.setText(_translate("MainWindow", "Số proxy xoay:"))
        self.pushButton_5.setText(_translate("MainWindow", "Số luồng:"))
        self.pushButton_6.setText(_translate("MainWindow", "Link proxy:"))
        self.pushButton.clicked.connect(lambda: self.mo_file_cookie("outlook"))
        self.pushButton_2.clicked.connect(lambda: self.mo_file_cookie("name"))
        # self.pushButton_4 kết nối ở setupUi → self.toggle_run

    # ================== PHẦN: điều khiển Start/Stop ==================
    def toggle_run(self):
        if not self.running:
            self.start_run()
        else:
            self.stop_run()

    def start_run(self):
        global outlooks, names, nothreads, window_height, window_width, gap, end_thread
        if outlooks == []:
            QMessageBox.information(None , 'Error', 'Chưa có gmail')
            return
        if names == []:
            QMessageBox.information(None , 'Error', 'Chưa có danh sách name')
            return
        if self.lineEdit.text() == '':
            QMessageBox.information(None , 'Error', 'Chưa nhập số luồng')
            return
        if self.lineEdit_2.text() == '':
            QMessageBox.information(None , 'Error', 'Chưa nhập link proxy')
            return

        self.running = True
        self.stop_event.clear()
        self.pushButton_4.setText("Dừng lại")
        self.pushButton_4.setStyleSheet("QPushButton { background-color : red }")

        nothreads = int(self.lineEdit.text())
        dis = len(outlooks) // max(1, nothreads)

        def batch_run():
            global end_thread
            try:
                for i in range(0, len(outlooks), nothreads):
                    threads = []
                    self.threads = threads
                    end_thread = [0] * min(nothreads, len(outlooks) - i)
                    for j in range(i, min(i + nothreads, len(outlooks))):
                        row = (j % nothreads) // nothreads
                        col = (j % nothreads) % nothreads
                        x_position = col * (window_width + gap)
                        y_position = row * (window_height + gap)
                        if self.pushButton_4.text() == 'Dừng lại':
                            t = threading.Thread(target=self.main, args=(j, dis, nothreads, x_position, y_position), daemon=True)
                            threads.append(t)
                            t.start()
                        self.ui_sleep(5)

                    while sum(end_thread) < len(threads):
                        print(end_thread)
                        self.ui_sleep(5)
                        # kiểm tra stop_event bằng màu của nút start
                        if self.pushButton_4.text() == "Bắt đầu":
                            print("Dừng tất cả")
                            for idx, val in enumerate(end_thread):
                                end_thread[idx] = 1
                            break
                    
                    # kiểm tra dừng hẳn
                    if self.pushButton_4.text() == "Bắt đầu":
                        stop_event.set() 
                        # break

                    for t in threads:
                        try:
                            t.join(timeout=0.1)
                        except Exception:
                            pass

                    if self.pushButton_4.text() == "Bắt đầu":
                        break
            finally:
                self.finish_run()

        master = threading.Thread(target=batch_run, daemon=True)
        master.start()

    def stop_run(self):
        self.stop_event.set()

        # Kill theo PID chromedriver (tránh kill Chrome user)
        try:
            pids = list(getattr(self, "_pids", set()))
            for pid in pids:
                try:
                    if sys.platform.startswith("win"):
                        # /F: force, /T: kill cả tiến trình con (chrome con)
                        subprocess.run(
                            ["taskkill", "/F", "/T", "/PID", str(pid)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                    else:
                        # best-effort trên *nix
                        os.kill(pid, signal.SIGKILL)
                except Exception:
                    pass
        finally:
            try:
                self._pids.clear()
            except Exception:
                pass

        # Dọn state trong app
        with self.drivers_lock:
            self.drivers.clear()
        # dừng tất cả luồng con
        # for t in self.threads:
        #     try:
        #         t.kill()
        #     except Exception:
        #         pass
        self.threads = []
        self.finish_run()

    def finish_run(self):
        self.running = False
        self.pushButton_4.setText("Bắt đầu")
        self.pushButton_4.setStyleSheet("")

    # =====================================================

    def mo_file_cookie(self, type):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(None, 'Chọn Tệp', '', 'All Files (*.*)')
        global outlooks, names
        if files:
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = file.read().strip('\n').split('\n')
                    if type == 'outlook':
                        outlooks = data
                        self.pushButton.setStyleSheet("QPushButton { background-color : green }")   
                        self.label.setText(f"Số acc Gmail: {len(outlooks)}")
                        self.tableWidget.setRowCount(len(outlooks))
                        for i in range(len(outlooks)):
                            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(outlooks[i].split('|')[0]))
                    else:
                        names = data
                        self.pushButton_2.setStyleSheet("QPushButton { background-color : green }")
                        self.label_2.setText(f"Số name: {len(names)}")

    # HÀM run CŨ không còn dùng; để lại nếu muốn tham chiếu
    def run(self):
        self.start_run()

    def ui_sleep(self, x):
        QtTest.QTest.qWait(x * 1000)
    def generate_password(self):
        global passwords
        pw = random.choice(passwords).strip().lower()
        pw = pw[0].upper() + pw[1:]
        digits = ''.join(random.choices('0123456789', k=3))
        return pw + '@' + digits  
    def generate_random_string(self):
        global user_names
        selected_name = random.choice(user_names).split('|')
        ho = selected_name[0].strip().lower()[:5]
        ten = selected_name[1].strip().lower()[:5]
        digits = ''.join(random.choices('0123456789', k=3))
        letters = ''.join(random.choices(string.ascii_lowercase, k=2))
        result = digits + letters
        return ho + ten + result

# ---- Subclass QMainWindow để chặn nút X và dọn tài nguyên ----
class AppMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def closeEvent(self, event: QtGui.QCloseEvent):
        # khi bấm X: dừng tất cả, đóng toàn bộ Chrome (kill theo PID)
        try:
            self.ui.stop_run()
        except Exception:
            pass
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = AppMainWindow()
    # dự phòng: nếu vì lý do nào đó closeEvent không chạy, vẫn dọn khi app quit
    app.aboutToQuit.connect(MainWindow.ui.stop_run)
    MainWindow.show()
    sys.exit(app.exec())
