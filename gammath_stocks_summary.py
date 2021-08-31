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

def get_ticker_summary(tsymbol):
    if (len(tsymbol) == 0):
        return None

    new_heldPercentInstitutions = 0
    heldPercentInstitutionsChange = 0
    new_heldPercentInstitutionsChange = 0
    heldPercentInsidersChange = 0
    new_heldPercentInsiders = 0
    new_heldPercentInsidersChange = 0
    heldPercentInstitutionsChangeDir = ''
    heldPercentInsidersChangeDir = ''
    heldPercentInstitutions = 0
    heldPercentInsiders = 0

    path = Tickers_dir / f'{tsymbol}'

    file_exists = (path / f'{tsymbol}_summary.csv').exists()

    #Check if file exists and is it from another day
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

            #Get the values for institution and insider holding pct and pct_change from previous file
            stock_summary = pd.read_csv(path / f'{tsymbol}_summary.csv')

            #Get current pct change
            heldPercentInstitutionsChange = round(stock_summary['heldPercentInstitutionsChange'][0], 5)
            heldPercentInsidersChange = round(stock_summary['heldPercentInsidersChange'][0], 5)

            #Get current values
            heldPercentInstitutions = round(stock_summary['heldPercentInstitutions'][0], 5)
            heldPercentInsiders = round(stock_summary['heldPercentInsiders'][0], 5)
    else:
        dont_need_fetch = False

    #Check if we need to get new summary info
    if (dont_need_fetch):
        print(f'\nFile for {tsymbol} exists.')
        return
    else:
        print(f'\nFile for {tsymbol} does not exist. Fetching it now')
        try:
            ticker = yf.Ticker(tsymbol)
            stock_summary = ticker.info
        except:
            print(f'\nStock summary for ticker {tsymbol} not found')
            return

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
        new_heldPercentInstitutions = round(stock_summary['heldPercentInstitutions'], 5)
        #Compute pct change for institutional holdings
        new_heldPercentInstitutionsChange = round((new_heldPercentInstitutions - heldPercentInstitutions), 5)

        print(f'\nInst holdings pct change for {tsymbol}: {new_heldPercentInstitutionsChange}. Was: {heldPercentInstitutionsChange}')

        new_heldPercentInstitutionsChange += heldPercentInstitutionsChange
        new_heldPercentInstitutionsChange = round(new_heldPercentInstitutionsChange, 5)
        if (new_heldPercentInstitutionsChange > heldPercentInstitutionsChange):
            heldPercentInstitutionsChangeDir = 'up'
        elif (new_heldPercentInstitutionsChange < heldPercentInstitutionsChange):
            heldPercentInstitutionsChangeDir = 'down'
        else:
            heldPercentInstitutionsChangeDir = 'flat'
    except:
        new_heldPercentInstitutions = 0
        stock_summary['heldPercentInstitutions'] = 0
        print('\nheldPercentInstitutions not found for ', tsymbol)
        print('\nError while getting heldPercentInstitutions info for ', tsymbol, ': ', sys.exc_info()[0])
    try:
        new_heldPercentInsiders = round(stock_summary['heldPercentInsiders'], 5)
        #Compute pct change for insiders holdings
        new_heldPercentInsidersChange = round((new_heldPercentInsiders - heldPercentInsiders), 5)
        val_type = type(new_heldPercentInsidersChange)
        print(f'\nInsiders holdings pct change for {tsymbol}: {new_heldPercentInsidersChange}. Was: {heldPercentInsidersChange}. Type:{val_type}')

        new_heldPercentInsidersChange += heldPercentInsidersChange
        new_heldPercentInsidersChange = round(new_heldPercentInsidersChange, 5)
        if (new_heldPercentInsidersChange > heldPercentInsidersChange):
            heldPercentInsidersChangeDir = 'up'
        elif (new_heldPercentInsidersChange < heldPercentInsidersChange):
            heldPercentInsidersChangeDir = 'down'
        else:
            heldPercentInsidersChangeDir = 'flat'
    except:
        new_heldPercentInsiders = 0
        stock_summary['heldPercentInsiders'] = 0
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

    df = pd.DataFrame({'trailingPE': trailingPE, 'forwardPE': forwardPE, 'fiftyTwoWeekHigh': fiftyTwoWeekHigh, 'fiftyTwoWeekLow': fiftyTwoWeekLow, 'fiftyDayAverage': fiftyDayAverage, 'twoHundredDayAverage': twoHundredDayAverage, 'shortRatio': shortRatio, 'pegRatio': pegRatio, 'beta': beta, 'heldPercentInstitutions': new_heldPercentInstitutions, 'heldPercentInstitutionsChange': new_heldPercentInstitutionsChange, 'heldPercentInstitutionsChangeDir': heldPercentInstitutionsChangeDir , 'heldPercentInsiders': new_heldPercentInsiders, 'heldPercentInsidersChange': new_heldPercentInsidersChange, 'heldPercentInsidersChangeDir': heldPercentInsidersChangeDir, 'priceToBook': pbr, 'state': state, 'country': country, 'currentPrice': curr_price}, index=range(1))

    path = Tickers_dir / f'{tsymbol}'
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    #Save the history for reference and processing
    df.to_csv(path / f'{tsymbol}_summary.csv')

    #Play nice
#    time.sleep(random.randrange(MIN_DELAY_BETWEEN_BATCHES, MAX_DELAY_BETWEEN_BATCHES))
    return
