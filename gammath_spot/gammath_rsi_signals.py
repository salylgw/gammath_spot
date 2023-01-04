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
from pathlib import Path
from talib import RSI
import numpy as np


def get_rsi_signals(tsymbol, df, path):

    RSI_TIME_PERIOD = 14
    RSI_OVERSOLD_LEVEL = 30
    RSI_OVERBOUGHT_LEVEL = 70

    rsi_gscore = 0
    rsi_max_score = 0
    rsi_signals = ''
    curr_count_quantile_str = ''

    try:
        rsi = RSI(df.Close, timeperiod=RSI_TIME_PERIOD)
    except:
        raise RuntimeError('RSI call failed')

    rsi_len = len(rsi)
    if (rsi_len <= 0):
        raise ValueError('Invalid length of RSI data')

    rsi_ds = rsi.describe()
    curr_rsi = rsi[rsi_len-1]
    prev_rsi = rsi[rsi_len-2]

    if (curr_rsi < prev_rsi):
        rsi_direction = 'falling'
    elif (curr_rsi > prev_rsi):
        rsi_direction = 'rising'
    else:
        rsi_direction = 'direction_unclear'

    #Get the RSI mean for reference to check for average RSI
    rsi_mean = rsi_ds['mean']
    if (curr_rsi < rsi_mean):
        rsi_avg = 'below average'
        rsi_gscore += 2
        if (rsi_direction != 'falling'):
            rsi_gscore += 2
    elif (curr_rsi > rsi_mean):
        rsi_avg = 'above average'
        rsi_gscore -= 4
    else:
        rsi_avg = 'average'

    rsi_max_score += 4

    #Higher weights when oversold or overbought
    #Score is calculated after checking percentile for number of days oversold/overbought
    if (curr_rsi <= RSI_OVERSOLD_LEVEL):
        rsi_lvl = 'oversold'
    elif (curr_rsi >= RSI_OVERBOUGHT_LEVEL):
        rsi_lvl = 'overbought'
    else:
        rsi_lvl = 'normal'

    curr_oversold_count = 0
    curr_overbought_count = 0

    avg_oversold_days = 0

    rsi_os_count_series = pd.Series(np.nan, pd.RangeIndex(rsi_len))
    rsi_os_count_index = 0

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
            curr_oversold_count = 0

        if ((rsi[i] < RSI_OVERBOUGHT_LEVEL) and (curr_overbought_count > 0)):
            rsi_ob_count_index += 1
            curr_overbought_count = 0


    rsi_os_count_series = rsi_os_count_series.dropna()
    rsi_os_count_series = rsi_os_count_series.sort_values()

    rsi_ob_count_series = rsi_ob_count_series.dropna()
    rsi_ob_count_series = rsi_ob_count_series.sort_values()


    if (curr_oversold_count > 0):
        #Get percentile values for oversold days count
        bp, mp, tp = rsi_os_count_series.quantile([0.25, 0.5, 0.75])

        if (curr_oversold_count < mp):
            curr_count_quantile_str = 'oversold day-count in bottom quantile'

        if (curr_oversold_count >= bp):
            rsi_gscore += 1

        if (curr_oversold_count >= mp):
            rsi_gscore += 2
            curr_count_quantile_str = 'oversold day-count in middle quantile'

        if (curr_oversold_count >= tp):
            rsi_gscore += 3
            curr_count_quantile_str = 'oversold day-count in top quantile'

    elif (curr_overbought_count > 0):
        #Get percentile values for overbought days count
        bp, mp, tp = rsi_ob_count_series.quantile([0.25, 0.5, 0.75])

        if (curr_overbought_count < mp):
            curr_count_quantile_str = 'overbought day-count in bottom quantile'

        if (curr_overbought_count >= bp):
            rsi_gscore -= 1

        if (curr_overbought_count >= mp):
            rsi_gscore -= 2
            curr_count_quantile_str = 'overbought day-count in middle quantile'

        if (curr_overbought_count >= tp):
            rsi_gscore -= 3
            curr_count_quantile_str = 'overbought day-count in top quantile'

    rsi_max_score += 6

    rsi_grec = f'rsi_gscore:{rsi_gscore}/{rsi_max_score}'
    rsi_signals = f'rsi: {rsi_avg},{rsi_lvl},{rsi_direction},{curr_count_quantile_str},{rsi_grec}'

    #Return RSI data in a dataframe for plotting charts with date as index
    rsi_df = pd.DataFrame({'RSI': rsi})
    rsi_df = rsi_df.set_index(df.Date)

    return rsi_df, rsi_gscore, rsi_max_score, rsi_signals
