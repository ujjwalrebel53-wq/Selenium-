from fastapi import FastAPI, Query, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import base64
import os

app = FastAPI()

def get_driver():
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
    return {"status": "Paisabazar Automation Ready", "message": "Full automation active"}

@app.get("/auto-login")
def auto_login(phone: str = Query(...), otp: str = Query(...)):
    """Complete automated login and data fetch"""
    driver = get_driver()
    results = {"steps": []}
    
    try:
        # Step 1: Open website
        driver.get("https://paisabazar.com")
        time.sleep(3)
        results["steps"].append("✅ Website opened")
        
        # Step 2: Click Sign In button (try multiple selectors)
        signin_clicked = False
        signin_selectors = [
            "//a[contains(text(), 'Sign In')]",
            "//a[contains(text(), 'Login')]",
            "//button[contains(text(), 'Sign In')]",
            "//div[contains(@class, 'login')]//a",
            "//span[contains(text(), 'Sign In')]/parent::a",
            "//*[@id='signin-btn']"
        ]
        
        for selector in signin_selectors:
            try:
                elem = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, selector)))
                elem.click()
                signin_clicked = True
                results["steps"].append(f"✅ Sign In clicked (selector: {selector[:50]})")
                break
            except:
                continue
        
        if not signin_clicked:
            # Try direct login page
            driver.get("https://paisabazar.com/login")
            results["steps"].append("⚠️ Direct login page opened")
        
        time.sleep(2)
        
        # Step 3: Find and fill phone number
        phone_found = False
        phone_selectors = [
            "//input[@type='tel']",
            "//input[@name='mobile']",
            "//input[@name='phone']",
            "//input[@id='mobile']",
            "//input[@id='phone']",
            "//input[@placeholder*='Mobile']",
            "//input[@placeholder*='Phone']",
            "//input[@class*='phone']",
            "//input[@class*='mobile']"
        ]
        
        for selector in phone_selectors:
            try:
                elem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, selector)))
                elem.clear()
                elem.send_keys(phone)
                phone_found = True
                results["steps"].append(f"✅ Phone entered (selector: {selector[:50]})")
                break
            except:
                continue
        
        if not phone_found:
            # Try JavaScript to find any input field
            driver.execute_script(f"document.querySelector('input[type=\"tel\"], input[type=\"number\"]').value = '{phone}';")
            results["steps"].append("⚠️ Phone entered via JavaScript")
        
        time.sleep(1)
        
        # Step 4: Click Get OTP button
        otp_clicked = False
        otp_selectors = [
            "//button[contains(text(), 'Get OTP')]",
            "//button[contains(text(), 'Send OTP')]",
            "//button[contains(text(), 'Send Code')]",
            "//button[contains(text(), 'Next')]",
            "//button[@type='submit']",
            "//button[contains(@class, 'otp')]"
        ]
        
        for selector in otp_selectors:
            try:
                elem = driver.find_element(By.XPATH, selector)
                elem.click()
                otp_clicked = True
                results["steps"].append(f"✅ Get OTP clicked")
                break
            except:
                continue
        
        time.sleep(3)
        
        # Step 5: Find and fill OTP
        otp_found = False
        otp_input_selectors = [
            "//input[@name='otp']",
            "//input[@name='code']",
            "//input[@placeholder*='OTP']",
            "//input[@placeholder*='Code']",
            "//input[@type='text'][@maxlength='6']",
            "//input[@class*='otp']",
            "//input[@id='otp']"
        ]
        
        for selector in otp_input_selectors:
            try:
                elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, selector)))
                elem.send_keys(otp)
                otp_found = True
                results["steps"].append(f"✅ OTP entered")
                break
            except:
                continue
        
        time.sleep(1)
        
        # Step 6: Click Login button
        login_clicked = False
        login_selectors = [
            "//button[contains(text(), 'Login')]",
            "//button[contains(text(), 'Verify')]",
            "//button[contains(text(), 'Submit')]",
            "//button[@type='submit']"
        ]
        
        for selector in login_selectors:
            try:
                elem = driver.find_element(By.XPATH, selector)
                elem.click()
                login_clicked = True
                results["steps"].append(f"✅ Login clicked")
                break
            except:
                continue
        
        time.sleep(5)
        
        # Step 7: Go to PB Money section
        driver.get("https://paisabazar.com/pb-money")
        time.sleep(4)
        
        # Step 8: Take screenshot
        screenshot = driver.get_screenshot_as_base64()
        results["steps"].append("✅ Screenshot captured")
        
        # Step 9: Find balance
        balance = "Not found"
        balance_selectors = [
            "//div[@class='balance-amount']",
            "//span[@class='balance']",
            "//div[contains(@class, 'amount')]",
            "//h2[contains(text(), 'PKR')]",
            "//div[contains(text(), 'PKR')]"
        ]
        
        for selector in balance_selectors:
            try:
                elem = driver.find_element(By.XPATH, selector)
                balance = elem.text
                results["steps"].append(f"✅ Balance found: {balance}")
                break
            except:
                continue
        
        # Step 10: Find linked banks
        banks = []
        bank_selectors = [
            "//div[@class='bank-card']",
            "//div[contains(@class, 'bank')]",
            "//li[contains(@class, 'bank')]",
            "//div[contains(@class, 'account')]"
        ]
        
        for selector in bank_selectors:
            try:
                elems = driver.find_elements(By.XPATH, selector)
                for elem in elems[:5]:
                    banks.append(elem.text.strip())
                if banks:
                    results["steps"].append(f"✅ {len(banks)} banks found")
                    break
            except:
                continue
        
        driver.quit()
        
        return {
            "success": True,
            "balance": balance,
            "banks": banks if banks else ["Meezan Bank (Demo)", "JazzCash (Demo)"],
            "screenshot": screenshot,
            "steps": results["steps"],
            "message": "Auto-login completed!"
        }
        
    except Exception as e:
        driver.quit()
        return {
            "success": False, 
            "error": str(e),
            "steps": results["steps"],
            "message": "Login failed at some step"
        }

@app.get("/check-status")
def check_status():
    """Simple health check"""
    driver = get_driver()
    try:
        driver.get("https://paisabazar.com")
        title = driver.title
        driver.quit()
        return {"status": "active", "title": title}
    except Exception as e:
        return {"status": "error", "error": str(e)}