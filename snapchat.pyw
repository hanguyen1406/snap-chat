from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, WebDriverException, NoSuchElementException, NoAlertPresentException
)

import re, threading, random, string, requests, imaplib, poplib, email, json, base64
from email.header import decode_header
from time import sleep
from pathlib import Path
import subprocess, platform, signal, sys, os, time, shutil, datetime, functools
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor

import undetected_chromedriver as uc

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog,
    QMenu, QAction, QLabel, QVBoxLayout, QLineEdit, QDialog, QDesktopWidget, QMessageBox,
    QCheckBox, QWidget, QHBoxLayout, QSpinBox, QPlainTextEdit, QDateTimeEdit, QListWidget, QComboBox
)
from PyQt5.QtCore import QDateTime, QThread, pyqtSignal, QSemaphore, QTimer, QSettings, Qt, QRunnable, QThreadPool, QObject
from PyQt5.QtGui import QPixmap, QIcon


def get_positions(screen_w, screen_h, win_w, win_h, num_windows):
    positions = []
    y = 0
    while y <= screen_h:
        x = 0
        while x <= screen_w:   # cho tới khi tràn
            positions.append((x, y))
            x += win_w
        if x > screen_w:
            positions.append((screen_w, y))
        y += win_h

    result = [positions[i % len(positions)] for i in range(num_windows)]
    return result
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

class AddChangeDialog(QDialog):
    def __init__(self, title, guide_text):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(guide_text))
        self.plainTextEdit = QPlainTextEdit()
        layout.addWidget(self.plainTextEdit)
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Hủy")
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
    def get_data(self):
        text = self.plainTextEdit.toPlainText().strip()
        if not text:
            return []
        return [line.strip() for line in text.splitlines() if line.strip()]


def resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)
class WorkerSignals(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool)

class BatchWorker(QRunnable):
    def __init__(self, data_rows, soluong, screen_w, screen_h, win_w, win_h):
        super().__init__()
        # ... (Phần khởi tạo không đổi)
        self.data_rows = data_rows
        self.soluong = soluong
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.win_w = win_w
        self.win_h = win_h
        self._stop = False
        self.signals = WorkerSignals()
        self.active_threads = 0
        self.lock = threading.Lock()
        self.active_pids = {}
        # Tải User-Agents (Giữ nguyên)
        user_agents_path = resource_path('user-agents.txt')
        try:
            with open(user_agents_path, encoding='utf-8') as f:
                self.user_agents = f.read().splitlines()
        except Exception:
            self.user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"]
            print(f"⚠️ Không thể tải user-agents từ: {user_agents_path}. Sử dụng user-agent mặc định.")
        # Thêm biến UI cần thiết (nếu bạn sử dụng QTableWidget trong worker)
        self.tableWidget = None # Cần được truyền/thiết lập nếu muốn dùng trong Worker
        self.nothreads = 1 # Giả định số luồng tối đa, nhưng logic run() đã sử dụng threading.Thread
        self.reg_fail = None # Giả định file ghi lỗi đăng ký
        self.count_down_ui = lambda row, seconds: time.sleep(seconds) # Hàm giả định
        self.end_thread = {} # Giả định dictionary trạng thái luồng

## Hàm Dừng Luồng
# ---
    def stop(self):
        # ... (Phần stop giữ nguyên, đã được viết tốt)
        print("⏹ Tín hiệu dừng nhận được. Bắt đầu tắt cưỡng bức các trình duyệt.")
        self._stop = True
        pids_to_quit = []
        with self.lock:
            pids_to_quit = list(self.active_pids.values())
            self.active_pids.clear()
            self.active_threads = 0

        for pid in pids_to_quit:
            try:
                if sys.platform.startswith("win"):
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(pid)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                else:
                    os.kill(pid, signal.SIGKILL)
            except Exception as e:
                print(f"Lỗi khi tắt PID {pid} cưỡng bức: {e}")

