from fastapi import FastAPI, Query
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import shutil
import subprocess

app = FastAPI()
driver = None

def get_driver():
    global driver
    if driver is None:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--single-process")
        options.add_argument("--window-size=1280,720")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")
        # selenium/standalone-chrome image mein Chrome already set hota hai
        driver = webdriver.Chrome(options=options)
    return driver

def reset_driver():
    global driver
    try:
        if driver:
            driver.quit()
    except:
        pass
    driver = None

@app.get("/")
def root():
    return {
        "status": "Paisabazar Automation Ready",
        "endpoints": {
            "1_start": "/start",
            "2_send_otp": "/send-otp?phone=9876543210",
            "3_verify_otp": "/verify-otp?phone=9876543210&otp=123456",
            "4_get_balance": "/get-balance",
            "full_flow": "/full-flow?phone=9876543210&otp=123456",
            "screenshot": "/screenshot",
            "reset": "/reset",
            "debug": "/debug-chrome"
        }
    }

@app.get("/debug-chrome")
def debug_chrome():
    results = {}
    results["chromium_which"] = shutil.which("chromium")
    results["chromium_browser_which"] = shutil.which("chromium-browser")
    results["chromedriver_which"] = shutil.which("chromedriver")
    results["google_chrome_which"] = shutil.which("google-chrome")
    results["google_chrome_stable"] = shutil.which("google-chrome-stable")

    try:
        r = subprocess.run(["find", "/usr", "-name", "chrom*", "-type", "f"],
                           capture_output=True, text=True, timeout=15)
        results["usr_chrom_files"] = r.stdout.strip().split("\n")
    except Exception as e:
        results["usr_chrom_files"] = str(e)

    try:
        r = subprocess.run(["google-chrome", "--version"],
                           capture_output=True, text=True, timeout=10)
        results["chrome_version"] = r.stdout.strip()
    except Exception as e:
        results["chrome_version"] = str(e)

    try:
        r = subprocess.run(["chromedriver", "--version"],
                           capture_output=True, text=True, timeout=10)
        results["chromedriver_version"] = r.stdout.strip()
    except Exception as e:
        results["chromedriver_version"] = str(e)

    return results

@app.get("/reset")
def reset():
    reset_driver()
    return {"success": True, "message": "Driver reset ho gaya"}

@app.get("/screenshot")
def screenshot():
    try:
        d = get_driver()
        img = d.get_screenshot_as_base64()
        return {"success": True, "current_url": d.current_url, "screenshot_base64": img}
    except Exception as e:
        reset_driver()
        return {"success": False, "error": str(e)}

@app.get("/start")
def start():
    try:
        reset_driver()
        d = get_driver()
        wait = WebDriverWait(d, 30)

        d.get("https://www.paisabazaar.com")
        time.sleep(4)

        signin_selectors = [
            "//a[contains(text(),'Sign In')]",
            "//a[contains(text(),'Login')]",
            "//button[contains(text(),'Sign In')]",
            "//a[contains(@href,'login')]",
            "//a[contains(@href,'signin')]",
            "//*[contains(@class,'login')]//a",
            "//*[contains(@class,'signin')]",
        ]

        clicked = False
        for selector in signin_selectors:
            try:
                elem = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                elem.click()
                clicked = True
                time.sleep(3)
                break
            except:
                continue

        screenshot_b64 = d.get_screenshot_as_base64()
        return {
            "success": clicked,
            "message": "Sign In page khul gaya" if clicked else "Sign In button nahi mila",
            "current_url": d.current_url,
            "screenshot": screenshot_b64
        }
    except Exception as e:
        reset_driver()
        return {"success": False, "error": str(e)}

@app.get("/send-otp")
def send_otp(phone: str = Query(...)):
    try:
        d = get_driver()
        wait = WebDriverWait(d, 30)

        phone_selectors = [
            "//input[@type='tel']",
            "//input[@name='mobile']",
            "//input[@name='phone']",
            "//input[@id='mobile']",
            "//input[@id='phone']",
            "//input[contains(@placeholder,'Mobile')]",
            "//input[contains(@placeholder,'Phone')]",
            "//input[contains(@placeholder,'mobile')]",
            "//input[contains(@placeholder,'Enter')]",
        ]

        phone_input = None
        for selector in phone_selectors:
            try:
                phone_input = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                if phone_input.is_displayed():
                    break
            except:
                continue

        if not phone_input:
            return {"success": False, "error": "Phone input nahi mila", "current_url": d.current_url, "screenshot": d.get_screenshot_as_base64()}

        phone_input.clear()
        phone_input.send_keys(phone)
        time.sleep(1)

        otp_btn_selectors = [
            "//button[contains(text(),'Get OTP')]",
            "//button[contains(text(),'Send OTP')]",
            "//button[contains(text(),'SEND OTP')]",
            "//button[contains(text(),'GET OTP')]",
            "//button[contains(text(),'Next')]",
            "//button[contains(text(),'Continue')]",
            "//button[@type='submit']",
            "//input[@type='submit']",
        ]

        btn_clicked = False
        for selector in otp_btn_selectors:
            try:
                btn = d.find_element(By.XPATH, selector)
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    btn_clicked = True
                    time.sleep(3)
                    break
            except:
                continue

        return {
            "success": btn_clicked,
            "message": f"OTP bhej diya {phone} pe" if btn_clicked else "OTP button nahi mila",
            "current_url": d.current_url,
            "screenshot": d.get_screenshot_as_base64()
        }
    except Exception as e:
        reset_driver()
        return {"success": False, "error": str(e)}

