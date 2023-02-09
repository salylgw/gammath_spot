# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works'

import pandas as pd
import yfinance as yf
from pathlib import Path

try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut


def get_ticker_history(tsymbol, ticker, path):

    if (len(tsymbol) == 0):
        raise ValueError('Invalid symbol')

    mtdpy, mtd5y = gut.get_min_trading_days()

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        history_file_exists = False
    else:
        #Check if we have stock history for this stock
        history_file_exists = (path / f'{tsymbol}_history.csv').exists()

        if (history_file_exists):
            #Read in the previous history file to check last history date
            df_old = pd.read_csv(path / f'{tsymbol}_history.csv', index_col='Date')
            df_old_len = len(df_old)
            if (df_old_len >= mtd5y):
                history_file_exists = True
            else:
                history_file_exists = False

    if (history_file_exists):

        #Get the date from where to obtain new data
        start_date = df_old.index[df_old_len-1].split(' ')[0]

        #Index for truncating
        last_date = df_old.index[df_old_len-2]

        #Always save the previous price history for reference
        df_old.to_csv(path / f'{tsymbol}_history_prev.csv')

        #Obtain the new data
        try:
            stock_history_part = ticker.history(start=start_date, interval='1d', actions=True, auto_adjust=True)

            #Get the number of new entries
            part_len = len(stock_history_part)

            #Truncate the unwanted items; No need to remove older dates
            df_old = df_old.truncate(after=last_date)

            #Save old and new data into single history
            stock_history = pd.concat([df_old, stock_history_part])
        except:
            raise RuntimeError('Error obaining stock history')
    else:
        #Obtain full stock history
        try:
            #Get 10Y stock history using 10Y-period
            stock_history = ticker.history(period='10y', interval='1d', actions=True, auto_adjust=True)
        except:
            raise RuntimeError('Error obtaining stock history')

    #Remove rows with nan values (if any)
    stock_history = stock_history.dropna(how='any')

    stock_history_len = len(stock_history)
    if (stock_history_len >= mtd5y):
        try:
            #Save the history file without nan-rows for processing
            stock_history.to_csv(path / f'{tsymbol}_history.csv')
        except:
            raise RuntimeError('Stock history file RW error')
    else:
        raise ValueError('Insufficient length for stock history')

    return
