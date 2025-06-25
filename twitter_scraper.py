from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

SEARCH_TEXT = "AI cybersecurity trends"
NUM_TWEETS_TO_SCRAPE = 20

# Setup Chrome with your profile
options = Options()
options.add_argument("user-data-dir=C:/selenium/chrome-profile")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    driver.get("https://x.com/explore")
    time.sleep(5)

    # Close cookie banner if present
    try:
        cookie_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//div[contains(text(), "Accept")]')))
        cookie_button.click()
        print("🍪 Cookie banner closed")
    except:
        print("🍪 No cookie banner found or already handled")

    # Activate search bar with `/` and enter search query
    body = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    body.send_keys('/')
    time.sleep(1)

    search_input = driver.switch_to.active_element
    search_input.clear()
    search_input.send_keys(SEARCH_TEXT)
    search_input.send_keys(Keys.ENTER)

    print("🔍 Searching...")
    time.sleep(5)

    # Scrape tweets dynamically
    tweet_data = []
    scroll_attempts = 0

    while len(tweet_data) < NUM_TWEETS_TO_SCRAPE and scroll_attempts < 10:
        articles = driver.find_elements(By.XPATH, '//article')

        for tweet in articles:
            if len(tweet_data) >= NUM_TWEETS_TO_SCRAPE:
                break
            try:
                # Try clicking "Show more" if present
                try:
                    show_more = tweet.find_element(By.XPATH, './/button[@data-testid="tweet-text-show-more-link"]')
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_more)
                    driver.execute_script("arguments[0].click();", show_more)
                    time.sleep(0.5)
                    print("🔽 Expanded tweet")
                except:
                    pass  # No "Show more" button

                # Extract tweet text
                text_elements = tweet.find_elements(By.XPATH, './/div[@data-testid="tweetText"]//span')
                tweet_text = ' '.join([el.text.strip() for el in text_elements if el.text.strip()])

                # Save unique and valid tweets only
                if tweet_text and not any(t["text"] == tweet_text for t in tweet_data):
                    tweet_data.append({"index": len(tweet_data)+1, "text": tweet_text})
                    print(f"📝 Tweet {len(tweet_data)}: {tweet_text[:60]}...")

            except Exception as e:
                print(f"⚠️ Skipped tweet due to error: {e}")

        # Scroll if not enough tweets collected
        if len(tweet_data) < NUM_TWEETS_TO_SCRAPE:
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(2)
            scroll_attempts += 1

    # Save tweets to JSON
    with open("tweets.json", "w", encoding="utf-8") as f:
        json.dump(tweet_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(tweet_data)} tweets to tweets.json")
    time.sleep(10)

except Exception as e:
    print(f"❌ Error: {e}")

# driver.quit()
