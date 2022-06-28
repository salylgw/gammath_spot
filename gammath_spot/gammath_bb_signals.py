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
from talib import BBANDS
import numpy as np


def get_bollinger_bands_signals(tsymbol, df, path):

    BBANDS_TIME_PERIOD = 14

    try:
        #Get bollinger bands values
        ub, mb, lb = BBANDS(df.Close, timeperiod=BBANDS_TIME_PERIOD, nbdevup=2, nbdevdn=2, matype=0)
    except:
        raise RuntimeError('Bollinger Band Call Failed')

    bb_len = len(mb)

    bb_gscore = 0
    bb_max_score = 0
    bb_signals = ''

    if (bb_len <= 0):
        bb_max_score += 10
        bb_signals = f'bollinger bands: ERROR'
        raise ValueError('Bollinger Bands call return 0 length data')

    #Get current values for lower, middle and upper bands
    last_val_lb = lb[bb_len-1]
    last_val_mb = mb[bb_len-1]
    last_val_ub = ub[bb_len-1]

    #Get the most recent price from dataframe
    lp = df['Close'][bb_len-1]

    #Check current price level with respect to bollinger bands
    if (lp < last_val_mb):

        bb_avg = 'below average'
        bb_gscore += 4

        if ((last_val_mb - lp) < (abs(lp - last_val_lb))):
            bb_vicinity = 'near middle band'
            bb_gscore += 1
        else:
            #Higher buy weights when near lower band
            bb_vicinity = 'near lower band'
            bb_gscore += 6

    elif (lp > last_val_mb):

        bb_avg = 'above average'
        bb_gscore -= 4

        if ((lp - last_val_mb) < (abs(last_val_ub - lp))):
            bb_vicinity = 'near middle band'
            bb_gscore -= 1
        else:
            #Higher sell weights when near upper band
            bb_vicinity = 'near upper band'
            bb_gscore -= 6
    else:
        bb_avg = 'average'
        bb_vicinity = 'at middle band'

    bb_max_score += 10

    bb_grec = f'bb_gscore:{bb_gscore}/{bb_max_score}'
    bb_signals = f'bollinger bands:{bb_avg},{bb_vicinity},{bb_grec}'

    #Return Bollinger bands in a dataframe for plotting charts with date as index
    bb_df = pd.DataFrame({tsymbol: df.Close, 'Upper Band': ub, 'Middle Band': mb, 'Lower Band': lb})
    bb_df = bb_df.set_index(df.Date)

    return bb_df, bb_gscore, bb_max_score, bb_signals
