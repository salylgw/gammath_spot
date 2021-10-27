# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from pathlib import Path
from talib import MFI
import numpy as np

MFI_TIME_PERIOD = 14

MFI_OVERSOLD_LEVEL = 20
MFI_OVERBOUGHT_LEVEL = 80

def get_mfi_signals(tsymbol, df, path):

    print(f'\nGetting MFI signals for {tsymbol}')

    mfi_buy_score = 0
    mfi_sell_score = 0
    mfi_max_score = 0
    mfi_signals = ''

    mfi_avg = ''
    mfi_dir = ''
    mfi_lvl = ''

    #Using MFI only to look for probable price direction reversal indicator
    mfi_indicator = 'Probable Reversal not detected'

    prices = df.Close
    prices_len = len(prices)
    if (prices_len <= 0):
        mfi_max_score = 5
        print(f'\nError: Incorrect length of Price dataframe for {tsymbol}')
        mfi_signals = f'MFI:ERROR'
        return mfi_signals
    else:
        lp = prices[prices_len-1]
        lpm1 = prices[prices_len-2]

    try:
        mfi = MFI(df.High, df.Low, df.Close, df.Volume, timeperiod=MFI_TIME_PERIOD)
        mfi_len = len(mfi)
        mfi_ds = mfi.describe()
        mfi_mean = mfi_ds['mean']
    except:
        mfi_max_score = 5
        print(f'\nError: getting MFI for {tsymbol}')
        mfi_signals = f'MFI:ERROR'
        return mfi_signals

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
            mfi_buy_score += 1
            mfi_sell_score -= 1
        elif (curr_mfi > mfi_mean):
            mfi_avg = 'above average'
            mfi_sell_score += 1
            mfi_buy_score -= 1
        else:
            mfi_avg = 'average'

        mfi_max_score += 1

        if (curr_mfi >= MFI_OVERBOUGHT_LEVEL):
            mfi_lvl = 'overbought'
            mfi_sell_score += 2
            mfi_buy_score -= 2
        elif (curr_mfi <= MFI_OVERSOLD_LEVEL):
            mfi_lvl = 'oversold'
            mfi_buy_score += 2
            mfi_sell_score -= 2
        else:
            mfi_lvl = ''

        mfi_max_score += 2

        #Look for reversal when overbought/oversold
        if ((curr_mfi < lm1_mfi) and (curr_mfi >= MFI_OVERBOUGHT_LEVEL)):
            mfi_dir = 'falling'
            if (price_dir == 'rising'):
                mfi_indicator = 'Overbought and reversal probable. Price could start falling'
                mfi_sell_score += 2
                mfi_buy_score -= 2
        elif ((curr_mfi > lm1_mfi) and (curr_mfi <= MFI_OVERSOLD_LEVEL)):
            mfi_dir = 'rising'
            if (price_dir == 'falling'):
                mfi_indicator = 'Oversold and reversal probable. Price could start rising'
                mfi_buy_score += 2
                mfi_sell_score -= 2


        mfi_max_score += 2
    else:
        print(f'\nError: MFI length is 0 for {tsymbol}')
        mfi_signals = f'MFI:ERROR'
        mfi_max_score = 5
        return mfi_signals

    mfi_buy_rec = f'mfi_buy_score:{mfi_buy_score}/{mfi_max_score}'
    mfi_sell_rec = f'mfi_sell_score:{mfi_sell_score}/{mfi_max_score}'

    mfi_signals = f'mfi:{mfi_avg},{mfi_dir},{mfi_lvl},{mfi_buy_rec},{mfi_sell_rec},{mfi_indicator}'

    
    return mfi, mfi_buy_score, mfi_sell_score, mfi_max_score, mfi_signals

