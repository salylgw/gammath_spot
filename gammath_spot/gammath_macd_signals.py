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
from datetime import datetime
from pathlib import Path
from talib import RSI, BBANDS, MACD, MFI, STOCH
import numpy as np

def get_macd_signals(tsymbol, df, path):

    MACD_FAST_PERIOD = 12
    MACD_SLOW_PERIOD = 26
    MACD_SIGNAL_PERIOD = 9

    macd_gscore = 0
    macd_max_score = 0
    curr_count_quantile_str = ''
    curr_diff_quantile_str = ''

    try:
        macd, macd_signal, macd_histogram = MACD(df.Close, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD)
    except:
        raise RuntimeError('MACD data generation failed')

    macd_len = len(macd)
    if (macd_len <= 0):
        raise ValueError('MACD data length error')

    #Check current MACD trend
    macd_trend = ''
    if (macd_histogram[macd_len-1] > 0):
        macd_trend = 'positive'
    else:
        macd_trend = 'negative'

    #Generally speaking, buy signal is when -ve to +ve crossover is encountered and sell signal is when +ve to -ve crossover is encountered. However, here, we are not using the buy/sell signal; instead we are using the trends and difference to get better price before the crossover is seen i.e. higher dip score during -ve trend and higher premium score during +ve trend

    curr_days_in_positive = 0
    curr_macd_pdiff = 0
    curr_days_in_negative = 0
    curr_macd_ndiff = 0
    max_macd_ndiff = 0

    last_buy_signal_index = 0
    last_sell_signal_index = 0

    macd_neg_days_count_series = pd.Series(np.nan, pd.RangeIndex(macd_len))
    macd_neg_days_count_index = 0

    macd_pos_days_count_series = pd.Series(np.nan, pd.RangeIndex(macd_len))
    macd_pos_days_count_index = 0

    macd_neg_diff_count_series = pd.Series(np.nan, pd.RangeIndex(macd_len))
    macd_neg_diff_count_index = 0

    macd_pos_diff_count_series = pd.Series(np.nan, pd.RangeIndex(macd_len))
    macd_pos_diff_count_index = 0

    #Maintain the count and diff when MACD indicates -ve trend and +ve trend
    for i in range(macd_len-1):
        if ((macd_histogram[i] <= 0) and (macd_histogram[i+1] > 0)):
            #Buy signal
            if (curr_days_in_negative > 0):
                macd_neg_days_count_series[macd_neg_days_count_index] = curr_days_in_negative
                macd_neg_days_count_index += 1

            curr_days_in_positive = 1
            curr_days_in_negative = 0
            last_buy_signal_index = i+1
            curr_macd_pdiff = round(macd_histogram[i+1], 3)
            macd_pos_diff_count_series[macd_pos_diff_count_index] = curr_macd_pdiff
            macd_pos_diff_count_index += 1
        elif ((macd_histogram[i] >= 0) and (macd_histogram[i+1] < 0)):
            #Sell signal

            if (curr_days_in_positive > 0):
                macd_pos_days_count_series[macd_pos_days_count_index] = curr_days_in_positive
                macd_pos_days_count_index += 1

            curr_days_in_negative = 1
            curr_days_in_positive = 0
            last_sell_signal_index = i+1
            curr_macd_ndiff = round(abs(macd_histogram[i+1]), 3)
            macd_neg_diff_count_series[macd_neg_diff_count_index] = curr_macd_ndiff
            macd_neg_diff_count_index += 1
        else:
            if (curr_days_in_positive != 0):
                curr_days_in_positive += 1
                curr_macd_pdiff = round(macd_histogram[i+1], 3)
                macd_pos_diff_count_series[macd_pos_diff_count_index] = curr_macd_pdiff
                macd_pos_diff_count_index += 1
            elif (curr_days_in_negative != 0):
                curr_days_in_negative += 1
                curr_macd_ndiff = round(abs(macd_histogram[i+1]), 3)
                macd_neg_diff_count_series[macd_neg_diff_count_index] = curr_macd_ndiff
                macd_neg_diff_count_index += 1

    #Drop nans and sort the vals
    macd_neg_days_count_series = macd_neg_days_count_series.dropna()
    macd_neg_days_count_series = macd_neg_days_count_series.sort_values()

    macd_neg_diff_count_series = macd_neg_diff_count_series.dropna()
    macd_neg_diff_count_series = macd_neg_diff_count_series.sort_values()

    macd_pos_days_count_series = macd_pos_days_count_series.dropna()
    macd_pos_days_count_series = macd_pos_days_count_series.sort_values()

    macd_pos_diff_count_series = macd_pos_diff_count_series.dropna()
    macd_pos_diff_count_series = macd_pos_diff_count_series.sort_values()

    #Buy/Sell signal moment is only a small part of the equation; No scoring on the start of the indication

    #Check which percentile quarter do current -ve and +ve trend days fall
    if (curr_days_in_negative > 0):
        #Get values for -ve trend days counts at 25/50/75 percentile
        bp, mp, tp = macd_neg_days_count_series.quantile([0.25, 0.5, 0.75])

        #Get values for -ve diff at 25/50/75 percentile
        bp_diff, mp_diff, tp_diff = macd_neg_diff_count_series.quantile([0.25, 0.5, 0.75])

        if (curr_macd_ndiff < mp_diff):
            curr_diff_quantile_str = 'bottom quantile'

        if (curr_macd_ndiff >= mp_diff):
            curr_diff_quantile_str = 'middle quantile'

        if (curr_macd_ndiff >= tp_diff):
            curr_diff_quantile_str = 'top quantile'

        #It has just crossed over to sell side so don't buy at least until we hit 25 percentile of -ve days
        if (curr_days_in_negative < bp):
            macd_gscore -= 10
            curr_count_quantile_str = 'bottom quantile'
        else:
            #Increase buy score at 25, 50 and 75 percentile crossing
            if (curr_days_in_negative >= bp):
                macd_gscore += 1
                curr_count_quantile_str = 'bottom quantile'

            if (curr_days_in_negative >= mp):
                macd_gscore += 2
                curr_count_quantile_str = 'middle quantile'

            if (curr_days_in_negative >= tp):
                macd_gscore += 2
                curr_count_quantile_str = 'top quantile'

            #Check which percentile quarter do current -ve and +ve diff fall
            if (curr_macd_ndiff > 0):

                if (curr_macd_ndiff >= mp_diff):
                    macd_gscore += 2

                if (curr_macd_ndiff >= tp_diff):
                    macd_gscore += 3


    elif (curr_days_in_positive > 0):

        #Get percentile values for +ve trend days counts
        bp, mp, tp = macd_pos_days_count_series.quantile([0.25, 0.5, 0.75])

        #Get percentile values for +ve diff
        bp_diff, mp_diff, tp_diff = macd_pos_diff_count_series.quantile([0.25, 0.5, 0.75])

        if (curr_macd_pdiff <= mp_diff):
            curr_diff_quantile_str = 'bottom quantile'

        if (curr_macd_pdiff > mp_diff):
            curr_diff_quantile_str = 'middle quantile'

        if (curr_macd_pdiff >= tp_diff):
            curr_diff_quantile_str = 'top quantile'

        #It has just crossed over to buy side so buy only until we hit 25 percentile of +ve days
        if (curr_days_in_positive < bp):
            if (curr_macd_pdiff < mp_diff):
                macd_gscore += 5
            else:
                macd_gscore -= 5

            curr_count_quantile_str = 'bottom quantile'

        else:
            #Increase sell score at 25, 50 and 75 percentile crossing
            if (curr_days_in_positive >= bp):
                macd_gscore -= 1
                curr_count_quantile_str = 'bottom quantile'

            if (curr_days_in_positive >= mp):
                macd_gscore -= 2
                curr_count_quantile_str = 'middle quantile'

            if (curr_days_in_positive >= tp):
                macd_gscore -= 2
                curr_count_quantile_str = 'top quantile'

            if (curr_macd_pdiff > 0):

                if (curr_macd_pdiff > mp_diff):
                    macd_gscore -= 2

                if (curr_macd_pdiff >= tp_diff):
                    macd_gscore -= 3


    macd_max_score += 10

    #Get current stock price
    current_price = df['Close'][len(df)-1]

    #Save the last buy and sell signal dates for reference
    macd_buy_signal_date = df['Date'][last_buy_signal_index]
    buy_sig_price = df['Close'][last_buy_signal_index]
    buy_sig_price_str = f'sig_price:%5.3f' % df['Close'][last_buy_signal_index]
    macd_sell_signal_date = df['Date'][last_sell_signal_index]
    sell_sig_price = df['Close'][last_sell_signal_index]
    sell_sig_price_str = f'sig_price:%5.3f' % df['Close'][last_sell_signal_index]

    #If current price is more than price at sell signal then flag it by setting MACD-gScore to -10
    if (macd_trend == 'negative'):
        if (current_price > sell_sig_price):
            macd_gscore = -10

    #Format the strings to log
    macd_grec = f'macd_gscore:{macd_gscore}/{macd_max_score}'

    macd_buy_sell_sig_date = ''
    if (macd_trend == 'positive'):
        macd_buy_sell_stats = f'{buy_sig_price_str},+ve_days_count in {curr_count_quantile_str},curr_diff in {curr_diff_quantile_str}'
    else:
        macd_buy_sell_stats = f'{sell_sig_price_str},-ve_days_count in {curr_count_quantile_str},curr_diff in {curr_diff_quantile_str}'

    macd_signals = f'MACD trend:{macd_trend},{macd_buy_sell_stats},{macd_grec}'

    #Return MACD lines in a dataframe for plotting charts with date as index
    macd_df = pd.DataFrame({'MACD': macd, 'MACD_SIGNAL': macd_signal})
    macd_df = macd_df.set_index(df.Date)

    return macd_df, macd_gscore, macd_max_score, macd_signals
