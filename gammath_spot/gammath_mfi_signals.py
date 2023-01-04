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
from pathlib import Path
from talib import MFI
import numpy as np


def get_mfi_signals(tsymbol, df, path):

    MFI_TIME_PERIOD = 14
    MFI_OVERSOLD_LEVEL = 20
    MFI_OVERBOUGHT_LEVEL = 80

    mfi_gscore = 0
    mfi_max_score = 0
    mfi_signals = ''

    mfi_avg = ''
    mfi_dir = ''
    mfi_lvl = ''

    #Using MFI only to look for probable price direction reversal indicator
    mfi_indicator = ''

    prices = df.Close
    prices_len = len(prices)
    if (prices_len <= 0):
        raise ValueError('Invalid Price data for generating MFI')
    else:
        lp = prices[prices_len-1]
        lpm1 = prices[prices_len-2]

    try:
        mfi = MFI(df.High, df.Low, df.Close, df.Volume, timeperiod=MFI_TIME_PERIOD)
        mfi_len = len(mfi)
        mfi_ds = mfi.describe()
        mfi_mean = mfi_ds['mean']
    except:
        raise RuntimeError('MFI data generation failed')

    #Get current price direction
    if (lp < lpm1):
        price_dir = 'falling'
    elif (lp > lpm1):
        price_dir = 'rising'
    else:
        price_dir = 'direction_unclear'

    if (mfi_len > 0):
        curr_mfi = mfi[mfi_len-1]
        lm1_mfi = mfi[mfi_len-2]

        #Get the current MFI level compared to the mean
        if (curr_mfi < mfi_mean):
            mfi_avg = 'below average'
            mfi_gscore += 3
        elif (curr_mfi > mfi_mean):
            mfi_avg = 'above average'
            mfi_gscore -= 3
        else:
            mfi_avg = 'average'

        mfi_max_score += 3

        if (curr_mfi >= MFI_OVERBOUGHT_LEVEL):
            mfi_lvl = 'overbought'
            mfi_gscore -= 4
        elif (curr_mfi <= MFI_OVERSOLD_LEVEL):
            mfi_lvl = 'oversold'
            mfi_gscore += 4
        else:
            mfi_lvl = ''

        mfi_max_score += 4

        if (curr_mfi < lm1_mfi):
            mfi_dir = 'falling'
            #Look for reversal when overbought/oversold
            if (curr_mfi >= MFI_OVERBOUGHT_LEVEL):
                if (price_dir == 'rising'):
                    mfi_indicator = 'Price could start FALLING'
                    mfi_gscore -= 3
        elif (curr_mfi > lm1_mfi):
            mfi_dir = 'rising'
            #Look for reversal when overbought/oversold
            if (curr_mfi <= MFI_OVERSOLD_LEVEL):
                if (price_dir == 'falling'):
                    mfi_indicator = 'Price could start RISING'
                    mfi_gscore += 3
        else:
            mfi_dir = 'flat'

        mfi_max_score += 3
    else:
        raise ValueError('Invalid MFI data length ')

    mfi_grec = f'mfi_gscore:{mfi_gscore}/{mfi_max_score}'

    mfi_signals = f'mfi:{mfi_avg},{mfi_dir},{mfi_lvl},{mfi_grec},{mfi_indicator}'

    #Return MFI data in a dataframe for plotting charts with date as index
    mfi_df = pd.DataFrame({'MFI': mfi})
    mfi_df = mfi_df.set_index(df.Date)

    return mfi_df, mfi_gscore, mfi_max_score, mfi_signals

