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

Tickers_dir = Path('tickers')

def get_ticker_summary(tsymbol):
    if (len(tsymbol) == 0):
        return None

    ticker = yf.Ticker(tsymbol)
    stock_summary = ticker.info

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
    #state
    #country

    try:
        trailingPE = stock_summary['trailingPE']
    except:
        trailingPE = 0
        print('\ntrailingPE not found for ', tsymbol)
        print('\nError while getting stock info for ', tsymbol, ': ', sys.exc_info()[0])

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

    df = pd.DataFrame({'trailingPE': trailingPE, 'forwardPE': forwardPE, 'fiftyTwoWeekHigh': fiftyTwoWeekHigh, 'fiftyTwoWeekLow': fiftyTwoWeekLow, 'fiftyDayAverage': fiftyDayAverage, 'twoHundredDayAverage': twoHundredDayAverage, 'shortRatio': shortRatio, 'pegRatio': pegRatio, 'beta': beta, 'heldPercentInstitutions': heldPercentInstitutions, 'heldPercentInsiders': heldPercentInsiders, 'state': state, 'country': country}, index=range(1))


    path = Tickers_dir / f'{tsymbol}'
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    #Save the history for reference and processing
    df.to_csv(path / f'{tsymbol}_summary.csv')

    return
