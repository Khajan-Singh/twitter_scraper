from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

SEARCH_TEXT = "AI cybersecurity trends"

options = Options()
options.add_argument("user-data-dir=C:/selenium/chrome-profile")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    driver.get("https://x.com/explore")
    time.sleep(5)  # wait for page to load

    # Close cookie banner if present
    try:
        cookie_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//div[contains(text(), "Accept")]')))
        cookie_button.click()
        print("🍪 Cookie banner closed")
    except Exception:
        print("🍪 No cookie banner found or already handled")

    # Send '/' key to open search input (keyboard shortcut)
    body = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    body.send_keys('/')
    time.sleep(1)  # wait for search input to appear

    # The search input should now be focused as active element
    search_input = driver.switch_to.active_element
    search_input.clear()
    search_input.send_keys(SEARCH_TEXT)
    search_input.send_keys(Keys.ENTER)

    print("✅ Search executed successfully!")
    time.sleep(10)  # Keep browser open to see results

except Exception as e:
    print(f"❌ Error: {e}")

# driver.quit()
