# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import yfinance as yf
from pathlib import Path
import pandas as pd
import sys
import time
import os
import random
import gammath_stocks_summary as gss
import gammath_stocks_financials as gsf
import gammath_stocks_history as gsh
import gammath_stocks_options as gso

Tickers_dir = Path('tickers')

def get_stocks_data(tsymbol):
    if (len(tsymbol) == 0):
        return None

    #Create Yahoo finance ticker handle
    ticker = yf.Ticker(tsymbol)

    path = Tickers_dir / f'{tsymbol}'

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    #Get stock info
    result = gss.get_ticker_summary(tsymbol, ticker, path)

    if (result is None):
        print(f'\nDid not get ticker summary for {tsymbol}')

    #Get stock financials
    result = gsf.get_ticker_financials(tsymbol, ticker, path)
    if (result is None):
        print(f'\nDid not get ticker financials for {tsymbol}')

    #Get stock options data
    result = gso.get_options_data(tsymbol, ticker, path)
    if (result is None):
        print(f'\nDid not get ticker options info for {tsymbol}')

    #Get stock history
    result = gsh.get_ticker_history(tsymbol, ticker, path)
    if (result is None):
        print(f'\nDid not get ticker history for {tsymbol}')

    return
