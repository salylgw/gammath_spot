# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import yfinance as yf
from datetime import datetime
from pathlib import Path
import gammath_options_chain as goc


#Get summary of past 5 years history
end_date = datetime.today()
start_date = datetime(end_date.year-5, end_date.month, end_date.day)

Tickers_dir = Path('tickers')

def get_ticker_info(tsymbol, all):
    if (len(tsymbol) == 0):
        return None

    ticker = yf.Ticker(tsymbol)
    stock_history = ticker.history(interval='1d', start=start_date, end=end_date, actions=True,auto_adjust=True)

    print('Stock history dataframe info for ', tsymbol, ':\n')
    stock_history.info()

    path = Tickers_dir / f'{tsymbol}'
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    #Save the history for reference and processing
    stock_history.dropna().to_csv(path / f'{tsymbol}_history.csv')

    #Experimental: WIP
    if (all == True):
        goc.get_ticker_options(ticker, path)

    return path