@app.get("/verify-otp")
def verify_otp(phone: str = Query(...), otp: str = Query(...)):
    try:
        d = get_driver()
        wait = WebDriverWait(d, 30)

        otp_selectors = [
            "//input[@name='otp']",
            "//input[@id='otp']",
            "//input[contains(@placeholder,'OTP')]",
            "//input[contains(@placeholder,'otp')]",
            "//input[contains(@placeholder,'Code')]",
            "//input[@maxlength='6']",
            "//input[@maxlength='4']",
            "//input[@type='number']",
            "//input[@type='tel']",
        ]

        otp_input = None
        for selector in otp_selectors:
            try:
                otp_input = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                if otp_input.is_displayed():
                    break
            except:
                continue

        if not otp_input:
            return {"success": False, "error": "OTP input nahi mila", "current_url": d.current_url, "screenshot": d.get_screenshot_as_base64()}

        otp_input.clear()
        otp_input.send_keys(otp)
        time.sleep(1)

        verify_selectors = [
            "//button[contains(text(),'Verify')]",
            "//button[contains(text(),'Login')]",
            "//button[contains(text(),'Submit')]",
            "//button[contains(text(),'VERIFY')]",
            "//button[contains(text(),'Confirm')]",
            "//button[@type='submit']",
        ]

        for selector in verify_selectors:
            try:
                btn = d.find_element(By.XPATH, selector)
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    break
            except:
                continue

        time.sleep(5)
        current_url = d.current_url
        login_failed = "login" in current_url.lower() or "signin" in current_url.lower()

        return {
            "success": not login_failed,
            "message": "Login ho gaya!" if not login_failed else "Login fail - OTP galat ho sakta hai",
            "current_url": current_url,
            "screenshot": d.get_screenshot_as_base64()
        }
    except Exception as e:
        reset_driver()
        return {"success": False, "error": str(e)}

@app.get("/get-balance")
def get_balance():
    try:
        d = get_driver()
        d.get("https://www.paisabazaar.com/pb-money")
        time.sleep(5)

        balance = "Not found"
        for selector in ["//*[contains(@class,'balance')]", "//*[contains(@class,'amount')]", "//*[contains(text(),'₹')]"]:
            try:
                elem = d.find_element(By.XPATH, selector)
                if elem.text.strip():
                    balance = elem.text.strip()
                    break
            except:
                continue

        banks = []
        for selector in ["//*[contains(@class,'bank')]", "//*[contains(@class,'account')]"]:
            try:
                elems = d.find_elements(By.XPATH, selector)
                for elem in elems[:5]:
                    text = elem.text.strip()
                    if text and len(text) > 3:
                        banks.append(text)
                if banks:
                    break
            except:
                continue

        return {"success": True, "balance": balance, "banks": banks, "current_url": d.current_url, "screenshot": d.get_screenshot_as_base64()}
    except Exception as e:
        reset_driver()
        return {"success": False, "error": str(e)}

@app.get("/full-flow")
def full_flow(phone: str = Query(...), otp: str = Query(...)):
    results = {"steps": [], "success": False}

    s = start()
    results["steps"].append({"step": "Start", "result": s})
    if not s.get("success"):
        return results
    time.sleep(2)

    send = send_otp(phone)
    results["steps"].append({"step": "Send OTP", "result": send})
    if not send.get("success"):
        return results
    time.sleep(3)

    verify = verify_otp(phone, otp)
    results["steps"].append({"step": "Verify OTP", "result": verify})
    if not verify.get("success"):
        return results
    time.sleep(3)

    bal = get_balance()
    results["steps"].append({"step": "Get Balance", "result": bal})
    results["success"] = True
    results["balance"] = bal.get("balance", "N/A")
    results["banks"] = bal.get("banks", [])
    return results

@app.on_event("shutdown")
def shutdown():
    reset_driver()
