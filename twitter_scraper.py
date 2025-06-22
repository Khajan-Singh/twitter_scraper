from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

SEARCH_TEXT = "AI cybersecurity trends"
NUM_TWEETS_TO_SCRAPE = 5

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
    except:
        print("🍪 No cookie banner found or already handled")

    # Activate search bar using `/` key
    body = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    body.send_keys('/')
    time.sleep(1)

    # Enter search query
    search_input = driver.switch_to.active_element
    search_input.clear()
    search_input.send_keys(SEARCH_TEXT)
    search_input.send_keys(Keys.ENTER)

    print("🔍 Searching...")
    time.sleep(5)  # wait for results

    # Scroll to load more tweets
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 600);")
        time.sleep(2)

    # Scrape tweets
    tweets = driver.find_elements(By.XPATH, '//article')[:NUM_TWEETS_TO_SCRAPE]
    tweet_data = []

    for idx, tweet in enumerate(tweets):
        try:
            text_elements = tweet.find_elements(By.XPATH, './/div[@data-testid="tweetText"]//span')
            tweet_text = ' '.join([el.text.strip() for el in text_elements if el.text.strip()])
            print(f"📝 Tweet {idx+1}: {tweet_text[:60]}...")
            tweet_data.append({"index": idx+1, "text": tweet_text})
        except:
            print(f"⚠️ Skipped tweet {idx+1} (no text found)")

    # Save tweets to JSON
    with open("tweets.json", "w", encoding="utf-8") as f:
        json.dump(tweet_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(tweet_data)} tweets to tweets.json")
    time.sleep(10)

except Exception as e:
    print(f"Error: {e}")

# driver.quit()
