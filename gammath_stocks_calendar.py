# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import yfinance as yf
from pathlib import Path
import pandas as pd
import time
import os

Tickers_dir = Path('tickers')

def get_ticker_calendar(tsymbol, ticker, path):
    if (len(tsymbol) == 0):
        return None

    calendar_dont_need_fetch = True

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    try:
        file_exists = (path / f'{tsymbol}_calendar.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_calendar.csv')
            fct_time = time.ctime(fstat.st_ctime).split(' ')
            dt = time.strftime('%x').split('/')
            if (fct_time[2] == ''):
                fct_date_index = 3
            else:
                fct_date_index = 2

            fct_date = int(fct_time[fct_date_index])
            dt_date = int(dt[1])

            if (fct_date == dt_date):
                print('No need to get new file')
                calendar_dont_need_fetch = True
            else:
                print('Date mismatch. Need to fetch new file')
                calendar_dont_need_fetch = False
        else:
            calendar_dont_need_fetch = False
    except:
        print(f'\nError reading Calendar file for ticker {tsymbol} not found')
        return None

    if not calendar_dont_need_fetch:
        print(f'\nFetching calendar for {tsymbol}')
        try:
            stock_calendar_sheet = ticker.calendar
            if (len(stock_calendar_sheet) > 0):
                #Save the data for reference and processing
                stock_calendar_sheet.to_csv(path / f'{tsymbol}_calendar.csv')
            else:
                print(f'\nCalendar for {tsymbol} is empty')
        except:
            print(f'\nError getting Calendar for ticker {tsymbol} not found')
            return None


    return
