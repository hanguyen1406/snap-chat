import os
import sys
import time
import random
import string
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Ensure output directory exists
OUTPUT_DIR = "fun_capcha_data"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
questions_dir = os.path.join(OUTPUT_DIR, "questions")
images_dir = os.path.join(OUTPUT_DIR, "images")
if not os.path.exists(questions_dir): os.makedirs(questions_dir)
if not os.path.exists(images_dir): os.makedirs(images_dir)

# GLOBAL DRIVER INSTALL - Fixes threading race condition
try:
    print("Installing/Updating Chrome Driver globally...")
    DRIVER_PATH = ChromeDriverManager().install()
except Exception as e:
    print(f"Global driver install failed: {e}")
    DRIVER_PATH = None

def generate_random_string(length=8):
    # First character must be a letter
    first_char = random.choice(string.ascii_letters)
    # Remaining characters can be letters or digits
    remaining_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=length - 1))
    return first_char + remaining_chars

def generate_random_name():
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "David", "Eve", "Frank"]
    last_names = ["Smith", "Doe", "Johnson", "Brown", "Williams", "Jones", "Miller", "Davis"]
    return random.choice(first_names), random.choice(last_names)

def generate_random_email():
    name = generate_random_string(10)
    return f"{name}@gmail.com"

def run_crawler(thread_id):
    # Window Layout Config
    disp_width = 400
    disp_height = 800
    cols = 4 # Adjust based on screen size
    
    # zero-indexed id for math
    tid = thread_id - 1
    pos_x = (tid % cols) * disp_width
    pos_y = (tid // cols) * disp_height

    while True: # Outer loop for Driver Restart
        print(f"[Thread {thread_id}] Initializing Chrome Driver...")
        driver = None
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--log-level=3")
            # Remove start-maximized to respect set_window_rect
            
            # Use pre-installed path if available
            if DRIVER_PATH:
                service = ChromeService(DRIVER_PATH)
            else:
                service = ChromeService(ChromeDriverManager().install())

            driver = webdriver.Chrome(service=service, options=options)
            
            # Set Window Position and Size
            try:
                driver.set_window_rect(x=pos_x, y=pos_y, width=disp_width, height=disp_height)
            except Exception as e:
                # print(f"[Thread {thread_id}] Could not set window rect: {e}")
                pass

            # Navigation Loop
            while True: 
                try:
                    print(f"[Thread {thread_id}] Navigating to Signup...")
                    driver.get("https://accounts.snapchat.com/v2/signup?continue=%2Faccounts%2Fsso%3Fclient_id%3Dlens-studio-web")
                    
                    # Handle Cookie Consent
                    try:
                        accept_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//span[text()='Accept All']"))
                        )
                        accept_button.click()
                    except:
                        pass

                    wait = WebDriverWait(driver, 15)
                    
                    def safe_send_keys(by, value, text, name_log):
                        try:
                            element = wait.until(EC.visibility_of_element_located((by, value)))
                            driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            element.clear()
                            element.send_keys(text)
                            time.sleep(random.uniform(0.1, 0.3))
                            return True
                        except:
                            return False

                    # Fill Form
                    fname, lname = generate_random_name()
                    safe_send_keys(By.NAME, "firstName", fname, "First Name")
                    safe_send_keys(By.NAME, "lastName", lname, "Last Name")
                    
                    try: 
                        u_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
                        if u_field.is_displayed():
                             u_len = random.randint(8, 12)
                             u_field.send_keys(generate_random_string(u_len))
                    except: pass

                    safe_send_keys(By.NAME, "password", generate_random_string(12) + "Aa1!", "Password")
                    safe_send_keys(By.NAME, "email", generate_random_email(), "Email")
                    
                    # Birthday
                    try:
                        month_elem = wait.until(EC.presence_of_element_located((By.ID, "month")))
                        Select(month_elem).select_by_value(str(random.randint(1, 12)))
                        safe_send_keys(By.ID, "day", str(random.randint(1, 28)), "Day")
                        safe_send_keys(By.ID, "year", str(random.randint(1995, 2002)), "Year")
                    except: pass

                    # Submit
                    try:
                        submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
                        driver.execute_script("arguments[0].click();", submit_btn)
                    except: pass

                    time.sleep(5)
                    # Captcha Hunt
                    print(f"[Thread {thread_id}] Checking for Captcha...")
                    # Wait up to 10s for iframe
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
                    except:
                         # No iframe found, reload immediately
                        continue 

                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    
                    found_captcha = False
                    # for i, iframe in enumerate(iframes):
                    try:
                        src = iframes[0].get_attribute("src")
                        # Relaxed check: if we are iterating iframes, check inside for buttons
                        # Or strictly check src if possible. Let's keep src check for robustness unless it fails.
                        # User previously removed src check? Let's keep it safe.
                        # Actually user code replacement REMOVED the src check lines in the manual edit attempt. 
                        # But let's keep the button count logic as the primary trigger.
                        
                        # Switching to iframe to check content
                        driver.switch_to.frame(iframes[0])
                        time.sleep(1)
                        iframes1 = driver.find_elements(By.TAG_NAME, "iframe")
                        driver.switch_to.frame(iframes1[0])
                        time.sleep(1)
                        iframes2 = driver.find_elements(By.TAG_NAME, "iframe")
                        driver.switch_to.frame(iframes2[0])
                        time.sleep(1)


                        # Check buttons (User Logic: 0=Reload, 1=Click)
                        buttons = driver.find_elements(By.CSS_SELECTOR, "button")
                        
                        if len(buttons) == 0:
                            # Not the right iframe or captcha not loaded
                            driver.switch_to.default_content()
                            continue 
                        else:
                            print(f"[Thread {thread_id}] Found {len(buttons)} buttons in iframe. Clicking Start...")
                            found_captcha = True
                            buttons[0].click()
                            time.sleep(4) # Wait for game load

                            # Extract Data
                            ts = int(time.time())
                            
                            # 1. Question Text
                            try:
                                question_text = ""
                                headers = driver.find_elements(By.CSS_SELECTOR, "#description, div[role='heading'], h2, .challenge-instructions-container")
                                for h in headers:
                                    if h.is_displayed() and h.text.strip():
                                        question_text += h.text.strip() + " "
                                
                                if question_text:
                                    with open(os.path.join(questions_dir, f"q_{ts}_{thread_id}.txt"), "w", encoding="utf-8") as f:
                                        f.write(question_text)
                                    print(f"[Thread {thread_id}] Saved question: {question_text[:30]}...")
                            except: pass
                            
                            # 2. Scrape Images (Carousel vs Grid)
                            try:
                                # Check for Arrows
                                next_arrow = None
                                try:
                                    next_arrow = driver.find_elements(By.CSS_SELECTOR, "a.right-arrow")
                                except: pass

                                if next_arrow:
                                    print(f"[Thread {thread_id}] Rotating/Cycling Captcha detected.")
                                    for step in range(8): # Max 15 steps
                                        # Capture
                                        try:
                                            game = driver.find_element(By.CSS_SELECTOR, "#game-core-frame, #root, body")
                                            game.screenshot(os.path.join(images_dir, f"game_t{thread_id}_{ts}_step{step}.png"))
                                        except: pass
                                        
                                        # Click Next
                                        try:
                                            btn = driver.find_element(By.CSS_SELECTOR, "a.right-arrow")
                                            btn.click()
                                            time.sleep(0.4)
                                        except:
                                            break # End of carousel?
                                else:
                                    pass
                                    # Single Grid
                                    # try:
                                    #     game = driver.find_element(By.ID, "game_children_ul")
                                    # except:
                                    #     try: game = driver.find_element(By.ID, "game-core-frame")
                                    #     except: game = driver.find_element(By.CSS_SELECTOR, "body")
                                    
                                    # game.screenshot(os.path.join(images_dir, f"game_t{thread_id}_{ts}.png"))
                                    # print(f"[Thread {thread_id}] Saved single screenshot.")

                            except Exception as e:
                                print(f"[Thread {thread_id}] Screenshot failed: {e}")

                            driver.switch_to.default_content()
                            driver.quit() 
                            break # Stop checking iframes if we successfully processed one
                    
                    except Exception as e:
                        print(f"[Thread {thread_id}] Error inspecting iframe: {e}")
                        driver.switch_to.default_content()
                    
                    if not found_captcha:
                        print(f"[Thread {thread_id}] No captcha buttons found, reloading...")
                    else:
                        print(f"[Thread {thread_id}] Captcha processed, reloading...")
                    # Restart Loop
                    time.sleep(0.5) 
                     # Close current driver

                except Exception as e:
                    print(f"[Thread {thread_id}] Page Error: {e}")
                    # If window is closed, this will raise error and go to outer loop to restart driver
                    if "no such window" in str(e):
                        raise e 
                    time.sleep(1)

        except Exception as e:
            print(f"[Thread {thread_id}] Driver Crash/Restart: {e}")
            try: 
                if driver: driver.quit() 
            except: pass
            time.sleep(3)

def main():
    try:
        user_in = input("Nhap so luong luong (Enter number of threads): ")
        num_threads = int(user_in)
    except ValueError:
        print("Invalid input, defaulting to 1")
        num_threads = 1

    print(f"Starting {num_threads} threads...")
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=run_crawler, args=(i+1,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
