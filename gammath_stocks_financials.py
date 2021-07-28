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
        file_exists = (path / f'{tsymbol}_qbs.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_qbs.csv')
            fct_time = time.ctime(fstat.st_ctime).split(' ')
            dt = time.strftime('%x').split('/')
            if (fct_time[2] == dt[1]):
                print('No need to get new file')
                dont_need_fetch = True
            else:
                print('Date mismatch. Need to fetch new file')
                dont_need_fetch = False
        else:
            dont_need_fetch = False


        if not dont_need_fetch:
            stock_balance_sheet = ticker.quarterly_balancesheet
            if (len(stock_balance_sheet) > 0):
                #Save the data for reference and processing
                stock_balance_sheet.to_csv(path / f'{tsymbol}_qbs.csv')
            else:
                print(f'\nBalance sheet for {tsymbol} is empty')
    except:
        print(f'\nQuarterly balance sheet for ticker {tsymbol} not found')

    print(f'\nFetching quarterly Cash Flow for {tsymbol}')
    try:
        file_exists = (path / f'{tsymbol}_qcf.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_qcf.csv')
            fct_time = time.ctime(fstat.st_ctime).split(' ')
            dt = time.strftime('%x').split('/')
            if (fct_time[2] == dt[1]):
                print('No need to get new file')
                dont_need_fetch = True
            else:
                print('Date mismatch. Need to fetch new file')
                dont_need_fetch = False
        else:
            dont_need_fetch = False


        if not dont_need_fetch:
            stock_cash_flow = ticker.quarterly_cashflow
            if (len(stock_cash_flow) > 0):
                #Save the data for reference and processing
                stock_cash_flow.to_csv(path / f'{tsymbol}_qcf.csv')
            else:
                print(f'\nCash flow sheet for {tsymbol} is empty')
    except:
        print(f'\nQuarterly Cash Flow for ticker {tsymbol} not found')

    print(f'\nFetching quarterly Earnings for {tsymbol}')
    try:
        file_exists = (path / f'{tsymbol}_qe.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_qe.csv')
            fct_time = time.ctime(fstat.st_ctime).split(' ')
            dt = time.strftime('%x').split('/')
            if (fct_time[2] == dt[1]):
                print('No need to get new file')
                dont_need_fetch = True
            else:
                print('Date mismatch. Need to fetch new file')
                dont_need_fetch = False
        else:
            dont_need_fetch = False


        if not dont_need_fetch:
            stock_earnings = ticker.quarterly_earnings
            #Save the data for reference and processing
            if (len(stock_earnings) > 0):
                stock_earnings.to_csv(path / f'{tsymbol}_qe.csv')
            else:
                print(f'\nEarnings sheet for {tsymbol} is empty')
    except:
        print(f'\nQuarterly Earnings for ticker {tsymbol} not found')

    print(f'\nFetching quarterly Financials for {tsymbol}')
    try:
        file_exists = (path / f'{tsymbol}_qf.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_qf.csv')
            fct_time = time.ctime(fstat.st_ctime).split(' ')
            dt = time.strftime('%x').split('/')
            if (fct_time[2] == dt[1]):
                print('No need to get new file')
                dont_need_fetch = True
            else:
                print('Date mismatch. Need to fetch new file')
                dont_need_fetch = False
        else:
            dont_need_fetch = False


        if not dont_need_fetch:
            stock_financials = ticker.quarterly_financials
            if (len(stock_financials) > 0):
                #Save the data for reference and processing
                stock_financials.to_csv(path / f'{tsymbol}_qf.csv')
            else:
                print(f'\nFinancials sheet for {tsymbol} is empty')
    except:
        print(f'\nQuarterly Financials for ticker {tsymbol} not found')

    print(f'\nFetching recommendations for {tsymbol}')
    try:

        file_exists = (path / f'{tsymbol}_reco.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_reco.csv')
            fct_time = time.ctime(fstat.st_ctime).split(' ')
            dt = time.strftime('%x').split('/')
            if (fct_time[2] == dt[1]):
                print('No need to get new file')
                dont_need_fetch = True
            else:
                print('Date mismatch. Need to fetch new file')
                dont_need_fetch = False
        else:
            dont_need_fetch = False


        if not dont_need_fetch:
            stock_recommendations = ticker.recommendations
            if (len(stock_recommendations) > 0):
                #Save the data for reference and processing
                stock_recommendations.to_csv(path / f'{tsymbol}_reco.csv')
            else:
                print(f'\nRecommendations sheet for {tsymbol} is empty')
    except:
        print(f'\nRecommendations for ticker {tsymbol} not found')

    #Play nice
    time.sleep(random.randrange(MIN_DELAY_BETWEEN_BATCHES, MAX_DELAY_BETWEEN_BATCHES))
    return