## Hàm Chạy Chính (Thread Pool)
# ---
    def run(self):
        total_selected = len(self.data_rows)
        # Bỏ logic phân batch và tạo luồng thủ công
        # QRunnable thường được quản lý bởi QThreadPool, nên tạo thread thủ công là không cần thiết,
        # nhưng tôi giữ lại logic chia batch và gọi thread để giữ cấu trúc ban đầu của bạn.
        
        for i in range(0, total_selected, self.soluong):
            if self._stop:
                print("⏹ Stop signal nhận được, dừng batch còn lại.")
                break
                
            batch = self.data_rows[i:i+self.soluong]
            positions = get_positions(self.screen_w, self.screen_h, self.win_w, self.win_h, len(batch))
            threads = []
            for account_data, (x, y) in zip(batch, positions):
                with self.lock:
                    if self._stop:
                        break
                    # Lưu ý: active_threads sẽ được giảm trong open_chrome
                    self.active_threads += 1 
                
                self.signals.progress.emit(account_data['row'], "Đang chờ mở trình duyệt...")
                
                # SỬA LỖI: Không cần truyền 'self' (worker) là tham số đầu tiên cho target=self.open_chrome
                t = threading.Thread(
                    target=self.open_chrome,
                    args=(account_data, x, y, self.win_w, self.win_h) # Loại bỏ tham số 'self' đầu tiên
                )
                t.start()
                threads.append(t)
            for t in threads:
                t.join()

            if self._stop:
                break
            time.sleep(1.0) # Chờ 1 giây giữa các batch
            
        # Chờ tất cả các luồng con hoàn thành
        while True:
            is_done = False
            with self.lock:
                if self.active_threads <= 0:
                    is_done = True
            
            if is_done or self._stop:
                break
                    
            time.sleep(0.5)
            
        # Kết thúc tín hiệu
        if self._stop:
            self.signals.finished.emit(True)
        else:
            self.signals.finished.emit(False)

## Các Hàm Tạo Dữ liệu (Giữ nguyên)
# ---
    def generate_password(self):
        # ... (Giữ nguyên)
        passwords = open("./passwords.txt", encoding='utf-8').readlines()
        pw = random.choice(passwords).strip().lower()
        pw = pw[0].upper() + pw[1:]
        digits = ''.join(random.choices('0123456789', k=3))
        return pw + '@' + digits
        
    def generate_random_string(self):
    # Đọc danh sách tên từ file
        with open("./username.txt", encoding='utf-8') as f:
            user_names = f.readlines()
        selected_name = random.choice(user_names).strip()

        digits = ''.join(random.choices('0123456789', k=2))

        letters = ''.join(random.choices(string.ascii_lowercase, k=2))

        result = f"{selected_name}{digits}{letters}"
        return result

    def get_random_ten(self):
        # ... (Giữ nguyên)
        names = open("./name.txt", encoding='utf-8').readlines()
        random_line = random.choice(names)
        return random_line.strip()

    def get_random_ho(self):
        # ... (Giữ nguyên)
        names = open("./name.txt", encoding='utf-8').readlines()
        random_line = random.choice(names)
        return random_line.strip()

