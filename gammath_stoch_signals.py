# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from talib import STOCH

STOCH_FAST_PERIOD = 14
STOCH_SLOW_PERIOD = 3
STOCH_OVERSOLD_LEVEL = 20
STOCH_OVERBOUGHT_LEVEL = 80

def get_stochastics_slow_signals(df):

    slowk, slowd = STOCH(df.High, df.Low, df.Close, fastk_period=STOCH_FAST_PERIOD, slowk_period=STOCH_SLOW_PERIOD, slowk_matype=0, slowd_period=STOCH_SLOW_PERIOD, slowd_matype=0)

    stoch_len = len(slowd)
    stoch_d_curr_val = slowd[stoch_len-1]
    slowd_ds = slowd.describe()
    slowd_mean = slowd_ds['mean']

    stoch_buy_score = 0
    stoch_sell_score = 0
    stoch_max_score = 0

    if (stoch_d_curr_val < slowd_mean):
        stoch_lvl = 'below average'
        stoch_buy_score += 2
        stoch_sell_score -= 2
    elif (stoch_d_curr_val > slowd_mean):
        stoch_lvl = 'above average'
        stoch_sell_score += 2
        stoch_buy_score -= 2
    else:
        stoch_lvl = 'average'
        stoch_buy_score += 1
        stoch_sell_score -= 1

    stoch_max_score += 2

    #Check for stochastic oversold/overbought levels
    stoch_lvl = ''
    if (stoch_d_curr_val <= STOCH_OVERSOLD_LEVEL):
        stoch_lvl = 'oversold'
        stoch_buy_score += 3
        stoch_sell_score -= 3
    elif (stoch_d_curr_val >= STOCH_OVERBOUGHT_LEVEL):
        stoch_lvl = 'overbought'
        stoch_sell_score += 3
        stoch_buy_score -= 3

    stoch_max_score += 3

    last_crossover_index = 0

    for i in range(stoch_len-1):
        #Detect crossovers
        if (((slowk[i] < slowd[i]) and (slowk[i+1] > slowd[i+1])) or ((slowk[i] > slowd[i]) and (slowk[i+1] < slowd[i+1]))):
            last_crossover_index = i+1

    #Get crossover date
    stoch_crossover_date = df['Date'][last_crossover_index]

    #Keep slowd value for reference
    stoch_slowd = round(slowd[stoch_len-1], 3)

    stoch_buy_rec = f'stoch_buy_rec:{stoch_buy_score}/{stoch_max_score}'
    stoch_sell_rec = f'stoch_sell_rec:{stoch_sell_score}/{stoch_max_score}'

    stoch_slow_signals = f'stochs: {stoch_lvl},slowd:{stoch_slowd},l_xovr_date:{stoch_crossover_date},{stoch_buy_rec},{stoch_sell_rec}'

    return slowk, slowd, stoch_buy_score, stoch_sell_score, stoch_max_score, stoch_slow_signals
