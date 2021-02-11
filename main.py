import praw
import re
import pandas as pd
import json
from datetime import date, datetime
import os
import requests

def exchange_data_up_to_date(verbose=False):
    """Checks if exchange data is up to date

    Returns
    -------
    Bool
        True if exchange data has been scraped within the last week
        False if not (or if folder does not exist)
    """
    if os.path.exists("exchange_data"):
    # make sure stock list is reasonably up-to-date:
        today = datetime.now()
        last_updated = open("exchange_data/last_updated.txt", 'r')
        last_updated = last_updated.read()
        last_updated = datetime.strptime('2021-02-07', "%Y-%m-%d")
        if abs((today - last_updated).days) > 7:
            if verbose: print("Listed stocks > one week old.")
            return False
    else:
        if verbose: print("Exchange data folder doesn't exist.")
        return False
    # Folder exists and stocks have been scraped in the last week.
    if verbose: print("Folder and exchange data up-to-date")
    return True


def update_exchange_data(verbose=False):
    """Updates exchange data files from dumbstockapi.com, which is an easy API that returns current market
    tickers (although not sure how up to date it is).

    Exchanges included so far: NASDAQ, NYSE, AMEX, & TSX
    """
    # create folder if doesnt exist already:
    if not os.path.exists("exchange_data"):
        if verbose: print("Creating exchange data (list of tickers) folder...")
        os.mkdir("exchange_data")

    # scrape data from NA exchanges:
    exchanges = ['NASDAQ', 'NYSE', 'AMEX', 'TSX']
    today = date.today()
    for e in exchanges:
        if verbose: print(f"Updating tickers for: {e}.")
        url = f"https://dumbstockapi.com/stock?exchanges={e}"
        response = requests.request("GET", url)
        data = pd.DataFrame(json.loads(response.text))
        data.to_csv(f"exchange_data/{e}_{today}.csv")

    # record last-updated date:
    text_file = open("exchange_data/last_updated.txt", "w")
    text_file.write(f"{today}")
    text_file.close()
    if verbose: print("Exchange tickers updated.")


def get_all_listed_stocks():
    """Reads all the CSV files in the 'exchange_data' folder and returns a list of stock tickers
    in alphabetical order.

    Return
    ------
    list
        Stock tickers in NYSE, AMEX, NASDAQ, and TSX
    """
    ticker_list = []
    filelist = [f for f in os.listdir('exchange_data') if f.endswith('.csv')]
    for file in filelist:
        tickers = pd.read_csv('exchange_data/' + file, skip_blank_lines=True, usecols=['ticker'])
        [ticker_list.append(str(v).rstrip()) for v in tickers['ticker'].values]
    ticker_list.sort()
    return ticker_list


def get_subreddit_ticker_timeseries(sub, stockList, verbose=False, reddit_timeframe="all"):
    """Get a list of tuples of each time a ticker is mentioned in a given subreddit

    Parameters
    ----------
    sub : string
        subreddit name e.g., "wallstreetbets"

    stockList: list
        list of stock tickers used to filter words that pass the regex pattern

    Returns
    -------
    list
        a list of tuples (ticker, time [in utc]) recording the ticker and time mentioned in the subreddit

    """
    reddit = praw.Reddit(
        "bot1"
    )

    regexPattern = r'\b([A-Za-z][\S]+)\b'
    blacklist = ["A", "I", "DD", "WSB", "YOLO", "RH", "EV", "PE", "ETH", "BTC", "E"]
    tickerSeries = []

    for submission in reddit.subreddit(sub).top(reddit_timeframe):
        submission.comments.replace_more(limit=0)
        if verbose: print(submission.title)
        for comment in submission.comments.list():
            for phrase in re.findall(regexPattern, comment.body):
                if phrase not in blacklist:
                    if phrase in stockList:
                        tickerSeries.append((phrase, comment.created_utc))
    return tickerSeries


def scrape_stock_subreddits(subs=["wallstreetbets", "stocks", "investing", "smallstreetbets"], verbose=False, reddit_timeframe="all"):
    """Scrape a list of subreddits for all stock tickers mentioned.

    Parameters
    ----------
    subs : list
        list of subreddits e.g., "wallstreetbets"
    verbose : Bool , optional
        Prints messages like reddit discussion titles
    
    Returns
    -------
    dict
        keys : subreddits (sub parameter)
        values : list of tuples (ticker, time mentioned in utc)
    """
    listedStocks = get_all_listed_stocks()
    tickerSeries = {}
    for sub in subs:
        if verbose: print(f"Scraping subreddit: {sub}...")
        subTickers = get_subreddit_ticker_timeseries(sub, listedStocks, verbose=verbose, reddit_timeframe=reddit_timeframe)
        tickerSeries[sub] = subTickers
    return tickerSeries
    

if __name__ == '__main__':
    """ Main function ensures all tickers are up-to-date then scrapes a few subreddits for
    ticker mentions timeseries.

    - Creates exchange_data/ folder if doesn't exist yet
    - Creates output folder and saves json data
        - keys are subreddit name, values are a list of tuples (ticker, time mentioned in utc)
    """
    verbose=True
    reddit_timeframe="day" # Can be one of: all, day, hour, month, week, year (default: all)
    subs=["wallstreetbets", "stocks", "investing", "smallstreetbets"]

    assert reddit_timeframe in ["all", "day", "hour", "month", "week", "year"]

    # check if stock data is up-to-date:
    if not exchange_data_up_to_date(verbose=verbose):
        update_exchange_data(verbose=verbose)

    # scrape stocks:
    tickerSeries = scrape_stock_subreddits(subs, verbose=verbose, reddit_timeframe=reddit_timeframe)
    if not os.path.exists("output"):
        os.mkdir("output")
    with open(f'output/ticker_series_{date.today()}.json', 'w') as f:
        if verbose: print(f"Saving timeseries to output/ticker_series_{date.today()}.json")
        json.dump(tickerSeries, f)