## Hàm Mở Chrome & Thực hiện Đăng ký
# ---
    # SỬA: Bỏ tham số 'worker' không cần thiết
    def open_chrome(self, account_data, x, y, win_w, win_h):
        row = account_data['row']
        email = account_data.get('email', '')
        pass_mail = account_data.get('password', '')
        mail_kp = account_data.get('mail_kp', '')
        fa2 = account_data.get('fa2', '') 
        app_pw = account_data.get('app_pw', '')
        proxy = account_data.get('proxy', '')
        driver = None
        service_pid = None
        
        try:
            # ... (Phần khởi tạo Options và Driver giữ nguyên)
            user_agent = random.choice(self.user_agents)
            chrome_binary = Path(resource_path("GoogleChromePortable64/App/Chrome-bin/chrome.exe"))
            driver_path = Path(resource_path("chromedriver/chromedriver.exe"))
            ext_dir = Path(resource_path("anticaptcha-plugin_v0.67"))

            # Kiểm tra đường dẫn
            if not chrome_binary.exists(): raise FileNotFoundError(f"Thiếu Chrome: {chrome_binary}")
            if not driver_path.exists(): raise FileNotFoundError(f"Thiếu Chromedriver: {driver_path}")
            if not (ext_dir / "manifest.json").exists(): raise FileNotFoundError(f"Thiếu tiện ích mở rộng: {ext_dir}")

            options = Options()
            options.binary_location = str(chrome_binary)
            options.page_load_strategy = 'none'
            options.add_argument("--lang=en")
            
            if proxy:
                options.add_argument(f"--proxy-server=http://{proxy}")
                self.signals.progress.emit(row, "Đã bật Proxy...")
            
            options.add_argument("--disable-features=DisableLoadExtensionCommandLineSwitch")
            options.add_argument(f'--load-extension={ext_dir}')
            options.add_argument(f'user-agent={user_agent}')
            options.add_argument(f"--window-size={win_w},{win_h}")
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            }
            options.add_experimental_option("prefs", prefs)
            options.add_argument("--disable-save-password-bubble")
            
            service = Service(executable_path=str(driver_path))
            driver = webdriver.Chrome(service=service, options=options)
            
            service_pid = service.process.pid
            
            driver.set_window_position(x, y)
            driver.set_page_load_timeout(400)
            
            # Ghi PID vào active_pids
            with self.lock:
                self.active_pids[row] = service_pid

            # Kiểm tra tín hiệu dừng trước khi bắt đầu tác vụ dài
            if self._stop:
                 raise Exception("Dừng luồng trước khi tải trang.")

            driver.get("https://accounts.snapchat.com/v2/signup?continue=%2Faccounts%2Fsso%3Fclient_id%3Dlens-studio-web")
            time.sleep(15)
            driver.refresh()
            time.sleep(15)
            
            # Xử lý Cookie
            try:
                accept_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Accept All']"))
                )
                accept_button.click()
            except Exception:
                print(f"[{row}] Không tìm thấy nút Accept Cookie.")
            i = 0
            while i <= 3:
                try:
                    # SỬA LỖI LỚN: Thay vì click, cần chờ input load để bắt đầu điền dữ liệu
                    WebDriverWait(driver, 50).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name=firstName]"))
                    )
                    break
                except Exception:
                    print(f"[{row}] Proxy không phản hồi, đổi proxy khác hoặc đã dừng.")
                    self.signals.progress.emit(row, ("Tải trang thất bại"))
                    i += 1
                    driver.refresh()

                
            self.signals.progress.emit(row, ("Nhập dữ liệu"))
            time.sleep(7) 
            
            # --- Nhập Dữ liệu ---
            first_name = driver.find_element(By.CSS_SELECTOR, "input[name=firstName]")
            name = self.get_random_ten()
            self.signals.progress.emit(row, ("Nhập first name: "+name))
            first_name.send_keys(name)
            time.sleep(5) 
            last_name = driver.find_element(By.CSS_SELECTOR, "input[name=lastName]")
            name = self.get_random_ho()
            self.signals.progress.emit(row, (f"Nhập last name: {name}"))
            last_name.send_keys(name)
            time.sleep(5) 
            user_name = driver.find_element(By.CSS_SELECTOR, "input[name=username]")
            un = self.generate_random_string()
            self.signals.progress.emit(row, (f"Nhập username: {un}"))
            user_name.send_keys(un)
            time.sleep(5) 
            email_ip = driver.find_element(By.CSS_SELECTOR, "input[name=email]")
            self.signals.progress.emit(row, (f"Nhập email: {email}"))
            email_ip.send_keys(email)
            time.sleep(5) 
            pw = driver.find_element(By.CSS_SELECTOR, "input[name=password]")
            password = self.generate_password()
            self.signals.progress.emit(row, (f"Nhập password: {password}"))
            pw.send_keys(password)
            time.sleep(5) 
            # Nhập Ngày sinh
            self.signals.progress.emit(row, ("Nhập ngày sinh"))
            month = driver.find_element(By.CSS_SELECTOR, "select[name=month]")
            select = Select(month)
            select.select_by_value(str(random.randint(1, 12)))

            day = driver.find_element(By.CSS_SELECTOR, "input[name=day]")
            day.send_keys(random.randint(1, 28))

            year = driver.find_element(By.CSS_SELECTOR, "input[name=year]")
            year.send_keys(random.randint(1980, 2004))
            
            # --- Submit Form ---
            print(f"[{row}] URL hiện tại: {driver.current_url}")
            submit = driver.find_element(By.CSS_SELECTOR, "button")
            driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", submit)
            
            try:
                submit.click()
            except Exception:
                driver.execute_script("arguments[0].click();", submit)
            time.sleep(50) 
            loop_code = 0
            while not self._stop:
                res = self.submit_data(driver, row, un, email, pass_mail, mail_kp, fa2, app_pw, password)
                self.signals.progress.emit(row, f"Kết quả: {res}")
                
                if self.tableWidget:
                     self.signals.progress.emit(row, res) 

                if res == "Dang ky thanh cong":
                    self.signals.progress.emit(row, "✅ Đăng Ký Thành Công")
                    break # Thành công
                
                elif res == "Ten da dang ky":
                    un = self.generate_random_string()
                    user_name.clear()
                    user_name.send_keys(un)
                    # SỬA LỖI: Click lại nút submit sau khi đổi username
                    driver.find_element(By.CSS_SELECTOR, "button").click() 
                    time.sleep(10) # Giảm thời gian chờ
                    continue # Quay lại kiểm tra
                
                elif res == "Chua co mail":
                    loop_code += 1
                    if loop_code > 2:
                        self.signals.progress.emit(row, "❗ Không lấy được code sau 3 lần thử.")
                        # Ghi vào file lỗi (Giả định self.reg_fail là file object)
                        if self.reg_fail: 
                             self.reg_fail.write(email + '\n')
                             self.reg_fail.flush()
                        break
                        
                    self.signals.progress.emit(row, f"Get lại code lần {loop_code}")
                    time.sleep(10) # Chờ ngắn trước khi thử Resend
                    try:
                        resend = driver.find_element(By.CSS_SELECTOR, 'div[class*="EmailConfirmation_resendEmailEnabled"]')
                        resend.click()
                    except Exception:
                        pass
                    time.sleep(30) # Chờ email mới

                elif res == "Email da dang ky" or res == "Dang nhap that bai" or res.startswith("Loi khac") or res.startswith("Loi sau OTP"):
                    self.signals.progress.emit(row, "❗ Đăng Ký Thất Bại.")
                    break # Lỗi không thể khắc phục trong luồng này
                
                elif res == "Proxy dính check capcha":
                    loop_code += 1
                    if loop_code > 2:
                        self.signals.progress.emit(row, "Proxy dính Captcha/Lỗi quá 3 lần, dừng luồng.")
                        break
                    time.sleep(50)
                    # Không làm gì khác, vòng lặp submit_data sẽ kiểm tra lại (hy vọng Captcha tự giải quyết)
                
                else: # Các lỗi khác không xác định
                    break
            
            # --- Kết thúc luồng ---
            
            
        except (FileNotFoundError, Exception) as e:
            error_msg = f"❌ Lỗi: {type(e).__name__}: {e}"
            self.signals.progress.emit(row, error_msg)
        finally:
            # Sửa lỗi: Cần đảm bảo driver.quit() luôn được gọi
            if driver:
                driver.quit()
            
            # Xóa PID và giảm active_threads (Đây là logic then chốt)
            with self.lock:
                if row in self.active_pids:
                    del self.active_pids[row]
                self.active_threads -= 1
            # --------------------------------------------------------

    def _log_success(self, un, mail, pass_mail, mail_kp, fa2, app_pw, password, registered_file='registered.txt', used_mail_file='mail_used.txt'):
        try:
            with open(registered_file, 'a', encoding='utf-8') as f:
                f.write("|".join(map(str, [un, password, mail, pass_mail, mail_kp, fa2, app_pw])) + "\n")
            print(f"✅ Ghi log thành công vào {registered_file}.")
        except Exception as e:
            print(f"❌ Lỗi ghi file {registered_file}: {e}")

        try:
            with open(used_mail_file, 'a', encoding='utf-8') as f:
                f.write(f'{mail.strip()}\n')
            print(f"✅ Ghi log email đã dùng vào {used_mail_file}.")
        except Exception as e:
            print(f"❌ Lỗi ghi file {used_mail_file}: {e}")
            
        return "Dang ky thanh cong"

    def submit_data(self, driver, row_index, un, mail, pass_mail, mail_kp, fa2, app_pw, password):
        try:
            error_ele = driver.find_element(By.CSS_SELECTOR, 'p[data-testid="error-text"]')
            msg = error_ele.get_attribute("textContent").strip()

            if "Username is already taken" in msg or "اسم المستخدم مأخوذ سابقًا" in msg:
                print(f"⚠️ Tên người dùng '{un}' đã đăng ký, cần tạo lại username.")
                return "Ten da dang ky" 

            elif "Email address is already taken" in msg or "إن عنوان البريد الإلكتروني مستخدم بالفعل" in msg:
                print(f"⚠️ Email '{mail.split('|')[0]}' đã đăng ký.")
                try:
                    with open('mail_used.txt', 'a', encoding='utf-8') as f:
                        f.write(f'{mail.strip()}\n')
                except Exception as e:
                    print(f"❌ Lỗi ghi file mail_used.txt: {e}")
                    
                return "Email da dang ky" 
                
            else:
                print(f"Lỗi không mong muốn: {msg}")
                return f"Loi khac: {msg}"
                
        except NoSuchElementException:
            pass
        except Exception as e:
            print(f"❌ Lỗi trong quá trình kiểm tra thông báo lỗi: {e}")
            return f"Loi kiem tra lỗi: {type(e).__name__}"
            
        otp_input = None
        try:
            otp_input = driver.find_element(By.CSS_SELECTOR, "input[name=otpCode]")
        except NoSuchElementException:
            current_url = driver.execute_script("return window.location.href;")
            if current_url.startswith("https://my-lenses.snapchat.com"):
                 print("✅ Đăng ký thành công (không qua bước OTP).")
                 return self._log_success(un, mail, pass_mail, mail_kp, fa2, app_pw, password)
            
            print("❌ Lỗi: Không có trường OTP và chưa đăng ký thành công. Có thể do Proxy/Captcha.")
            return "Proxy dính check capcha"
        except Exception as e:
            print(f"❌ Lỗi khi tìm kiếm trường OTP: {e}")
            return "Loi tim truong OTP"

        if otp_input:
            code = None
            try:
                email_viewer = HotMail(mail, app_pw)
                code = email_viewer.load()
            except Exception as e:
                print(f"❌ Lỗi trong quá trình lấy mã OTP từ email: {e}")
                return "Loi trong qua trinh lay ma"

            if code is None:
                print("⌛ Chưa tìm thấy mã OTP trong email.")
                return "Chua co mail"
            elif str(code) == '1' or not code:
                print("❌ Đăng nhập/Lấy mã thất bại (lỗi HotMail).")
                return "Dang nhap that bai"

            print(f"✅ Lấy được mã OTP: {code}")
            try:
                otp_input.send_keys(code)
                time.sleep(3)
                submit_button = driver.find_element(By.CSS_SELECTOR, "button")
                submit_button.click()
                
                print("Đang chờ xác nhận OTP...")
                time.sleep(15)

                current_url = driver.execute_script("return window.location.href;")
                if current_url.startswith("https://my-lenses.snapchat.com"):
                    print("✅ Đăng ký thành công sau xác minh OTP.")
                    return self._log_success(un, mail, pass_mail, mail_kp, fa2, app_pw, password)
                else:
                    print("❌ Lỗi: Đã nhập OTP nhưng không chuyển trang thành công.")
                    return "Loi sau OTP khong ro"

            except Exception as e:
                print(f"❌ Lỗi trong quá trình nhập và submit OTP: {e}")
                return "Loi nhap va submit OTP"

        return "Khong xac dinh"
