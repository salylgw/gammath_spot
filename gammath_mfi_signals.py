# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from pathlib import Path
from talib import MFI

MFI_TIME_PERIOD = 14
MFI_OVERSOLD_LEVEL = 20
MFI_OVERBOUGHT_LEVEL = 80

def get_mfi_signals(df):

    mfi = MFI(df.High, df.Low, df.Close, df.Volume, timeperiod=MFI_TIME_PERIOD)
    mfi_ds = mfi.describe()
    mfi_mean = mfi_ds['mean']
    mfi_len = len(mfi)

    mfi_avg = ''
    mfi_dir = ''
    mfi_lvl = ''

    mfi_buy_score = 0
    mfi_sell_score = 0
    mfi_max_score = 0

    if (mfi_len > 0):
        curr_mfi = mfi[mfi_len-1]
        lm1_mfi = mfi[mfi_len-2]
        lm2_mfi = mfi[mfi_len-3]

        if ((curr_mfi < lm1_mfi) and (lm1_mfi < lm2_mfi)):
            mfi_dir = 'falling'

            mfi_sell_score += 1
            mfi_buy_score -= 1

        elif ((curr_mfi > lm1_mfi) and (lm1_mfi > lm2_mfi)):
            mfi_dir = 'rising'

            mfi_buy_score += 1
            mfi_sell_score -= 1

        else:
            mfi_dir = 'direction unclear'

        mfi_max_score += 1

        if (curr_mfi < mfi_mean):
            mfi_avg = 'below average'
            mfi_buy_score += 1
        elif (curr_mfi > mfi_mean):
            mfi_avg = 'above average'
            mfi_sell_score += 1
        else:
            mfi_avg = 'average'

        mfi_max_score += 1

        if (curr_mfi >= MFI_OVERBOUGHT_LEVEL):
            mfi_lvl = 'overbought'
            mfi_sell_score += 1
            mfi_buy_score -= 1
            
        elif (curr_mfi <= MFI_OVERSOLD_LEVEL):
            mfi_lvl = 'oversold'
            mfi_buy_score += 1
            mfi_sell_score -= 1
        else:
            mfi_lvl = ''

        mfi_max_score += 1

    curr_oversold_count = 0
    min_oversold_days = 0
    max_oversold_days = 0
    avg_oversold_days = 0

    #Get oversold days stats
    for i in range(mfi_len):
        if (mfi[i] <= MFI_OVERSOLD_LEVEL):
            curr_oversold_count += 1
        else:
            if ((min_oversold_days > 0) and (curr_oversold_count > 0)):
                if (min_oversold_days > curr_oversold_count):
                    min_oversold_days = curr_oversold_count
            elif (min_oversold_days == 0):
                min_oversold_days = curr_oversold_count

            if ((max_oversold_days > 0) and (curr_oversold_count > 0)):
                if (max_oversold_days < curr_oversold_count):
                    max_oversold_days = curr_oversold_count
            elif (max_oversold_days == 0):
                max_oversold_days = curr_oversold_count

            curr_oversold_count = 0

    if (curr_oversold_count > max_oversold_days):
        max_oversold_days = curr_oversold_count

    avg_oversold_days = (min_oversold_days + max_oversold_days)/2

    if (curr_oversold_count >= min_oversold_days):
        mfi_buy_score += 1
        mfi_sell_score -= 1

    mfi_max_score += 1

    if (curr_oversold_count >= avg_oversold_days):
        mfi_buy_score += 1
        mfi_sell_score -= 1

    mfi_max_score += 1

    if (curr_oversold_count >= max_oversold_days):
        mfi_buy_score += 1
        mfi_sell_score -= 1

    mfi_max_score += 1

    mfi_buy_rec = f'mfi_buy_score:{mfi_buy_score}/{mfi_max_score}'
    mfi_sell_rec = f'mfi_sell_score:{mfi_sell_score}/{mfi_max_score}'

    mfi_signals = f'mfi:{mfi_avg},{mfi_dir},{mfi_lvl},{mfi_buy_rec},{mfi_sell_rec},miosd:{min_oversold_days},maxosd:{max_oversold_days},avosd:{avg_oversold_days},cosd:{curr_oversold_count}'
    
    return mfi, mfi_buy_score, mfi_sell_score, mfi_max_score, mfi_signals
    
    
