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


def get_ticker_summary(tsymbol, ticker, path):

    #Get stock info summary from the internet
    print(f'\nGetting {tsymbol} ticker summary.')

    if (len(tsymbol) == 0):
        raise ValueError('Invalid symbol')

    Tickers_dir = Path('tickers')

    #Check if file exists and is it from another day
    file_exists = (path / f'{tsymbol}_summary.csv').exists()

    if file_exists:
        fstat = os.stat(path / f'{tsymbol}_summary.csv')
        fct_time = time.ctime(fstat.st_ctime).split(' ')
        if (fct_time[2] == ''):
            fct_date_index = 3
        else:
            fct_date_index = 2

        fct_date = int(fct_time[fct_date_index])
        dt = time.strftime('%x').split('/')
        dt_date = int(dt[1])

        if (fct_date == dt_date):
            print('No need to get new file')
            dont_need_fetch = True
        else:
            print('Date mismatch. Need to fetch new file')
            dont_need_fetch = False
    else:
        dont_need_fetch = False

    #Check if we need to get new summary info
    if (dont_need_fetch):
        print(f'\nFile for {tsymbol} exists.')
        return
    else:
        print(f'\nFile for {tsymbol} does not exist. Fetching it now')
        try:
            stock_summary = ticker.info
        except:
            print(f'\nStock summary for ticker {tsymbol} not found')
            raise ValueError('Stock summary not found')

    #Extract the items of interest
    #trailingPE
    #forwardPE
    #fiftyTwoWeekHigh
    #fiftyTwoWeekLow
    #fiftyDayAverage
    #twoHundredDayAverage
    #shortRatio
    #pegRatio
    #beta
    #heldPercentInstitutions
    #heldPercentInsiders
    #priceToBook
    #state
    #country
    #regularMarketPrice
    #marketCap

    try:
        trailingPE = stock_summary['trailingPE']
    except:
        trailingPE = 0
        print('\ntrailingPE not found for ', tsymbol)
        print('\nError while getting trailingPE info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        forwardPE = stock_summary['forwardPE']
    except:
        forwardPE = 0
        print('\nforwardPE not found for ', tsymbol)
        print('\nError while getting forwardPE info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        fiftyTwoWeekHigh = stock_summary['fiftyTwoWeekHigh']
    except:
        fiftyTwoWeekHigh = 0
        print('\nfiftyTwoWeekHigh not found for ', tsymbol)
        print('\nError while getting fiftyTwoWeekHigh info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        fiftyTwoWeekLow = stock_summary['fiftyTwoWeekLow']
    except:
        fiftyTwoWeekLow = 0
        print('\nfiftyTwoWeekLow not found for ', tsymbol)
        print('\nError while getting fiftyTwoWeekLow info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        fiftyDayAverage = stock_summary['fiftyDayAverage']
    except:
        fiftyDayAverage = 0
        print('\nfiftyDayAverage not found for ', tsymbol)
        print('\nError while getting fiftyDayAverage info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        twoHundredDayAverage = stock_summary['twoHundredDayAverage']
    except:
        twoHundredDayAverage = 0
        print('\ntwoHundredDayAverage not found for ', tsymbol)
        print('\nError while getting twoHundredDayAverage info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        shortRatio = stock_summary['shortRatio']
    except:
        shortRatio = 0
        print('\nshortRatio not found for ', tsymbol)
        print('\nError while getting shortRatio info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        pegRatio = stock_summary['pegRatio']
    except:
        pegRatio = 0
        print('\npegRatio not found for ', tsymbol)
        print('\nError while getting pegRatio info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        beta = stock_summary['beta']
    except:
        beta = 0
        print('\beta not found for ', tsymbol)
        print('\nError while getting pegRatio info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        heldPercentInstitutions = stock_summary['heldPercentInstitutions']
    except:
        heldPercentInstitutions = 0
        print('\nheldPercentInstitutions not found for ', tsymbol)
        print('\nError while getting heldPercentInstitutions info for ', tsymbol, ': ', sys.exc_info()[0])
    try:
        heldPercentInsiders = stock_summary['heldPercentInsiders']
    except:
        heldPercentInsiders = 0
        print('\nheldPercentInsiders not found for ', tsymbol)
        print('\nError while getting heldPercentInsiders info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        pbr = stock_summary['priceToBook']
    except:
        pbr = 0
        print('\nPrice to Book ratio not found for ', tsymbol)
        print('\nError while getting PBR info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        state = stock_summary['state']
    except:
        state = ''
        print('\ncountry not found for ', tsymbol)
        print('\nError while getting state info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        country = stock_summary['country']
    except:
        country = ''
        print('\ncountry not found for ', tsymbol)
        print('\nError while getting country info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        curr_price = stock_summary['regularMarketPrice']
    except:
        curr_price = 0
        print('\nCurrent price not found for ', tsymbol)
        print('\nError while getting current price info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        mktcap = stock_summary['marketCap']
        print(f'\nMarket cap for {tsymbol} is {mktcap}')
    except:
        mktcap = 0
        print('\nMarket Cap not found for ', tsymbol)
        print('\nError while getting current price info for ', tsymbol, ': ', sys.exc_info()[0])

    df = pd.DataFrame({'trailingPE': trailingPE, 'forwardPE': forwardPE, 'fiftyTwoWeekHigh': fiftyTwoWeekHigh, 'fiftyTwoWeekLow': fiftyTwoWeekLow, 'fiftyDayAverage': fiftyDayAverage, 'twoHundredDayAverage': twoHundredDayAverage, 'shortRatio': shortRatio, 'pegRatio': pegRatio, 'beta': beta, 'heldPercentInstitutions': heldPercentInstitutions, 'heldPercentInsiders': heldPercentInsiders, 'priceToBook': pbr, 'state': state, 'country': country, 'currentPrice': curr_price, 'marketCap': mktcap}, index=range(1))

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    #Save the history for reference and processing
    df.to_csv(path / f'{tsymbol}_summary.csv')

    return
