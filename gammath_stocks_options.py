# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import yfinance as yf
from pathlib import Path
import bisect
from datetime import datetime
import pandas as pd
import time
import os

def get_options_data(tsymbol, ticker, path):

    #Get current date and time
    current_dt = datetime.now()

    try:
        if ((path / f'{tsymbol}_options_dates.csv').exists()):
            print(f'\nGet options dates for {tsymbol}')
            #Get the latest options expiry date
            dates_df = pd.read_csv(path / f'{tsymbol}_options_dates.csv', index_col='Unnamed: 0')

            option_date = dates_df.loc[0][0]
        else:
            option_dates = ticker.options
            if (len(option_dates)):
                opt_dates_ds = pd.Series(option_dates)
                opt_dates_ds.to_csv(path / f'{tsymbol}_options_dates.csv')

                option_date = option_dates[0]
            else:
                return None

        #Check if file exists and is it from another day
        file_exists = (path / f'{tsymbol}_call_{option_date}.csv').exists()

        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_call_{option_date}.csv')
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

        #We only need to read options data once a day
        if (not dont_need_fetch):
            print('\nGetting option chain for ', tsymbol)

            print('\nNext options expiry ', tsymbol, 'is ', option_date, 'type is ', type(option_date))

            options = ticker.option_chain(option_date)
            options.calls.info()
            options.puts.info()
            print('\nGot option chain for ', tsymbol)

            print('\nSorting calls based on strike price')
            df_calls = options.calls.sort_values('strike')

            #Save the calls sorted by strike price
            df_calls.to_csv(path / f'{tsymbol}_call_{option_date}.csv')

            print('\nSorting puts based on strike price')
            df_puts = options.puts.sort_values('strike')

            #Save the puts sorted by strike price
            df_puts.to_csv(path / f'{tsymbol}_put_{option_date}.csv')

            print('\nSaved call and put data')
        else:
            print(f'\nOptions data already exists for {tsymbol}')

    except:
        print(f'\nError getting options data for {tsymbol}')
        return None

    return

