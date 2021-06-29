# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import yfinance as yf
from pathlib import Path

def get_ticker_options(ticker, path):

    try:
        option_dates = ticker.options
        if (len(option_dates)):
            option_date = option_dates[0]
            options = ticker.option_chain(option_date)
            options.calls.info()
            options.puts.info()
            options.calls.to_csv(path / f'{ticker.ticker}_call_{option_date}.csv')
            options.puts.to_csv(path / f'{ticker.ticker}_put_{option_date}.csv')
    except:
        print('\nOptions not support for ticker: ', ticker.ticker)

    return path
