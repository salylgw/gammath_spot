# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from talib import BBANDS

BBANDS_TIME_PERIOD = 14

def get_bollinger_bands_signals(df, path):

    ub, mb, lb = BBANDS(df.Close, timeperiod=BBANDS_TIME_PERIOD, nbdevup=2, nbdevdn=2, matype=0)
    bb_len = len(ub)
    if (bb_len<=0):
        return

    last_val_mb = mb[bb_len-1]
    last_val_ub = ub[bb_len-1]
    last_val_lb = lb[bb_len-1]

    bb_buy_score = 0
    bb_sell_score = 0
    bb_max_score = 0

    #Get the most recent price from dataframe
    lp = df['Close'][bb_len-1]

    if (lp < last_val_mb):

        bb_avg = 'below average'

        if ((last_val_mb - lp) < (abs(lp - last_val_lb))):
            bb_vicinity = 'near middle band'
            bb_buy_score += 2
            bb_sell_score -= 2
        else:
            #Higher buy weights when near lower band
            bb_vicinity = 'near lower band'
            bb_buy_score += 6
            bb_sell_score -= 6

    elif (lp > last_val_mb):

        bb_avg = 'above average'

        if ((lp - last_val_mb) < (abs(last_val_ub - lp))):
            bb_vicinity = 'near middle band'
            bb_sell_score += 2
            bb_buy_score -= 2
        else:
            #Higher sell weights when near upper band
            bb_vicinity = 'near upper band'
            bb_sell_score += 6
            bb_buy_score -= 6
    else:
        bb_avg = 'average'
        bb_vicinity = 'at middle band'
        bb_buy_score += 1
        bb_sell_score -= 1

    bb_max_score += 6

    bb_buy_rec = f'bb_buy_score:{bb_buy_score}/{bb_max_score}'
    bb_sell_rec = f'bb_sell_score:{bb_sell_score}/{bb_max_score}'
    bb_signals = f'bollinger bands:{bb_avg},{bb_vicinity},{bb_buy_rec},{bb_sell_rec}'
    
    return ub, mb, lb, bb_buy_score, bb_sell_score, bb_max_score, bb_signals
