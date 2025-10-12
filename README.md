### X/Twitter Tweet Summarizer with Selenium

## Program description:
opens X/twitter search, searches topics you want a summary of, scrapes the tweets, and create personalized tweets by summarizing the ones it scraped. summarizing powered by ChatGPT API. 

## Instructions:
install your ChromeWebDriver: https://developer.chrome.com/docs/chromedriver/downloads

install selenium:
```
pip install selenium
```

## Before running:
create a profile for selenium testing and log into X/twitter (so you don't have to repeadtly do it and potentially get flagged as a bot). make sure the chrome profile path in the code (twitter_scraper.py) matches the one you are using.