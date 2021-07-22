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

MIN_DELAY_BETWEEN_BATCHES = 1
MAX_DELAY_BETWEEN_BATCHES = 3

Tickers_dir = Path('tickers')

def get_ticker_financials(tsymbol):
    if (len(tsymbol) == 0):
        return None

    ticker = yf.Ticker(tsymbol)

    path = Tickers_dir / f'{tsymbol}'
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    print(f'\nFetching quarterly balance sheet for {tsymbol}')
    try:
        stock_balance_sheet = ticker.quarterly_balancesheet
        #Save the data for reference and processing
        stock_balance_sheet.to_csv(path / f'{tsymbol}_qbs.csv')
    except:
        print(f'\nQuarterly balance sheet for ticker {tsymbol} not found')

    print(f'\nFetching quarterly Cash Flow for {tsymbol}')
    try:
        stock_cash_flow = ticker.quarterly_cashflow
        #Save the data for reference and processing
        stock_cash_flow.to_csv(path / f'{tsymbol}_qcf.csv')
    except:
        print(f'\nQuarterly Cash Flow for ticker {tsymbol} not found')

    print(f'\nFetching quarterly Earnings for {tsymbol}')
    try:
        stock_earnings = ticker.quarterly_earnings
        #Save the data for reference and processing
        stock_earnings.to_csv(path / f'{tsymbol}_qe.csv')
    except:
        print(f'\nQuarterly Earnings for ticker {tsymbol} not found')

    print(f'\nFetching quarterly Financials for {tsymbol}')
    try:
        stock_financials = ticker.quarterly_financials
        #Save the data for reference and processing
        stock_financials.to_csv(path / f'{tsymbol}_qf.csv')
    except:
        print(f'\nQuarterly Financials for ticker {tsymbol} not found')

    print(f'\nFetching recommendations for {tsymbol}')
    try:
        stock_recommendations = ticker.recommendations
        #Save the data for reference and processing
        stock_recommendations.to_csv(path / f'{tsymbol}_reco.csv')
    except:
        print(f'\nRecommendations for ticker {tsymbol} not found')

    #Play nice
    time.sleep(random.randrange(MIN_DELAY_BETWEEN_BATCHES, MAX_DELAY_BETWEEN_BATCHES))
    return
