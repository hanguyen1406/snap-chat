from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Đường dẫn tới ChromeDriver

# Hàm mở cửa sổ trình duyệt mới và thiết lập vị trí
def open_browser_and_set_position(x, y, width, height):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_position(x, y)
    driver.set_window_size(width, height)
    return driver

# Kích thước và khoảng cách giữa các cửa sổ
window_width = 100
window_height = 400
gap = 40

# Số lượng cửa sổ muốn mở
num_windows = 7

# Danh sách các driver cho các cửa sổ
drivers = []

# Thiết lập vị trí và mở các cửa sổ
for i in range(num_windows):
    row = i // 7  # Tính số hàng (0-based index)
    col = i % 7  # Tính số cột (0-based index)
    
    x_position = col * (window_width + gap)
    y_position = row * (window_height + gap)
    print(f"Window {i}: ({x_position}, {y_position})")

    driver = open_browser_and_set_position(x_position, y_position, window_width, window_height)
    driver.get("https://www.example.com")  # Mở một trang web để kiểm tra
    drivers.append(driver)

# Thêm thời gian để quan sát các cửa sổ đã mở và sắp xếp
time.sleep(10)

# Đóng tất cả các cửa sổ trình duyệt
for driver in drivers:
    driver.quit()
