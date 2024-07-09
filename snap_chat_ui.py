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
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox

outlooks = []
names = []
nothreads = 0
user_agents = open('user-agents.txt').read().splitlines()
registered = open('reg_success.txt', 'a', encoding='utf-8')
mail_used = open('mail_used.txt', 'a', encoding='utf-8')
# Kích thước và khoảng cách giữa các cửa sổ
window_width = 100
window_height = 600
gap = 80


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

    def get_random_name(self):
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

    def main(self, n, distant, end, x_pos, y_pos):
        global user_agents, outlooks, window_width, window_height
        index = n * distant
        while index < end:
            print(f"Thread {n}:({index} -> {end}) is running")
            # Configure Chrome options to use the proxy
            try:
                proxy = self.get_proxys(1, self.lineEdit_2.text())[0]
                # proxy = self.get_proxys(1, self.lineEdit_2.text())
                if proxy[0] == '{': 
                    self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Lấy proxy lỗi, đang thử lại..."))
                    print("Get proxy lỗi", end="\r")
                    for i in range(10, -1, -1):
                        print(f"Get proxy lỗi, chờ {i}s", end="\r")
                        self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem(f"Get proxy lỗi, vui lòng chờ {i}s"))
                        sleep(1)
                    sleep(5)
                    continue
                else:
                    self.tableWidget.setItem(index, 1, QtWidgets.QTableWidgetItem(proxy))
            except:
                print("Proxy hết dung lượng")
                self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Proxy hết dung lượng, dừng chạy"))
                break
            finally:
                print(proxy)
            
            user_agent = random.choice(user_agents)
            # print(user_agent)
            # break
            options = Options()
            options.add_argument(f"--proxy-server={proxy}")
            options.add_argument(f'user-agent={user_agent}')
            options.add_argument(f"--window-size={window_width},{window_height}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--display=:1")
            options.add_argument("--log-level=3")
            
            # driver.set_window_size(window_width, window_height)
            #kiểm tra mail đã dùng hay chưa
            check_mail = open('mail_used.txt').read().splitlines()
            mail = outlooks[index].strip()
            print(mail)
            if mail in check_mail:
                print("Mail đã sử dụng")
                self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Mail đã sử dụng, chuyển sang mail tiếp"))
                index += 1
            else:
                sleep(distant)
                driver = webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()),
                    options=options,
                )
                driver.set_page_load_timeout(50)
                driver.set_window_position(x_pos, y_pos)
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
                
                try:
                    accept_button = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name=first_name]"))
                    )
                    accept_button.click()
                except Exception as e:
                    print("Proxy không phản hồi, đổi proxy khác")
                    self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Proxy không phản hồi, đổi proxy khác"))
                    driver.quit()
                    continue

                self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Nhập dữ liệu"))
                sleep(7)
                self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Nhập first name"))
                first_name = driver.find_element(By.CSS_SELECTOR, "input[name=first_name]")
                name = self.get_random_name()
                first_name.send_keys(name)
                
                sleep(2)
                self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Nhập last name"))
                name = self.get_random_name()
                last_name = driver.find_element(By.CSS_SELECTOR, "input[name=last_name]")
                last_name.send_keys(name)

                sleep(2)
                self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Nhập username"))
                user_name = driver.find_element(By.CSS_SELECTOR, "input[name=username]")
                un = self.generate_random_string()
                user_name.send_keys(un)
                
                sleep(2)
                self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Nhập email"))
                email = driver.find_element(By.CSS_SELECTOR, "input[name=email]")               
                email.send_keys(mail.split('|')[0])
                print(f"Đang đăng ký cho mail {mail.split('|')[0]} index: {index}")

                sleep(2)
                self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Nhập password"))
                pw = driver.find_element(By.CSS_SELECTOR, "input[name=password]")
                pw.send_keys(mail.split('|')[1])

                sleep(2)
                self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Nhập ngày sinh"))
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
                
                self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Nhập mã xác minh"))

                try:
                    res = self.submit_data(driver, n, distant, un, mail, prefix)
                    if res == "Đăng ký thành công":
                        self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Đăng ký thành công, chuyển email tiếp"))
                        index += 1
                    elif res == "Chưa có mail":
                        self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Chưa có mail, thử reg lại"))
                    elif res == "Tên đã đăng ký":
                        self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Tên đã đăng ký, thử lại tên khác"))
                        un = self.generate_random_string()
                        user_name.send_keys(un)
                        self.submit_data(driver, n, distant, un, mail, prefix)
                        driver.quit()
                    elif res == "Email đã đăng ký":
                        self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Email đã đăng ký, chuyển email tiếp"))
                        index += 1
                    elif res == "Proxy dính check capcha":
                        self.tableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem("Proxy dính check capcha, thử lại ip khác"))
                except:
                    print("Error")
                finally:
                    driver.quit()
            sleep(5)

    def submit_data(self, driver, n, distant, un, mail, prefix):
        global registered, mail_used
        if driver.current_url.startswith(prefix):
                print("Nhập mã xác minh")
                code = self.readCodeOutLook(mail.split('|')[0], mail.split('|')[1])
                # print(code)
                if code:
                    ip_code = driver.find_element(By.CSS_SELECTOR, "input[name=code]")
                    ip_code.send_keys(code)
                    submit = driver.find_element(By.CSS_SELECTOR, "button")
                    submit.click()      
                    registered.write(f'{un}|{mail.split('|')[1]}|{mail.strip()}\n')
                    mail_used.write(f'{mail.strip()}\n')
                    registered.flush()
                    mail_used.flush()
                    print("Đăng ký thành công, chuyển sang mail tiếp theo")
                    driver.quit()
                    return "Đăng ký thành công"
                    
                else:
                    print("Chưa có mail, thử chạy lại")
                    driver.quit()
                    return "Chưa có mail"
        else:
            sleep(5)
            if driver.page_source.find("Username is already taken") != -1:
                print(f"Tên {un} đã đăng ký, đang tạo lại username")
                driver.quit()
                return "Tên đã đăng ký"
            elif driver.page_source.find("Email address is already taken") != -1:
                print(f"Email {mail} đã đăng ký")
                mail_used.write(f'{mail}\n')
                mail_used.flush()
                driver.quit()
                return "Email đã đăng ký"
                # n += 1
            else:
                print(f"Proxy {n % distant} dính check capcha, đổi ip mới")
                return "Proxy dính check capcha"
        

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Import\n"
"Outlook"))
        self.pushButton_2.setText(_translate("MainWindow", "Import\n"
"Name"))
        self.label.setText(_translate("MainWindow", "Số acc Outlook:"))
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
        self.pushButton_4.clicked.connect(self.run)

    def hat_delay(self,dl, i):
        for x in range(int(dl) , 0, -1):
            print(f'[T][LOADING][|][x.....][{x}]      ',end='\r')
            sleep(0.200)
            print(f'[T][LOADING][/][xX....][{x}]      ',end='\r')
            sleep(0.200)
            print(f'[T][LOADING][-][xxX...][{x}]      ',end='\r')
            sleep(0.200)
            print(f'[T][LOADING][\\][xxxX..][{x}]      ',end='\r')
            sleep(0.200)
            print(f'[T][LOADING][|][xxxxX.][{x}]      ',end='\r')
            sleep(0.200)
            print(f'[T][LOADING][|][xxxxxx][{x}]      ',end='\r')
            sleep(0.200)        

    def mo_file_cookie(self, type):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(None, 'Chọn Tệp', '', 'All Files (*.*)')
        global outlooks, names
        if files:
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = file.read().strip('\n').split('\n')
                    if type == 'outlook':
                        outlooks = data
                        print("outlook")
                        self.pushButton.setStyleSheet("QPushButton { background-color : green }")   
                        self.label.setText(f"Số acc Outlook: {len(outlooks)}")
                        self.tableWidget.setRowCount(len(outlooks))
                        for i in range(len(outlooks)):
                            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(outlooks[i].split('|')[0]))
                    else:
                        names = data
                        print("name")
                        self.pushButton_2.setStyleSheet("QPushButton { background-color : green }")
                        self.label_2.setText(f"Số name: {len(names)}")
                        
    def run(self):
        global outlooks, names, nothreads, window_height, window_width, gap
        if outlooks == []:
            QMessageBox.information(None , 'Error', 'Chưa có outlook')
        elif names == []:
            QMessageBox.information(None , 'Error', 'Chưa có danh sách name')
        elif self.lineEdit.text() == '':
            QMessageBox.information(None , 'Error', 'Chưa nhập số luồng')
        elif self.lineEdit_2.text() == '':
            QMessageBox.information(None , 'Error', 'Chưa nhập link proxy')
        else:
            nothreads = int(self.lineEdit.text())
            print(nothreads)
            dis = len(outlooks) // nothreads
            for i in range(nothreads):
                row = i // nothreads  # Tính số hàng (0-based index)
                col = i % nothreads  # Tính số cột (0-based index)
                
                x_position = col * (window_width + gap)
                y_position = row * (window_height + gap)
                print(f"Window {i}: ({x_position}, {y_position})")

                # (x_position, y_position, window_width, window_height)
                threading.Thread(target=self.main, args=(i, dis, i * dis + dis, x_position, y_position)).start()
                sleep(20)

    def generate_random_string(self):
        length = random.randint(6, 10)
        letters = string.ascii_letters + string.digits  # Tập hợp các chữ cái và chữ số
        first_letter = random.choice(string.ascii_letters)  # Chọn chữ cái đầu tiên
        other_letters = ''.join(random.choices(letters, k=length-1))
        return first_letter + other_letters

    def readCodeOutLook(self, email, password):
        with MailBox('outlook.office365.com').login(email, password) as mailbox:
            for msg in mailbox.fetch():
                if msg.subject == 'Snapchat Login Verification Code':
                    data = msg.html.split('\n')
                    code = data[31].strip()
                    print(code)
                    return code
            return None



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
