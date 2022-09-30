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

import yfinance as yf
from pathlib import Path
import bisect
from datetime import datetime
import pandas as pd
import time
import os
import numpy as np

def get_options_signals(tsymbol, path, curr_price, df_summ):

    options_gscore = 0
    options_max_score = 0
    shortRatio = 0

    #Get the options data from existing file for next options expiry
    if ((path / f'{tsymbol}_options_dates.csv').exists()):

        #Get the latest options expiry date
        dates_df = pd.read_csv(path / f'{tsymbol}_options_dates.csv', index_col='Unnamed: 0')

        #Next expiry date
        option_date = dates_df.loc[0][0]

        #Get the calls and puts info
        df_calls = pd.read_csv(path / f'{tsymbol}_call_{option_date}.csv')
        df_puts = pd.read_csv(path / f'{tsymbol}_put_{option_date}.csv')

        try:
            call_opts_size = len(df_calls)
            put_opts_size = len(df_puts)

            if ((call_opts_size != 0) and (put_opts_size != 0)):

                #Get index for current price in call options data
                i = bisect.bisect_right(df_calls['strike'], curr_price)

                if (i < (call_opts_size-1)):
                    bullish_start_index = i
                else:
                    bullish_start_index = 0

                #Get index for current price in put options data
                i = bisect.bisect_right(df_puts['strike'], curr_price)

                if (i < (put_opts_size-1)):
                    bearish_end_index = i
                else:
                    bearish_end_index = 0

                #Get total call open interest for curr price and higher
                total_bullish_open_interest = df_calls['openInterest'][bullish_start_index:call_opts_size-1].sum()

                #Get total put open interest for curr price and lower
                total_bearish_open_intetest = df_puts['openInterest'][0:bearish_end_index].sum()

                if (total_bullish_open_interest > total_bearish_open_intetest):
                    options_gscore += 4
                    calls_puts_string = 'Bullish'
                else:
                    options_gscore -= 4
                    calls_puts_string = 'Bearish'
            else:
                calls_puts_string = 'No calls, puts data'

        except:
            calls_puts_string = 'No calls, puts data'
    else:
        calls_puts_string = 'No calls, puts data'

    #Just immediate options expiry data so not putting too much weight
    options_max_score += 4

    #Use short ratio to read the bullish/bearish trend
    #Add weightage for buy/sell scores
    try:
        shortRatio = df_summ['shortRatio'][0]
        if (np.isnan(shortRatio)):
            short_ratio_string = 'No short_ratio data'
        else:
            short_ratio_string = f'short_ratio:{shortRatio}'
            if (shortRatio > 0):
                if (shortRatio < 3):
                    options_gscore += 6
                elif (shortRatio < 6):
                    options_gscore += 4
                elif (shortRatio < 10):
                    options_gscore += 2
                else:
                    options_gscore -= 6
            else:
                options_gscore -= 6

    except:
        short_ratio_string = 'No short_ratio data'

    options_max_score += 6

    options_grec = f'options_gscore:{options_gscore}/{options_max_score}'
    options_signals = f'options: {short_ratio_string},{calls_puts_string},{options_grec}'

    return options_gscore, options_max_score, options_signals
