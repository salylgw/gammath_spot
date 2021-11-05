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
import gammath_utils as gut

def get_ticker_financials(tsymbol, ticker, path):

    print(f'\nGetting financials for {tsymbol}')

    if (len(tsymbol) == 0):
        raise ValueError('Invalid symbol')

    MIN_DELAY_BETWEEN_BATCHES = 1
    MAX_DELAY_BETWEEN_BATCHES = 3

    Tickers_dir = Path('tickers')

    qbs_dont_need_fetch = True
    qcf_dont_need_fetch = True
    qe_dont_need_fetch = True
    qf_dont_need_fetch = True
    reco_dont_need_fetch = True

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    try:
        file_exists = (path / f'{tsymbol}_qbs.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_qbs.csv')
            qbs_dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            qbs_dont_need_fetch = False
    except:
        print(f'\nQuarterly balance sheet for ticker {tsymbol} not found')

    try:
        file_exists = (path / f'{tsymbol}_qcf.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_qcf.csv')
            qcf_dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            qcf_dont_need_fetch = False
    except:
        print(f'\nQuarterly Cash Flow for ticker {tsymbol} not found')

    try:
        file_exists = (path / f'{tsymbol}_qe.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_qe.csv')
            qe_dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            qe_dont_need_fetch = False
    except:
        print(f'\nQuarterly Earnings for ticker {tsymbol} not found')

    try:
        file_exists = (path / f'{tsymbol}_qf.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_qf.csv')
            qf_dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            qf_dont_need_fetch = False
    except:
        print(f'\nQuarterly Financials for ticker {tsymbol} not found')

    try:

        file_exists = (path / f'{tsymbol}_reco.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_reco.csv')
            reco_dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            reco_dont_need_fetch = False
    except:
        print(f'\nRecommendations for ticker {tsymbol} not found')


    if (qbs_dont_need_fetch and qcf_dont_need_fetch and qe_dont_need_fetch and qf_dont_need_fetch and reco_dont_need_fetch):
        return
    else:

        if not qbs_dont_need_fetch:
            print(f'\nFetching quarterly balance sheet for {tsymbol}')
            try:
                stock_balance_sheet = ticker.quarterly_balancesheet
                if (len(stock_balance_sheet) > 0):
                    #Save the data for reference and processing
                    stock_balance_sheet.to_csv(path / f'{tsymbol}_qbs.csv')
                else:
                    print(f'\nBalance sheet for {tsymbol} is empty')
            except:
                print(f'\nQuarterly balance sheet for ticker {tsymbol} not found')

        if not qcf_dont_need_fetch:
            print(f'\nFetching quarterly Cash Flow for {tsymbol}')
            try:
                stock_cash_flow = ticker.quarterly_cashflow
                if (len(stock_cash_flow) > 0):
                    #Save the data for reference and processing
                    stock_cash_flow.to_csv(path / f'{tsymbol}_qcf.csv')
                else:
                    print(f'\nCash flow sheet for {tsymbol} is empty')
            except:
                print(f'\nQuarterly Cash flow sheet for ticker {tsymbol} not found')

        if not qe_dont_need_fetch:
            print(f'\nFetching quarterly Earnings for {tsymbol}')
            try:
                stock_earnings = ticker.quarterly_earnings
                #Save the data for reference and processing
                if (len(stock_earnings) > 0):
                    stock_earnings.to_csv(path / f'{tsymbol}_qe.csv')
                else:
                    print(f'\nEarnings sheet for {tsymbol} is empty')
            except:
                print(f'\nQuarterly Earnings sheet for ticker {tsymbol} not found')

        if not qf_dont_need_fetch:
            print(f'\nFetching quarterly Financials for {tsymbol}')
            try:
                stock_financials = ticker.quarterly_financials
                if (len(stock_financials) > 0):
                    #Save the data for reference and processing
                    stock_financials.to_csv(path / f'{tsymbol}_qf.csv')
                else:
                    print(f'\nFinancials sheet for {tsymbol} is empty')
            except:
                print(f'\nQuarterly Finances sheet for ticker {tsymbol} not found')

        if not reco_dont_need_fetch:
            print(f'\nFetching recommendations for {tsymbol}')
            try:
                stock_recommendations = ticker.recommendations
                if (len(stock_recommendations) > 0):
                    #Save the data for reference and processing
                    stock_recommendations.to_csv(path / f'{tsymbol}_reco.csv')
                else:
                    print(f'\nRecommendations sheet for {tsymbol} is empty')
            except:
                print(f'\nRecommendations sheet for ticker {tsymbol} not found')

    return
