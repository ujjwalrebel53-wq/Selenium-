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

@app.get("/check")
def check():
    return {"status": "alive"}

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
        
        # Enter phone
        phone_input = wait.until(EC.presence_of_element_located((By.NAME, "mobile")))
        phone_input.send_keys(phone)
        time.sleep(1)
        
        # Click Get OTP
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
        
        # Sign In
        signin = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Sign In')]")))
        signin.click()
        time.sleep(2)
        
        # Enter phone
        phone_input = wait.until(EC.presence_of_element_located((By.NAME, "mobile")))
        phone_input.send_keys(phone)
        time.sleep(1)
        
        # Get OTP
        otp_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Get OTP')]")
        otp_btn.click()
        time.sleep(2)
        
        # Enter OTP
        otp_input = wait.until(EC.presence_of_element_located((By.NAME, "otp")))
        otp_input.send_keys(otp)
        time.sleep(1)
        
        # Login
        login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_btn.click()
        time.sleep(5)
        
        # Get balance
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
