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

    #Using MFI only to look for probable price direction reversal indicator
    mfi_indicator = 'Probable Reversal not detected'

    prices = df.Close
    prices_len = len(prices)
    if (prices_len <= 0):
        print(f'\nError: Incorrect length of Price dataframe for {tsymbol}')
        mfi_signals = f'MFI:ERROR'
        return mfi_signals

    try:
        mfi = MFI(df.High, df.Low, df.Close, df.Volume, timeperiod=MFI_TIME_PERIOD)
    except:
        print(f'\nError: getting MFI for {tsymbol}')
        mfi_signals = f'MFI:ERROR'
        return mfi_signals

    lp = prices[prices_len-1]
    lpm1 = prices[prices_len-2]

    #Get current price direction
    if (lp < lpm1):
        price_dir = 'falling'
    elif (lp > lpm1):
        price_dir = 'rising'
    else:
        price_dir = 'direction_unclear'

    mfi_len = len(mfi)

    #Look for reversal when overbought/oversold
    if (mfi_len > 0):
        curr_mfi = mfi[mfi_len-1]
        lm1_mfi = mfi[mfi_len-2]

        if ((curr_mfi < lm1_mfi) and (curr_mfi >= MFI_OVERBOUGHT_LEVEL)):
            mfi_dir = 'falling'
            if (price_dir == 'rising'):
                mfi_indicator = 'Overbought and reversal probable. Price could start falling'
        elif ((curr_mfi > lm1_mfi) and (curr_mfi <= MFI_OVERSOLD_LEVEL)):
            mfi_dir = 'rising'
            if (price_dir == 'falling'):
                mfi_indicator = 'Oversold and reversal probable. Price could start rising'
    else:
        print(f'\nError: MFI length is 0 for {tsymbol}')

    mfi_signals = f'mfi:{mfi_indicator}'
    
    return mfi_signals
    
    
