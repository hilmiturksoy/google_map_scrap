from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
import os
import traceback

def get_business_data(kategori):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")

    # Mevcut dizin yolunu al
    base_path = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(base_path, "chromedriver.exe")

    try:
        # ChromeDriver'ı doğru yoldan çalıştır
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
    except Exception as e:
        with open("log.txt", "w") as f:
            f.write(traceback.format_exc())
        return []

    driver.get("https://www.google.com/maps")
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchboxinput"))
        )
        search_box.clear()
        search_box.send_keys(kategori)
        search_box.send_keys(Keys.RETURN)
        time.sleep(random.uniform(5, 8))
    except Exception as e:
        print(f"Arama kutusu bulunamadı! Hata: {e}")
        driver.quit()
        return []

    business_data = []
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".Nv2PK"))
        )
        scrollable_div = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
        )
        for _ in range(15):
            driver.execute_script("arguments[0].scrollTop += 500;", scrollable_div)
            time.sleep(random.uniform(3, 5))

        business_list = driver.find_elements(By.CSS_SELECTOR, ".Nv2PK")
        for i in range(len(business_list)):
            try:
                business_url = business_list[i].find_element(By.TAG_NAME, "a").get_attribute("href")
                driver.execute_script(f"window.open('{business_url}', '_blank');")
                driver.switch_to.window(driver.window_handles[1])

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "DUwDvf"))
                )
                name = driver.find_element(By.CLASS_NAME, "DUwDvf").text
                address = phone = "Bilinmiyor"
                try:
                    detail_divs = driver.find_elements(By.CLASS_NAME, "rogA2c")
                    details = [elem.text.strip() for elem in detail_divs]
                    for text in details:
                        if text.startswith("(") or text.replace(" ", "").isdigit():
                            phone = text
                        elif any(word in text.lower() for word in ["cad.", "sok.", "no:", "/", "bulvar", "mahalle"]):
                            address = text
                except:
                    pass

                business_data.append({"Ad": name, "Adres": address, "Telefon": phone})
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except:
                continue
    except:
        print("İşletme bilgileri alınamadı.")

    driver.quit()
    return business_data
