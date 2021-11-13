# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from talib import STOCH

def get_stochastics_slow_signals(tsymbol, df):

    STOCH_FAST_PERIOD = 14
    STOCH_SLOW_PERIOD = 3
    STOCH_OVERSOLD_LEVEL = 20
    STOCH_OVERBOUGHT_LEVEL = 80

    stoch_dip_score = 0
    stoch_max_score = 0
    stoch_slow_signals = ''

    try:
        slowk, slowd = STOCH(df.High, df.Low, df.Close, fastk_period=STOCH_FAST_PERIOD, slowk_period=STOCH_SLOW_PERIOD, slowk_matype=0, slowd_period=STOCH_SLOW_PERIOD, slowd_matype=0)
    except:
        raise RuntimeError('Stochastics data generation failed')

    stoch_len = len(slowd)

    if (stoch_len <= 0):
        raise ValueError('Stochastics data length error')

    stoch_d_curr_val = slowd[stoch_len-1]
    slowd_ds = slowd.describe()
    slowd_mean = slowd_ds['mean']

    if (stoch_d_curr_val < slowd_mean):
        stoch_lvl = 'below average'
        stoch_dip_score += 2
    elif (stoch_d_curr_val > slowd_mean):
        stoch_lvl = 'above average'
        stoch_dip_score -= 2
    else:
        stoch_lvl = 'average'

    stoch_max_score += 2

    #Check for stochastic oversold/overbought levels
    stoch_lvl = ''
    if (stoch_d_curr_val <= STOCH_OVERSOLD_LEVEL):
        stoch_lvl = 'oversold'
        stoch_dip_score += 3
    elif (stoch_d_curr_val >= STOCH_OVERBOUGHT_LEVEL):
        stoch_lvl = 'overbought'
        stoch_dip_score -= 3

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

    stoch_dip_rec = f'stoch_dip_rec:{stoch_dip_score}/{stoch_max_score}'

    stoch_slow_signals = f'stochs: {stoch_lvl},slowd:{stoch_slowd},l_xovr_date:{stoch_crossover_date},{stoch_dip_rec}'

    #Return slowk and slowd in a dataframe for plotting charts
    stoch_df = pd.DataFrame({'SLOWK': slowk, 'SLOWD': slowd})

    return stoch_df, stoch_dip_score, stoch_max_score, stoch_slow_signals
