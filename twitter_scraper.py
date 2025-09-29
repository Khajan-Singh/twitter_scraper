from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file in current directory
dotenv_path = ".\\apikey.env"
load_dotenv(dotenv_path)
openai_api_key = os.getenv("OPENAI_API_KEY")

SEARCH_TEXT = "(from:The_Cyber_News OR from:DarkReading OR from:TheHackerNews OR from:CyberSecNews OR from:SecurityWeek OR from:Hackread OR from:briankrebs OR from:SecurityTrybe) since:2025-06-26"
NUM_TWEETS_TO_SCRAPE = 25

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
        print("Cookie banner closed")
    except:
        print("No cookie banner found or already handled")

    # Activate search bar with `/` and enter search query
    body = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    body.send_keys('/')
    time.sleep(1)

    search_input = driver.switch_to.active_element
    search_input.clear()
    search_input.send_keys(SEARCH_TEXT)
    search_input.send_keys(Keys.ENTER)

    print("Searching...")
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
                    print("Expanded tweet")
                except:
                    pass  # No "Show more" button

                # Extract tweet text
                text_elements = tweet.find_elements(By.XPATH, './/div[@data-testid="tweetText"]//span')
                tweet_text = ' '.join([el.text.strip() for el in text_elements if el.text.strip()])

                # Save unique and valid tweets only
                if tweet_text and not any(t["text"] == tweet_text for t in tweet_data):
                    tweet_data.append({"index": len(tweet_data)+1, "text": tweet_text})
                    print(f"Tweet {len(tweet_data)}: {tweet_text[:60]}...")

            except Exception as e:
                print(f"Skipped tweet due to error: {e}")

        # Scroll if not enough tweets collected
        if len(tweet_data) < NUM_TWEETS_TO_SCRAPE:
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(2)
            scroll_attempts += 1

    # Save tweets to JSON
    with open("tweets.json", "w", encoding="utf-8") as f:
        json.dump(tweet_data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(tweet_data)} tweets to tweets.json")
    time.sleep(5)

    # === GPT SUMMARIZATION SECTION ===
    all_tweets = [tweet.get("text", "") for tweet in tweet_data if tweet.get("text")]
    if not all_tweets:
        print("No valid tweet text to summarize.")
        exit()

    combined_text = "\n\n".join(all_tweets)
    if len(combined_text) > 8000:
        combined_text = combined_text[:8000] + "..."

    prompt = f"""
Using these tweets, create your own tweets in a clear and concise way that highlights the key cybersecurity insights or news and are highly engaging, original tweet-style summaries (no hashtags needed). Keep the tweets authoritave but still punchy, fact-focused, and relevant to infosec professionals but also entertaining to read, not monotone. Analyze the following tweets and group those discussing similar cybersecurity topics (like breaches, scams, vulnerabilities, AI threats, etc.).

Then, write a concise and engaging summary tweet for each group. Only group tweets when they clearly relate to the same topic. Each summary should:
- Read like a standalone tweet
- Should highlight a key topic, threat, breakthrough, or discussion point in cybersecurity, preferably in an informative news format with key infromation/statistic/details that readers come back for information and not a question. 
- Don't pose your tweets as simple information but rather specific information that somebody might not have know, even as a professional in the fields they relate to
- Focus on the key insight or update and add information about the topic that you know of if needed to clarify or make it more engaging.
- Skip hashtags or links.
- Don't advertise certain companies or products
- Don't add headings to the tweets

Output each summary on a new line.

Tweets to summarize:
---
{combined_text}
---
Summarized tweets:
"""

    # Use new OpenAI SDK format
    client = OpenAI(api_key=openai_api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "This chatbot is your sharp, cyber-savvy sidekick — blending the urgency of breaking news with the clarity of a well-briefed analyst. It’s relentlessly current, tuned in to the cybersecurity pulse, and unafraid to get technical when needed. Think of it as a trusted digital reporter with a hacker’s edge: it explains complex exploits and emerging threats in a way that’s accessible to pros and novice enthusiasts alike. The tone is approachable, occasionally witty, and always mission-driven — committed to surfacing what matters most from the noise of the cyber world, one tweet-sized summary at a time."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        summaries = response.choices[0].message.content

        with open("summarized_tweets.json", "w", encoding="utf-8") as f:
            json.dump({"summaries": summaries}, f, ensure_ascii=False, indent=2)

        print("✅ Summarized tweets saved to summarized_tweets.json")

    except Exception as e:
        print(f"OpenAI API request failed: {e}")

except Exception as e:
    print(f"Error: {e}")

# driver.quit()
