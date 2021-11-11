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
import gammath_utils as gut

def get_options_data(tsymbol, ticker, path):

    #Get stock info summary from the internet

    if (len(tsymbol) == 0):
        raise ValueError('Invalid symbol')

    try:

        #Check if file exists and is it from another day
        file_exists = (path / f'{tsymbol}_options_dates.csv').exists()

        if (file_exists):
            #Check if it is latest
            fstat = os.stat(path / f'{tsymbol}_options_dates.csv')
            dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            dont_need_fetch = False

        if (dont_need_fetch):
            #Get the latest options expiry date
            dates_df = pd.read_csv(path / f'{tsymbol}_options_dates.csv', index_col='Unnamed: 0')

            option_date = dates_df.loc[0][0]
        else:
            #Read fresh data
            option_dates = ticker.options
            if (len(option_dates)):
                opt_dates_ds = pd.Series(option_dates)
                opt_dates_ds.to_csv(path / f'{tsymbol}_options_dates.csv')

                option_date = option_dates[0]
            else:
                raise RuntimeError('No option expiry dates')

        #Check if file exists and is it from another day
        file_exists = (path / f'{tsymbol}_call_{option_date}.csv').exists()

        if file_exists:
            #Check if it is latest
            fstat = os.stat(path / f'{tsymbol}_call_{option_date}.csv')
            dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            dont_need_fetch = False

        #We only need to read options data once a day
        if (not dont_need_fetch):
            options = ticker.option_chain(option_date)
            options.calls.info()
            options.puts.info()
            df_calls = options.calls.sort_values('strike')

            #Save the calls sorted by strike price
            df_calls.to_csv(path / f'{tsymbol}_call_{option_date}.csv')

            df_puts = options.puts.sort_values('strike')

            #Save the puts sorted by strike price
            df_puts.to_csv(path / f'{tsymbol}_put_{option_date}.csv')
    except:
        raise RuntimeError('No option data')

    return

