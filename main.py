from fastapi import FastAPI, Query, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import base64
import os

app = FastAPI()

# Global driver instance (optional, for better performance)
driver = None

def get_driver():
    global driver
    if driver is None:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=options)
    return driver

@app.get("/")
def root():
    return {
        "status": "Paisabazar Automation Ready",
        "endpoints": {
            "start": "/start",
            "send_otp": "/send-otp?phone=NUMBER",
            "verify_otp": "/verify-otp?phone=NUMBER&otp=CODE",
            "get_balance": "/get-balance"
        }
    }

@app.get("/start")
def start_session():
    """Start browser session and click Sign In button"""
    driver = get_driver()
    try:
        driver.get("https://paisabazar.com")
        wait = WebDriverWait(driver, 30)
        
        # Find and click Sign In button
        signin_selectors = [
            "//a[contains(text(), 'Sign In')]",
            "//a[contains(text(), 'Login')]",
            "//button[contains(text(), 'Sign In')]",
            "//div[@class='signin-btn']//a",
            "//span[contains(text(), 'Sign In')]"
        ]
        
        for selector in signin_selectors:
            try:
                signin = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                signin.click()
                return {"success": True, "message": "Sign In page opened"}
            except:
                continue
        
        return {"success": False, "error": "Sign In button not found"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/send-otp")
def send_otp(phone: str = Query(...)):
    """Enter mobile number and request OTP"""
    driver = get_driver()
    try:
        wait = WebDriverWait(driver, 30)
        
        # Find phone input field
        phone_selectors = [
            "//input[@type='tel']",
            "//input[@name='mobile']",
            "//input[@name='phone']",
            "//input[@id='mobile']",
            "//input[@placeholder*='Mobile']",
            "//input[@placeholder*='Phone']"
        ]
        
        phone_input = None
        for selector in phone_selectors:
            try:
                phone_input = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                break
            except:
                continue
        
        if not phone_input:
            return {"success": False, "error": "Phone input field not found"}
        
        phone_input.clear()
        phone_input.send_keys(phone)
        time.sleep(1)
        
        # Find and click Get OTP button
        otp_btn_selectors = [
            "//button[contains(text(), 'Get OTP')]",
            "//button[contains(text(), 'Send OTP')]",
            "//button[contains(text(), 'Send Code')]",
            "//button[contains(text(), 'Next')]"
        ]
        
        for selector in otp_btn_selectors:
            try:
                otp_btn = driver.find_element(By.XPATH, selector)
                otp_btn.click()
                return {"success": True, "message": f"OTP sent to {phone}"}
            except:
                continue
        
        return {"success": False, "error": "Get OTP button not found"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/verify-otp")
def verify_otp(phone: str = Query(...), otp: str = Query(...)):
    """Enter OTP and complete login"""
    driver = get_driver()
    try:
        wait = WebDriverWait(driver, 30)
        
        # Find OTP input field
        otp_selectors = [
            "//input[@name='otp']",
            "//input[@name='code']",
            "//input[@placeholder*='OTP']",
            "//input[@type='text'][@maxlength='6']"
        ]
        
        otp_input = None
        for selector in otp_selectors:
            try:
                otp_input = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                break
            except:
                continue
        
        if not otp_input:
            return {"success": False, "error": "OTP input field not found"}
        
        otp_input.send_keys(otp)
        time.sleep(1)
        
        # Find and click Login button
        login_selectors = [
            "//button[contains(text(), 'Login')]",
            "//button[contains(text(), 'Verify')]",
            "//button[contains(text(), 'Submit')]",
            "//button[@type='submit']"
        ]
        
        for selector in login_selectors:
            try:
                login_btn = driver.find_element(By.XPATH, selector)
                login_btn.click()
                break
            except:
                continue
        
        time.sleep(5)
        
        # Check if login successful
        if "login" in driver.current_url.lower():
            return {"success": False, "error": "Login failed - Invalid OTP"}
        
        return {"success": True, "message": "Login successful"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/get-balance")
def get_balance():
    """Fetch PB Money balance and linked banks"""
    driver = get_driver()
    try:
        # Go to PB Money section
        driver.get("https://paisabazar.com/pb-money")
        time.sleep(5)
        
        # Take screenshot
        screenshot = driver.get_screenshot_as_base64()
        
        # Find balance
        balance_selectors = [
            "//div[@class='balance-amount']",
            "//span[@class='balance']",
            "//div[contains(@class, 'amount')]",
            "//h2[contains(text(), 'PKR')]"
        ]
        
        balance = "Not found"
        for selector in balance_selectors:
            try:
                balance_elem = driver.find_element(By.XPATH, selector)
                balance = balance_elem.text
                break
            except:
                continue
        
        # Find linked banks
        banks = []
        bank_selectors = [
            "//div[@class='bank-card']",
            "//div[contains(@class, 'bank')]",
            "//li[contains(@class, 'bank-item')]"
        ]
        
        for selector in bank_selectors:
            try:
                bank_elems = driver.find_elements(By.XPATH, selector)
                for bank in bank_elems:
                    banks.append(bank.text)
                if banks:
                    break
            except:
                continue
        
        return {
            "success": True,
            "balance": balance,
            "banks": banks if banks else ["No banks linked"],
            "screenshot": screenshot
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/full-flow")
def full_flow(phone: str = Query(...), otp: str = Query(...)):
    """Complete flow: start -> send-otp -> verify-otp -> get-balance"""
    driver = get_driver()
    results = {}
    
    try:
        # Step 1: Start and click Sign In
        driver.get("https://paisabazar.com")
        wait = WebDriverWait(driver, 30)
        
        signin = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Sign In')]")))
        signin.click()
        results["step1"] = "Sign In clicked"
        time.sleep(2)
        
        # Step 2: Enter phone
        phone_input = wait.until(EC.presence_of_element_located((By.NAME, "mobile")))
        phone_input.send_keys(phone)
        results["step2"] = "Phone entered"
        time.sleep(1)
        
        # Step 3: Get OTP
        otp_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Get OTP')]")
        otp_btn.click()
        results["step3"] = "OTP requested"
        time.sleep(2)
        
        # Step 4: Enter OTP
        otp_input = wait.until(EC.presence_of_element_located((By.NAME, "otp")))
        otp_input.send_keys(otp)
        results["step4"] = "OTP entered"
        time.sleep(1)
        
        # Step 5: Login
        login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_btn.click()
        results["step5"] = "Login clicked"
        time.sleep(5)
        
        # Step 6: Get PB Money
        driver.get("https://paisabazar.com/pb-money")
        time.sleep(3)
        
        # Get balance
        balance = driver.find_element(By.CLASS_NAME, "balance-amount").text
        results["balance"] = balance
        
        # Get banks
        banks = []
        bank_elems = driver.find_elements(By.CLASS_NAME, "bank-name")
        for bank in bank_elems:
            banks.append(bank.text)
        results["banks"] = banks
        
        # Screenshot
        screenshot = driver.get_screenshot_as_base64()
        
        return {
            "success": True,
            "results": results,
            "screenshot": screenshot
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "step": results}

@app.on_event("shutdown")
def shutdown():
    global driver
    if driver:
        driver.quit()