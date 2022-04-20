# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2022, Salyl Bhagwat, Gammath Works
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
__copyright__ = 'Copyright (c) 2021-2022, Salyl Bhagwat, Gammath Works'

import pandas as pd
import yfinance as yf
from datetime import datetime
from pathlib import Path
import sys


def get_ticker_history(tsymbol, ticker, path):

    if (len(tsymbol) == 0):
        raise ValueError('Invalid symbol')

    try:
        # Get 10Y stock history using 10Y-period
        stock_history = ticker.history('10y', interval='1d', actions=True,auto_adjust=True)
    except:
        raise RuntimeError('Error obtaining stock history')

    stock_history_len = len(stock_history)

    if (stock_history_len > 0):
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        try:
            update_file = True

            #Always save the original price history for reference
            stock_history.to_csv(path / f'{tsymbol}_history_orig.csv')

            #Entries with nan values cause problems during analysis so drop those
            #Save the new history after dropping rows with nan values
            stock_history.dropna(how='any').to_csv(path / f'{tsymbol}_history_orig_changed.csv')

            #Read old history for comparison (if it exists)
            history_file_exists = (path / f'{tsymbol}_history.csv').exists()

            if (history_file_exists):
                #Get the len of existng file without nan-rows
                df_old = pd.read_csv(path / f'{tsymbol}_history.csv')
                df_old_len = len(df_old)

                #Get the len of new file without nan-rows
                df_new_changed = pd.read_csv(path / f'{tsymbol}_history_orig_changed.csv')
                df_new_changed_len = len(df_new_changed)

                if (df_new_changed_len < df_old_len):
                    print(f'\nNew file is shorter. New len: {df_new_len}, Old len: {df_old_len}')
                    # This is a workaround for cases where history file has missing data for
                    # few days prior to last day. In such cases, last day's data exists.
                    # This could cause incorrect analysis so I'm maintaining older file and
                    # using that where only last day's data doesn't exist.
                    # A Note in the CSV with overall gScores will indicate that today's
                    # data is missing so result can be ignored or today's data can be
                    # rechecked manually or in such cases, re-running scraper seems to
                    # get proper history and then this workaroud won't be used

                    # Don't replace old file as it has more data.
                    update_file = False

            if (update_file):
                #Save the history file without nan-rows for processing
                stock_history.dropna(how='any').to_csv(path / f'{tsymbol}_history.csv')

        except:
            raise RuntimeError('Stock history file RW error')
    else:
        raise ValueError('Invalid length stock history')

    return
