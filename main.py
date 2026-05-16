from fastapi import FastAPI, Query
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Selenium Ready", "message": "Use /send-otp and /verify-otp"}

@app.get("/send-otp")
def send_otp(phone: str = Query(...)):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://paisabazar.com")
        wait = WebDriverWait(driver, 30)
        
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

@app.get("/verify-otp")
def verify_otp(phone: str = Query(...), otp: str = Query(...)):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://paisabazar.com")
        wait = WebDriverWait(driver, 30)
        
        # Sign In
        signin = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Sign In')]")))
        signin.click()
        time.sleep(2)
        
        # Phone
        phone_input = wait.until(EC.presence_of_element_located((By.NAME, "mobile")))
        phone_input.send_keys(phone)
        time.sleep(1)
        
        # Get OTP
        otp_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Get OTP')]")
        otp_btn.click()
        time.sleep(2)
        
        # OTP
        otp_input = wait.until(EC.presence_of_element_located((By.NAME, "otp")))
        otp_input.send_keys(otp)
        time.sleep(1)
        
        # Login
        login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_btn.click()
        time.sleep(5)
        
        # PB Money
        driver.get("https://paisabazar.com/pb-money")
        time.sleep(3)
        
        # Balance
        balance_elem = driver.find_element(By.CLASS_NAME, "balance-amount")
        balance = balance_elem.text
        
        driver.quit()
        return {"success": True, "balance": balance}
        
    except Exception as e:
        driver.quit()
        return {"success": False, "error": str(e)}