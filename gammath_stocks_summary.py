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
#        df = pd.DataFrame({'trailingPE': stock_summary['trailingPE'], 'forwardPE': stock_summary['forwardPE'], 'fiftyTwoWeekHigh': stock_summary['fiftyTwoWeekHigh'], 'fiftyTwoWeekLow': stock_summary['fiftyTwoWeekLow'], 'fiftyDayAverage': stock_summary['fiftyDayAverage'], 'shortRatio': stock_summary['shortRatio'], 'pegRatio': stock_summary['pegRatio'], 'heldPercentInstitutions': stock_summary['heldPercentInstitutions'], 'heldPercentInsiders': stock_summary['heldPercentInsiders']}, index=range(1))
#        df = pd.DataFrame({'fiftyTwoWeekHigh': stock_summary['fiftyTwoWeekHigh'], 'fiftyTwoWeekLow': stock_summary['fiftyTwoWeekLow'], 'fiftyDayAverage': stock_summary['fiftyDayAverage'], 'shortRatio': stock_summary['shortRatio']}, index=range(1))

        df = pd.DataFrame({'fiftyTwoWeekHigh': stock_summary['fiftyTwoWeekHigh'], 'fiftyTwoWeekLow': stock_summary['fiftyTwoWeekLow'], 'fiftyDayAverage': stock_summary['fiftyDayAverage']}, index=range(1))
    except:
        #REVISIT missing items
        df = pd.DataFrame(list(stock_summary.items()))
        print('\nError while getting stock info for ', tsymbol, ': ', sys.exc_info()[0])

    path = Tickers_dir / f'{tsymbol}'
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    #Save the history for reference and processing
    df.to_csv(path / f'{tsymbol}_summary.csv')

    return
