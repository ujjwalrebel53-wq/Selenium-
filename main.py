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
    return {"status": "Paisabazar Bot Ready", "endpoints": ["/send-otp", "/verify", "/balance"]}

@app.get("/send-otp")
def send_otp(phone: str = Query(...)):
    driver = get_driver()
    try:
        driver.get("https://paisabazar.pk")
        wait = WebDriverWait(driver, 20)
        
        # Click Sign In using id you found
        signin = wait.until(EC.element_to_be_clickable((By.ID, "pbLogin")))
        signin.click()
        time.sleep(2)
        
        # Phone field (common selectors)
        phone_selectors = [
            "//input[@type='tel']",
            "//input[@name='mobile']",
            "//input[@name='phone']",
            "//input[@id='mobile']",
            "//input[@id='phone']"
        ]
        
        phone_input = None
        for selector in phone_selectors:
            try:
                phone_input = driver.find_element(By.XPATH, selector)
                break
            except:
                continue
        
        if not phone_input:
            driver.quit()
            return {"success": False, "error": "Phone field not found"}
        
        phone_input.send_keys(phone)
        time.sleep(1)
        
        # Get OTP button
        otp_selectors = [
            "//button[contains(text(), 'Get OTP')]",
            "//button[contains(text(), 'Send OTP')]",
            "//button[contains(text(), 'Next')]"
        ]
        
        for selector in otp_selectors:
            try:
                driver.find_element(By.XPATH, selector).click()
                break
            except:
                continue
        
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
        driver.get("https://paisabazar.pk")
        wait = WebDriverWait(driver, 20)
        
        # Sign In
        signin = wait.until(EC.element_to_be_clickable((By.ID, "pbLogin")))
        signin.click()
        time.sleep(2)
        
        # Phone
        phone_input = wait.until(EC.presence_of_element_located((By.NAME, "mobile")))
        phone_input.send_keys(phone)
        time.sleep(1)
        
        # Get OTP
        driver.find_element(By.XPATH, "//button[contains(text(), 'Get OTP')]").click()
        time.sleep(2)
        
        # OTP
        otp_input = driver.find_element(By.NAME, "otp")
        otp_input.send_keys(otp)
        time.sleep(1)
        
        # Login
        driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
        time.sleep(5)
        
        # Go to PB Money
        driver.get("https://paisabazar.pk/pb-money")
        time.sleep(3)
        
        # Get balance
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
        driver.get("https://paisabazar.pk/pb-money")
        time.sleep(4)
        balance = driver.find_element(By.CLASS_NAME, "balance-amount").text
        screenshot = driver.get_screenshot_as_base64()
        driver.quit()
        return {"success": True, "balance": balance, "screenshot": screenshot}
    except Exception as e:
        driver.quit()
        return {"success": False, "error": str(e)}
