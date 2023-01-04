# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works
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
__copyright__ = 'Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works'

import pandas as pd
from talib import STOCH

def get_stochastics_slow_signals(tsymbol, df):

    STOCH_FAST_PERIOD = 14
    STOCH_SLOW_PERIOD = 3
    STOCH_OVERSOLD_LEVEL = 20
    STOCH_OVERBOUGHT_LEVEL = 80

    stoch_gscore = 0
    stoch_max_score = 0
    stoch_slow_signals = ''
    stoch_lvl = ''


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
        stoch_gscore += 2
    elif (stoch_d_curr_val > slowd_mean):
        stoch_lvl = 'above average'
        stoch_gscore -= 2
    else:
        stoch_lvl = 'average'

    stoch_max_score += 2

    #Check for stochastic oversold/overbought levels
    if (stoch_d_curr_val <= STOCH_OVERSOLD_LEVEL):
        stoch_lvl = 'oversold'
        stoch_gscore += 3
    elif (stoch_d_curr_val >= STOCH_OVERBOUGHT_LEVEL):
        stoch_lvl = 'overbought'
        stoch_gscore -= 3

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

    stoch_grec = f'stoch_gscore:{stoch_gscore}/{stoch_max_score}'

    stoch_slow_signals = f'stochs: {stoch_lvl},slowd:{stoch_slowd},l_xovr_date:{stoch_crossover_date},{stoch_grec}'

    #Return slowk and slowd in a dataframe for plotting charts with date as index
    stoch_df = pd.DataFrame({'SLOWK': slowk, 'SLOWD': slowd})
    stoch_df = stoch_df.set_index(df.Date)

    return stoch_df, stoch_gscore, stoch_max_score, stoch_slow_signals