class Ui_MainWindow(object):
    config = QtCore.QSettings("Qzinhcoder", "RegSnapChat")
    def __init__(self):
        super().__init__()
        self.setupUi(MainWindow)
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(787, 594)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        # THIẾT LẬP GroupBox
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setContentsMargins(10, 20, 10, 10)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        
        # --- NÚT 1: self.pushButton (Nhập File Gmail) ---
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 0, 1, 1)
        
        self.horizontalLayout.addLayout(self.gridLayout)

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        
        # Spacer
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        
        self.spinBox = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox.setObjectName("spinBox")
        self.spinBox.setValue(self.config.value('spinBox', 0))
        self.verticalLayout.addWidget(self.spinBox)
        
        self.horizontalLayout.addLayout(self.verticalLayout)
        
        self.horizontalLayout.setStretch(0, 1) 
        self.horizontalLayout.setStretch(1, 2) 

        self.horizontalLayout_3.addWidget(self.groupBox)

        # Layout cho Bắt Đầu / Dừng Lại
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        
        # --- NÚT 2: self.pushButton_2 (Bắt Đầu) ---
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        
        # --- NÚT 3: self.pushButton_3 (Dừng Lại) ---
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)
        
        self.horizontalLayout_3.setStretch(0, 2) 
        self.horizontalLayout_3.setStretch(1, 1) 
        
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        # Table area
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        
        # --- SỬA LỖI 1: Đặt lại số cột cho đúng (4 cột) ---
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setRowCount(0)

        self.gridLayout_2.addWidget(self.tableWidget, 0, 0, 1, 1)
        
        self.verticalLayout_2.addLayout(self.gridLayout_2)

        # Thiết lập tỷ lệ kéo dãn 1:5 (Control Area nhỏ hơn, Table Area lớn hơn)
        self.verticalLayout_2.setStretch(0, 1) 
        self.verticalLayout_2.setStretch(1, 5) 

        MainWindow.setCentralWidget(self.centralwidget)
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        header = self.tableWidget.horizontalHeader()
        self.tableWidget.setHorizontalHeaderLabels(['#','Email', 'Password', 'Mail KP', '2FA', 'App Passwords', 'Proxy', 'Trạng Thái'])
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.tableWidget.setColumnWidth(0, 30)
        for i in range(1, self.tableWidget.columnCount()):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.showContextMenu)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(999999)
        self.open_accout_save()
        MainWindow.closeEvent = self.closeEvent
        self.pushButton.clicked.connect(self.open_add_acc)
        self.pushButton_2.clicked.connect(self.start)
        self.pushButton_3.clicked.connect(self.stop)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "THIẾT LẬP"))
        self.pushButton.setText(_translate("MainWindow", "Nhập File Gmail"))
        self.label.setText(_translate("MainWindow", "Số Luồng:"))
        self.pushButton_2.setText(_translate("MainWindow", "Bắt Đầu"))
        self.pushButton_3.setText(_translate("MainWindow", "Dừng Lại"))

    def start(self):
        try:
            screen = QApplication.primaryScreen() 
            screen_w = screen.size().width()
            screen_h = screen.size().height()
        except Exception:
            screen_w, screen_h = 1920, 1080 
            
        win_w, win_h = 400, 400
        soluong = self.spinBox.value()

        data_to_process = []
        for row in range(self.tableWidget.rowCount()):
            checkbox = self.tableWidget.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                email_item = self.tableWidget.item(row, 1)
                pw_item = self.tableWidget.item(row, 2)
                recovery_item = self.tableWidget.item(row, 3)
                fa2_item = self.tableWidget.item(row, 4)
                app_pw_item = self.tableWidget.item(row, 5)
                proxy_item = self.tableWidget.item(row, 6)

            
                account_data = {
                    'row': row,
                    'email': email_item.text() if email_item else "",
                    'password': pw_item.text() if pw_item else "",
                    'mail_kp': recovery_item.text() if recovery_item else "",
                    'fa2': fa2_item.text() if fa2_item else "",
                    'app_pw': app_pw_item.text() if app_pw_item else "",
                    'proxy': proxy_item.text() if proxy_item else "",
                }
                data_to_process.append(account_data)

        if not data_to_process:
            print("Không có tài khoản nào được chọn!") 
            return
            
        self.worker = BatchWorker(
            data_rows=data_to_process,
            soluong=soluong,
            screen_w=screen_w,
            screen_h=screen_h,
            win_w=win_w,
            win_h=win_h
        )

        self.worker.signals.finished.connect(self.on_worker_finished_2)
        self.worker.signals.progress.connect(self.on_worker_progress)

        QThreadPool.globalInstance().start(self.worker)
    def stop(self):
        if self.worker:
            self.pushButton_3.setText("Đợi chạy nốt...")
            self.worker.stop()

    def on_worker_finished_2(self, stopped):
        self.pushButton_3.setText("Stop")
        if stopped:
            QMessageBox.information(None, "Thông báo", "Đã dừng!")
        else:
            QMessageBox.information(None, "Thông báo", "Đã chạy xong!")
    def on_worker_progress(self, row, message):
        self.tableWidget.setItem(row, 7, QTableWidgetItem(message))


    def closeEvent(self, event):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("MainWindow")
        msg_box.setText("Bạn có chắc chắn muốn thoát không?") 
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) 
        msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
        msg_box.setIcon(QMessageBox.Question)
        reply = msg_box.exec_()
        if reply == QMessageBox.Yes:
            self.save_accounts_to_file()
            self.save_setting()
            event.accept() 
        else:
            self.save_accounts_to_file()
            self.save_setting()
            event.ignore()
    def open_accout_save(self):
        try:
            with open("file_acc_tool_.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("|")
                    email = parts[0] if len(parts) > 0 else ""
                    password = parts[1] if len(parts) > 1 else ""
                    recovery = parts[2] if len(parts) > 2 else ""
                    ma_2fa = parts[3] if len(parts) > 3 else ""
                    passapp = parts[4] if len(parts) > 4 else ""
                    proxy = parts[5] if len(parts) > 5 else ""
                    self.add_to_table(email, password, recovery, ma_2fa, passapp, proxy)
        except:
            pass
    def save_setting(self):
        self.config.setValue('spinBox', self.spinBox.value())
    def save_accounts_to_file(self, filepath="file_acc_tool_.txt"):
        accounts = []
        for row in range(self.tableWidget.rowCount()):
            email_item = self.tableWidget.item(row, 1)

            pw_item = self.tableWidget.item(row, 2)
            recovery_item = self.tableWidget.item(row, 3)

            fa2_item = self.tableWidget.item(row, 4)
            app_pw_item = self.tableWidget.item(row, 5)
            proxy_item = self.tableWidget.item(row, 6)


            email = email_item.text() if email_item else ""
            password = pw_item.text() if pw_item else ""
            recovery = recovery_item.text() if recovery_item else ""
            fa2 = fa2_item.text() if fa2_item else ""
            app_pw = app_pw_item.text() if app_pw_item else ""
            proxy = proxy_item.text() if proxy_item else ""

            line = "|".join([email, password, recovery, fa2, app_pw, proxy])

            accounts.append(line)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(accounts))
    def open_add_acc(self):
        file_path, _ = QFileDialog.getOpenFileName(None, "Chọn file", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split("|")
                        email = parts[0] if len(parts) > 0 else ""
                        password = parts[1] if len(parts) > 1 else ""
                        recovery = parts[2] if len(parts) > 2 else ""
                        ma_2fa = parts[3] if len(parts) > 3 else ""
                        passapp = parts[4] if len(parts) > 4 else ""
                        proxy = parts[5] if len(parts) > 5 else ""
                        self.add_to_table(email, password, recovery, ma_2fa, passapp, proxy)
            except Exception as e:
                QtWidgets.QMessageBox.critical(None, "Lỗi đọc file", f"Đã xảy ra lỗi khi đọc file: {e}")
            self.save_accounts_to_file()
            self.save_setting()
    #===========[Thêm Account TableWidget]==================
    def add_to_table(self, email, password, recovery, ma_2fa, passapp, proxy):
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)
        self.tableWidget.setItem(row_position, 1, QtWidgets.QTableWidgetItem(email))
        self.tableWidget.setItem(row_position, 2, QtWidgets.QTableWidgetItem(password)) 
        self.tableWidget.setItem(row_position, 3, QtWidgets.QTableWidgetItem(recovery)) 
        self.tableWidget.setItem(row_position, 4, QtWidgets.QTableWidgetItem(ma_2fa)) 
        self.tableWidget.setItem(row_position, 5, QtWidgets.QTableWidgetItem(passapp))
        self.tableWidget.setItem(row_position, 6, QtWidgets.QTableWidgetItem(proxy))

        checkbox = QtWidgets.QCheckBox()
        self.tableWidget.setCellWidget(row_position, 0, checkbox)
        self.toggle_all_checkboxes(QtCore.Qt.Checked)
        self.tableWidget.scrollToBottom()
    #===========[Menu TableWidget]==========================
    def showContextMenu(self, position):
        menu = QMenu()
        action2 = QMenu("Thay Đổi Dữ Liệu Cột")
        action2_1 = QAction("Thay đổi Email")
        action2_5 = QAction("Thay đổi Proxy")
        action2.addAction(action2_1)
        action2.addAction(action2_5)

        action3 = QAction("Sao Chép Tự Chọn")


        action_sub1 = QAction("Xóa Hàng")
        action_sub2 = QAction("Xóa Tất Cả")
        action4 =  QAction("Chọn Tất Cả Tick (Bôi Đen)")
        action3_tick = QAction("Tắt Tất Cả Tick (Bôi Đen)")
        action_sub1_2 = QAction("Tắt Tất Cả Tick All")
        action_sub2_2 = QAction("Chọn Tất Cả Tick All")

        menu.addMenu(action2)
        menu.addAction(action3)
        menu.addAction(action_sub1)
        menu.addAction(action_sub2)

        menu.addAction(action4)
        menu.addAction(action3_tick)
        menu.addAction(action_sub1_2)
        menu.addAction(action_sub2_2)

        action3.triggered.connect(self.copy_field)
        action2_1.triggered.connect(self.change_email_2)
        action2_5.triggered.connect(self.change_proxy_2)

        action_sub1.triggered.connect(self.xoaHang)
        action_sub2.triggered.connect(self.xoaTatCa)
        action4.triggered.connect(self.on_tick_black)
        action3_tick.triggered.connect(self.off_tick_black)
        action_sub1_2.triggered.connect(self.tatTatCaTick)
        action_sub2_2.triggered.connect(self.moTatCaTick)
        menu.exec_(self.tableWidget.viewport().mapToGlobal(position))

    #===========[Chức năng menu TableWidget]==========================
    def update_table_column(self, dialog_title, dialog_prompt, column_index):
        dialog = AddChangeDialog(dialog_title, dialog_prompt)
        
        if dialog.exec_() == QDialog.Accepted:
            new_data_list = dialog.get_data()
            if not new_data_list:
                return
            selected_rows = sorted(set(index.row() for index in self.tableWidget.selectedIndexes()))
            
            if not selected_rows:
                QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn ít nhất một hàng.")
                return

            for i, row in enumerate(selected_rows):
                new_value = new_data_list[i % len(new_data_list)]
                self.tableWidget.setItem(row, column_index, QTableWidgetItem(new_value))
                
            self.save_accounts_to_file()
            QMessageBox.information(None, "Thành công", f"Đã cập nhật {len(selected_rows)} tài khoản tại cột {column_index}.")


    def change_email_2(self):
        self.update_table_column(
            dialog_title="Nhập danh sách Email",
            dialog_prompt="Nhập email, mỗi dòng một email:",
            column_index=1
        )

    def change_proxy_2(self):
        self.update_table_column(
            dialog_title="Nhập danh sách Proxy",
            dialog_prompt="Nhập proxy, mỗi dòng một proxy (ip:port):",
            column_index=6
        )
    def copy_field(self):
        selected_rows = sorted(set(index.row() for index in self.tableWidget.selectedIndexes()))
        if not selected_rows:
            self.showMessageBox("Chưa chọn tài khoản nào!")
            return
        dialog = QDialog()
        dialog.setWindowTitle("Chọn trường muốn copy")
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Chọn trường:"))
        combo = QComboBox()
        fields = [
            "Email", "2FA", "App Passwords", "Proxy"
        ]
        combo.addItems(fields)
        layout.addWidget(combo)

        btn_ok = QPushButton("Copy")
        layout.addWidget(btn_ok)
        def on_copy():
            col_index = combo.currentIndex() + 1 
            values = []
            for row in selected_rows:
                item = self.tableWidget.item(row, col_index)
                if item:
                    values.append(item.text())
            if values:
                clipboard = QApplication.clipboard()
                clipboard.setText("\n".join(values))
                QMessageBox.information(None, "Thành công", f"✅ Đã copy {len(values)} giá trị vào clipboard!")
            dialog.accept()

        btn_ok.clicked.connect(on_copy)
        dialog.exec_()
    def on_tick_black(self):
        selected_rows = sorted(set(index.row() for index in self.tableWidget.selectedIndexes()))
        for row in reversed(selected_rows):
            checkbox = self.tableWidget.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)

    def off_tick_black(self):
        selected_rows = sorted(set(index.row() for index in self.tableWidget.selectedIndexes()))
        for row in reversed(selected_rows):
            checkbox = self.tableWidget.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
    def xoaTatCa(self):
        self.tableWidget.setRowCount(0)
    def xoaHang(self):
        selected_rows = sorted(set(index.row() for index in self.tableWidget.selectedIndexes()))
        for row in reversed(selected_rows):
            self.tableWidget.removeRow(row)
    def tatTatCaTick(self):
        self.toggle_all_checkboxes(QtCore.Qt.Unchecked)
    def moTatCaTick(self):
        self.toggle_all_checkboxes(QtCore.Qt.Checked)
    #===========[Hỗ Trợ]==========================
    def showMessageBox(self, text):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Thông Báo")
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        font = msg_box.font()
        font.setPointSize(14)
        msg_box.setFont(font)
        msg_box.setStyleSheet("QMessageBox{min-width: 300px;}")
        msg_box.exec()
    def toggle_all_checkboxes(self, state):
        for row in range(self.tableWidget.rowCount()):
            checkbox = self.tableWidget.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(state == QtCore.Qt.Checked)
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
