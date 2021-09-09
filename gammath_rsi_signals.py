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
        rsi_buy_score += 6
        rsi_sell_score -= 6
    elif (curr_rsi >= RSI_OVERBOUGHT_LEVEL):
        rsi_lvl = 'overbought'
        rsi_sell_score += 6
        rsi_buy_score -= 6
    else:
        rsi_lvl = ''

    rsi_max_score += 6

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

    #Get oversold days stats
    for i in range(rsi_len):
        if (rsi[i] <= RSI_OVERSOLD_LEVEL):
            curr_oversold_count += 1
            rsi_os_count_series[rsi_os_count_index] = curr_oversold_count
        else:
            if (curr_oversold_count > 0):
                rsi_os_count_index += 1

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

    rsi_os_count_series = rsi_os_count_series.dropna()
    rsi_os_count_series = rsi_os_count_series.sort_values()

    #Get percentile values
    bp, mp, tp = rsi_os_count_series.quantile([0.25, 0.5, 0.75])

    top_percentile = round(tp, 3)
    print(f'\n RSI oversold top percentile is {top_percentile}')

    #Get results description
    os_count_descr = rsi_os_count_series.describe()

    #Save it for later reference
    os_count_descr.to_csv(path / f'{tsymbol}_RSI_OSC_summary.csv')

    if (curr_oversold_count > max_oversold_days):
        max_oversold_days = curr_oversold_count

    lowest_percentile_oversold_count = round(bp, 3)
    if (curr_oversold_count >= lowest_percentile_oversold_count):
        rsi_buy_score += 1
        rsi_sell_score -= 1

    rsi_max_score += 1

    avg_oversold_days = round(mp, 3)

    if (curr_oversold_count >= avg_oversold_days):
        rsi_buy_score += 1
        rsi_sell_score -= 1

    rsi_max_score += 1

    if (curr_oversold_count >= top_percentile):
        rsi_buy_score += 1
        rsi_sell_score -= 1

    rsi_max_score += 1

    if (curr_oversold_count >= max_oversold_days):
        rsi_buy_score += 3
        rsi_sell_score -= 3

    rsi_max_score += 3

    rsi_buy_rec = f'rsi_buy_score:{rsi_buy_score}/{rsi_max_score}'
    rsi_sell_rec = f'rsi_sell_score:{rsi_sell_score}/{rsi_max_score}'
    rsi_signals = f'rsi: {rsi_avg},{rsi_lvl},{rsi_direction},{rsi_buy_rec},{rsi_sell_rec},cosd:{curr_oversold_count},losdp:{lowest_percentile_oversold_count},mosdp:{avg_oversold_days},tosdp:{top_percentile}'
    
    return rsi, rsi_buy_score, rsi_sell_score, rsi_max_score, rsi_signals
