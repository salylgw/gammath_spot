# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from pathlib import Path
from talib import RSI
import numpy as np

RSI_TIME_PERIOD = 14
RSI_OVERSOLD_LEVEL = 30
RSI_OVERBOUGHT_LEVEL = 70

def get_rsi_signals(tsymbol, df, path):

    print(f'\nGetting RSI signals for {tsymbol}')

    rsi = RSI(df.Close, timeperiod=RSI_TIME_PERIOD)
    rsi_len = len(rsi)
    if (rsi_len <= 0):
        return

    rsi_ds = rsi.describe()
    rsi_ds.to_csv(path / f'{tsymbol}_RSI_summary.csv')
    curr_rsi = rsi[rsi_len-1]
    print('Current RSI for ', tsymbol, ' is: ', curr_rsi, '\n')
    f = open(path / f'{tsymbol}_RSI_summary.csv', 'a')
    f.write(f'curr_rsi,{curr_rsi}')
    f.close()
    prev_rsi = rsi[rsi_len-2]
    preprev_rsi = rsi[rsi_len-3]

    rsi_buy_score = 0
    rsi_sell_score = 0
    rsi_max_score = 0

    #Get the RSI mean for reference to check for average RSI
    rsi_mean = rsi_ds['mean']
    if (curr_rsi < rsi_mean):
        rsi_avg = 'below average'
        rsi_buy_score += 3
        rsi_sell_score -= 3
    elif (curr_rsi > rsi_mean):
        rsi_avg = 'above average'
        rsi_sell_score += 3
        rsi_buy_score -= 3
    else:
        rsi_avg = 'average'

    rsi_max_score += 3

    #Higher weights when oversold or overbought
    if (curr_rsi <= RSI_OVERSOLD_LEVEL):
        rsi_lvl = 'oversold'
    elif (curr_rsi >= RSI_OVERBOUGHT_LEVEL):
        rsi_lvl = 'overbought'
    else:
        rsi_lvl = ''

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

    curr_oversold_count = 0
    min_oversold_days = 0
    max_oversold_days = 0
    avg_oversold_days = 0

    rsi_os_count_series = pd.Series(np.nan, pd.RangeIndex(rsi_len))
    rsi_os_count_index = 0

    curr_overbought_count = 0
    min_overbought_days = 0
    max_overbought_days = 0
    avg_overbought_days = 0

    rsi_ob_count_series = pd.Series(np.nan, pd.RangeIndex(rsi_len))
    rsi_ob_count_index = 0

    #Get oversold and overbought number of days stats
    for i in range(rsi_len):
        if (rsi[i] <= RSI_OVERSOLD_LEVEL):
            curr_oversold_count += 1
            rsi_os_count_series[rsi_os_count_index] = curr_oversold_count

        if (rsi[i] >= RSI_OVERBOUGHT_LEVEL):
            curr_overbought_count += 1
            rsi_ob_count_series[rsi_ob_count_index] = curr_overbought_count

        if ((rsi[i] > RSI_OVERSOLD_LEVEL) and (curr_oversold_count > 0)):
            rsi_os_count_index += 1

            if (min_oversold_days > 0):
                if (min_oversold_days > curr_oversold_count):
                    min_oversold_days = curr_oversold_count
            elif (min_oversold_days == 0):
                min_oversold_days = curr_oversold_count

            if (max_oversold_days > 0):
                if (max_oversold_days < curr_oversold_count):
                    max_oversold_days = curr_oversold_count
            elif (max_oversold_days == 0):
                max_oversold_days = curr_oversold_count

            curr_oversold_count = 0

        if ((rsi[i] < RSI_OVERBOUGHT_LEVEL) and (curr_overbought_count > 0)):
            rsi_ob_count_index += 1

            if (min_overbought_days > 0):
                if (min_overbought_days > curr_overbought_count):
                    min_overbought_days = curr_overbought_count
            elif (min_overbought_days == 0):
                min_overbought_days = curr_overbought_count

            if (max_overbought_days > 0):
                if (max_overbought_days < curr_overbought_count):
                    max_overbought_days = curr_overbought_count
            elif (max_overbought_days == 0):
                max_overbought_days = curr_overbought_count

            curr_overbought_count = 0


    if (curr_oversold_count > max_oversold_days):
        max_oversold_days = curr_oversold_count

    if (curr_overbought_count > max_overbought_days):
        max_overbought_days = curr_overbought_count

    rsi_os_count_series = rsi_os_count_series.dropna()
    rsi_os_count_series = rsi_os_count_series.sort_values()

    rsi_ob_count_series = rsi_ob_count_series.dropna()
    rsi_ob_count_series = rsi_ob_count_series.sort_values()

    #Get percentile values for oversold days count
    bp, mp, tp = rsi_os_count_series.quantile([0.25, 0.5, 0.75])

    bp = round(bp, 3)
    mp = round(mp, 3)
    tp = round(tp, 3)

    #Get percentile values for overbought days count
    bp_ob, mp_ob, tp_ob = rsi_ob_count_series.quantile([0.25, 0.5, 0.75])

    bp_ob = round(bp_ob, 3)
    mp_ob = round(mp_ob, 3)
    tp_ob = round(tp_ob, 3)

    if (curr_oversold_count >= bp):
        rsi_buy_score += 1
        rsi_sell_score -= 1

    if (curr_overbought_count >= bp_ob):
        rsi_buy_score -= 1
        rsi_sell_score += 1

    rsi_max_score += 1

    if (curr_oversold_count >= mp):
        rsi_buy_score += 2
        rsi_sell_score -= 2

    if (curr_overbought_count >= mp_ob):
        rsi_buy_score -= 2
        rsi_sell_score += 2

    rsi_max_score += 2

    if (curr_oversold_count >= tp):
        rsi_buy_score += 3
        rsi_sell_score -= 3

    if (curr_overbought_count >= tp_ob):
        rsi_buy_score -= 3
        rsi_sell_score += 3

    rsi_max_score += 3

    rsi_buy_rec = f'rsi_buy_score:{rsi_buy_score}/{rsi_max_score}'
    rsi_sell_rec = f'rsi_sell_score:{rsi_sell_score}/{rsi_max_score}'
    rsi_signals = f'rsi: {rsi_avg},{rsi_lvl},{rsi_direction},{rsi_buy_rec},{rsi_sell_rec},cosd:{curr_oversold_count},mosd:{max_oversold_days},losdp:{bp},mosdp:{mp},tosdp:{tp},cobd:{curr_overbought_count},mobd:{max_overbought_days},lobdp:{bp_ob},mobdp:{mp_ob},tobdp:{tp_ob}'
    
    return rsi, rsi_buy_score, rsi_sell_score, rsi_max_score, rsi_signals
