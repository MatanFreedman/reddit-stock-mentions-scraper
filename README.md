# Reddit Stock Ticker Mentions Scraper
Scrapes popular stock-focused subreddits for mentions of any tickers in certain exchanges (default is NASDAQ, AMEX, NYSE, and TSX). Output can be used to show timeseries of number of mentions in each subreddit.

Running the main.py script will:

(1) Create an "exchange_data" folder that pulls all listed tickers from the NASDAQ, AMEX, NYSE, and TSX and stores them in .csv files. The script uses an API from https://dumbstockapi.com . I'm not sure how up to date it is but I doubt it will make a huge difference. 

(2) Check if the exchange data folder is reasonably up-to-date (within the last week). If not it will pull tickers from the mentioned API.

(3) Scrape whatever subreddits are specified at the top of the main function ("subs"). Default is WSB and some other
ones. 

(4) Final output: create output folder and save a "output/ticker_series_{TODAYS DATE}.json" where the keys are the subreddit and the elements are a list of tuples (ticker, time mentioned in utc)


Requirements:
There needs to be a "praw.ini" file in the main directory with your Reddit API credentials. It looks something like this:

```
[bot1]
client_id=YOUR_CLIENT_ID 
client_secret=YOUR_SECRET_KEY 
user_agent="Some unique user agent" 
```

More info here: https://praw.readthedocs.io/en/latest/getting_started/quick_start.html 
