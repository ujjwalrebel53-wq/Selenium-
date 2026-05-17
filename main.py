from fastapi import FastAPI, Query
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64

app = FastAPI()

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

@app.get("/")
def root():
    return {"status": "Paisabazar Automation Ready", "message": "Service is running"}

@app.get("/debug")
def debug():
    """Page ka HTML dekho - Selectors find karne ke liye"""
    driver = get_driver()
    try:
        driver.get("https://paisabazar.com")
        time.sleep(5)
        html = driver.page_source[:5000]
        return {
            "success": True,
            "title": driver.title,
            "url": driver.current_url,
            "html_preview": html,
            "page_loaded": True
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        driver.quit()

@app.get("/send-otp")
def send_otp(phone: str = Query(...)):
    driver = get_driver()
    try:
        driver.get("https://paisabazar.com")
        wait = WebDriverWait(driver, 15)
        
        # Click Sign In
        signin = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Sign In')]")))
        signin.click()
        time.sleep(2)
        
        # Phone input
        phone_input = wait.until(EC.presence_of_element_located((By.NAME, "mobile")))
        phone_input.send_keys(phone)
        time.sleep(1)
        
        # Get OTP button
        otp_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Get OTP')]")
        otp_btn.click()
        time.sleep(3)
        
        driver.quit()
        return {"success": True, "message": f"OTP sent to {phone}"}
    except Exception as e:
        driver.quit()
        return {"success": False, "error": str(e)}

@app.get("/verify")
def verify(phone: str = Query(...), otp: str = Query(...)):
    driver = get_driver()
    try:
        driver.get("https://paisabazar.com")
        wait = WebDriverWait(driver, 15)
        
        signin = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Sign In')]")))
        signin.click()
        time.sleep(2)
        
        phone_input = wait.until(EC.presence_of_element_located((By.NAME, "mobile")))
        phone_input.send_keys(phone)
        time.sleep(1)
        
        otp_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Get OTP')]")
        otp_btn.click()
        time.sleep(2)
        
        otp_input = wait.until(EC.presence_of_element_located((By.NAME, "otp")))
        otp_input.send_keys(otp)
        time.sleep(1)
        
        login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_btn.click()
        time.sleep(5)
        
        driver.get("https://paisabazar.com/pb-money")
        time.sleep(3)
        
        balance = driver.find_element(By.CLASS_NAME, "balance-amount").text
        
        driver.quit()
        return {"success": True, "balance": balance}
    except Exception as e:
        driver.quit()
        return {"success": False, "error": str(e)}

@app.get("/balance")
def balance():
    driver = get_driver()
    try:
        driver.get("https://paisabazar.com/pb-money")
        time.sleep(3)
        balance = driver.find_element(By.CLASS_NAME, "balance-amount").text
        screenshot = driver.get_screenshot_as_base64()
        driver.quit()
        return {"success": True, "balance": balance, "screenshot": screenshot}
    except Exception as e:
        driver.quit()
        return {"success": False, "error": str(e)}
