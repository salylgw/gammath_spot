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
    #shortRatio
    #pegRatio
    #heldPercentInstitutions
    #heldPercentInsiders

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
        print('\forwardPE not found for ', tsymbol)
        print('\nError while getting stock info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        fiftyTwoWeekHigh = stock_summary['fiftyTwoWeekHigh']
    except:
        fiftyTwoWeekHigh = 0
        print('\fiftyTwoWeekHigh not found for ', tsymbol)
        print('\nError while getting stock info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        fiftyTwoWeekLow = stock_summary['fiftyTwoWeekLow']
    except:
        fiftyTwoWeekLow = 0
        print('\fiftyTwoWeekLow not found for ', tsymbol)
        print('\nError while getting stock info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        fiftyDayAverage = stock_summary['fiftyDayAverage']
    except:
        fiftyDayAverage = 0
        print('\fiftyDayAverage not found for ', tsymbol)
        print('\nError while getting stock info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        shortRatio = stock_summary['shortRatio']
    except:
        shortRatio = 0
        print('\shortRatio not found for ', tsymbol)
        print('\nError while getting stock info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        pegRatio = stock_summary['pegRatio']
    except:
        pegRatio = 0
        print('\pegRatio not found for ', tsymbol)
        print('\nError while getting stock info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        heldPercentInstitutions = stock_summary['heldPercentInstitutions']
    except:
        heldPercentInstitutions = 0
        print('\heldPercentInstitutions not found for ', tsymbol)
        print('\nError while getting stock info for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        heldPercentInsiders = stock_summary['heldPercentInsiders']
    except:
        heldPercentInsiders = 0
        print('\heldPercentInsiders not found for ', tsymbol)
        print('\nError while getting stock info for ', tsymbol, ': ', sys.exc_info()[0])

    df = pd.DataFrame({'trailingPE': trailingPE, 'forwardPE': forwardPE, 'fiftyTwoWeekHigh': fiftyTwoWeekHigh, 'fiftyTwoWeekLow': fiftyTwoWeekLow, 'fiftyDayAverage': fiftyDayAverage, 'shortRatio': shortRatio, 'pegRatio': pegRatio, 'heldPercentInstitutions': heldPercentInstitutions, 'heldPercentInsiders': heldPercentInsiders}, index=range(1))


    path = Tickers_dir / f'{tsymbol}'
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    #Save the history for reference and processing
    df.to_csv(path / f'{tsymbol}_summary.csv')

    return
