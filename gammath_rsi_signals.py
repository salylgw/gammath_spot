# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from pathlib import Path
from talib import RSI

RSI_TIME_PERIOD = 14
RSI_OVERSOLD_LEVEL = 30
RSI_OVERBOUGHT_LEVEL = 70

def get_rsi_signals(tsymbol, df, path):

    rsi = RSI(df.Close, timeperiod=RSI_TIME_PERIOD)
    rsi_len = len(rsi)
    if (rsi_len <= 0):
        return

    rsi_ds = rsi.describe()
    rsi_ds.to_csv(path / f'{tsymbol}_RSI_summary.csv')
    curr_rsi = rsi[rsi_len-1]
    print('Current RSI for ', tsymbol, ' is: ', curr_rsi, '\n')
    f = open(path / f'{tsymbol}_RSI_summary.csv', 'a')
    f.write(f'curr_rsi:{curr_rsi}')
    f.close()
    prev_rsi = rsi[rsi_len-2]
    preprev_rsi = rsi[rsi_len-3]

    rsi_buy_score = 0
    rsi_sell_score = 0
    rsi_max_score = 0

    rsi_mean = rsi_ds['mean']
    if (curr_rsi < rsi_mean):
        rsi_avg = 'below average'
        rsi_buy_score += 1
        rsi_sell_score = 0
    elif (curr_rsi > rsi_mean):
        rsi_avg = 'above average'
        rsi_sell_score += 1
        rsi_buy_score = 0
    else:
        rsi_avg = 'average'

    rsi_max_score += 1

    if (curr_rsi <= RSI_OVERSOLD_LEVEL):
        rsi_lvl = 'oversold'
        rsi_buy_score += 2
        rsi_sell_score -= 1
    elif (curr_rsi >= RSI_OVERBOUGHT_LEVEL):
        rsi_lvl = 'overbought'
        rsi_sell_score += 2
        rsi_buy_score -= 1
    else:
        rsi_lvl = ''

    rsi_max_score += 2

    if ((curr_rsi < prev_rsi) and (prev_rsi < preprev_rsi)):
        rsi_direction = 'falling'

        rsi_sell_score += 1
        rsi_buy_score -= 1

    elif ((curr_rsi > prev_rsi) and (prev_rsi > preprev_rsi)):
        rsi_direction = 'rising'

        rsi_buy_score += 1
        rsi_sell_score -= 1

    else:
        rsi_direction = 'direction_unclear'

    rsi_max_score += 1

    rsi_buy_rec = f'rsi_buy_score:{rsi_buy_score}/{rsi_max_score}'
    rsi_sell_rec = f'rsi_sell_score:{rsi_sell_score}/{rsi_max_score}'
    rsi_signals = f'rsi: {rsi_avg},{rsi_lvl},{rsi_direction},{rsi_buy_rec},{rsi_sell_rec}'
    
    return rsi, rsi_buy_score, rsi_sell_score, rsi_max_score, rsi_signals
