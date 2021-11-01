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
import gammath_get_stcktwts as ggstw
import gammath_stocks_calendar as gsc

Tickers_dir = Path('tickers')

#Get data for stock ticker symbol from the internet
def get_stocks_data(tsymbol):
    if (len(tsymbol) == 0):
        return None

    path = Tickers_dir / f'{tsymbol}'

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    #Fetch stocktwits page; Finish getting all data outside of yahoo
    ggstw.get_stocktwits_ticker_info(tsymbol, path)

    try:
        #Create Yahoo finance ticker handle
        ticker = yf.Ticker(tsymbol)
    except:
        raise RuntimeError('Failed to create Yahoo ticker handle')

    try:
        #Get stock info
        gss.get_ticker_summary(tsymbol, ticker, path)

    except ValueError:
        print(f'Error while getting stock summary for {tsymbol}')

    try:
        #Get stock financials
        gsf.get_ticker_financials(tsymbol, ticker, path)
    except ValueError:
        print(f'Error while getting stock financial data for {tsymbol}')

    try:
        #Get stock options data
        gso.get_options_data(tsymbol, ticker, path)
    except ValueError:
        print(f'Error while getting stock options data for {tsymbol}')
    except RuntimeError:
        print(f'Could not get stock options data for {tsymbol}')

    #Getting calendar info is too slow.
#    try:
#        #Fetch calendar
#        gsc.get_ticker_calendar(tsymbol, ticker, path)
#    except ValueError:
#        print(f'Error while getting stock calendar data for {tsymbol}')
#    except RuntimeError:
#        print(f'Could not get stock calendar data for {tsymbol}')

    try:
        #Get stock history
        result = gsh.get_ticker_history(tsymbol, ticker, path)
    except ValueError:
        print(f'\nError while getting ticker price history for {tsymbol}')
    except RuntimeError:
        print(f'\nCould not get stock price history data for {tsymbol}')

    return
