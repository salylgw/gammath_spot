# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from datetime import datetime
from pathlib import Path
from talib import RSI, BBANDS, MACD, MFI, STOCH
import numpy as np

MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9

def get_macd_signals(tsymbol, df, path):

    print(f'\nGetting MACD signals for {tsymbol}')

    macd, macd_signal, macd_histogram = MACD(df.Close, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD)

    macd_len = len(macd)
    if (macd_len<=0):
        return

    macd_buy_score = 0
    macd_sell_score = 0
    macd_max_score = 0

    #Check current MACD trend
    macd_trend = ''
    if (macd_histogram[macd_len-1] > 0):
        macd_trend = 'positive'
    else:
        macd_trend = 'negative'

    buy_sig = 0
    curr_days_in_positive = 0
    max_days_in_positive = 0
    curr_macd_pdiff = 0
    max_macd_pdiff = 0
    sell_sig = 0
    curr_days_in_negative = 0
    max_days_in_negative = 0
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

    #Maintain the count when MACD indicates -ve trend and +ve trend
    for i in range(macd_len-1):
        if ((macd_histogram[i] <= 0) and (macd_histogram[i+1] > 0)):
            #Buy signal
            buy_sig = 1
            sell_sig = 0

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
            buy_sig = 0
            sell_sig = 1

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
            buy_sig = 0
            sell_sig = 0
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

        #Maintain max days in +ve trend
        if (max_days_in_positive < curr_days_in_positive):
            max_days_in_positive = curr_days_in_positive

        #Maintain max days in -ve trend
        if (max_days_in_negative < curr_days_in_negative):
            max_days_in_negative = curr_days_in_negative

        #Maintain max +ve diff
        if (max_macd_pdiff < curr_macd_pdiff):
            max_macd_pdiff = round(curr_macd_pdiff, 3)

        #Maintain max -ve diff
        if (max_macd_ndiff < curr_macd_ndiff):
            max_macd_ndiff = round(curr_macd_ndiff, 3)

    #Drop nans and sort the vals
    macd_neg_days_count_series = macd_neg_days_count_series.dropna()
    macd_neg_days_count_series = macd_neg_days_count_series.sort_values()

    macd_neg_diff_count_series = macd_neg_diff_count_series.dropna()
    macd_neg_diff_count_series = macd_neg_diff_count_series.sort_values()

    macd_pos_days_count_series = macd_pos_days_count_series.dropna()
    macd_pos_days_count_series = macd_pos_days_count_series.sort_values()

    macd_pos_diff_count_series = macd_pos_diff_count_series.dropna()
    macd_pos_diff_count_series = macd_pos_diff_count_series.sort_values()

    #Get percentile values for -ve trend days counts
    bnp, mnp, tnp = macd_neg_days_count_series.quantile([0.25, 0.5, 0.75])
    print(f'\n MACD neg days percentile: {bnp}, {mnp}, {tnp}')

    #Get percentile values for +ve trend counts
    bpp, mpp, tpp = macd_pos_days_count_series.quantile([0.25, 0.5, 0.75])
    print(f'\n MACD pos percentile: {bpp}, {mpp}, {tpp}')

    #Get percentile values for -ve diff
    bnp_diff, mnp_diff, tnp_diff = macd_neg_diff_count_series.quantile([0.25, 0.5, 0.75])
    print(f'\n MACD neg diff percentile: {bnp_diff}, {mnp_diff}, {tnp_diff}')

    #Get percentile values for +ve diff
    bpp_diff, mpp_diff, tpp_diff = macd_pos_diff_count_series.quantile([0.25, 0.5, 0.75])
    print(f'\n MACD pos diff percentile: {bpp_diff}, {mpp_diff}, {tpp_diff}')

    #Get results description
    macd_neg_days_count_descr = macd_neg_days_count_series.describe()
    macd_pos_days_count_descr = macd_pos_days_count_series.describe()

    #Save results description for later reference
    macd_neg_days_count_descr.to_csv(path / f'{tsymbol}_macd_neg_days_count_summary.csv')
    macd_pos_days_count_descr.to_csv(path / f'{tsymbol}_macd_pos_days_count_summary.csv')

    #Buy/Sell signal moment is only a small part of the equation
    if (buy_sig == 1):
        macd_buy_score += 1
        macd_sell_score -= 1
    elif (sell_sig == 1):
        macd_sell_score += 1
        macd_buy_score -= 1

    macd_max_score += 1

    #Check which percentile quarter do current -ve diff fall
    if (curr_macd_ndiff > 0):
        #Increase buy score at 25, 50 and 75 percentile crossing
        if (curr_macd_ndiff >= bnp_diff):
            macd_buy_score += 1
        else:
            macd_buy_score -= 3

        if (curr_macd_ndiff >= mnp_diff):
            macd_buy_score += 1

        if (curr_macd_ndiff >= tnp_diff):
            macd_buy_score += 1

    #Check which percentile quarter do current +ve diff fall
    if (curr_macd_pdiff > 0):
        #Increase sell score at 25, 50 and 75 percentile crossing
        if (curr_macd_pdiff >= bpp_diff):
            macd_sell_score += 1
        else:
            macd_sell_score -= 3

        if (curr_macd_pdiff >= mpp_diff):
            macd_sell_score += 1

        if (curr_macd_pdiff >= tpp_diff):
            macd_sell_score += 1

    macd_max_score += 3

    #Check which percentile quarter do current -ve trend days fall
    if (curr_days_in_negative > 0):
        #Increase buy score at 25, 50 and 75 percentile crossing
        if (curr_days_in_negative >= bnp):
            macd_buy_score += 1
        else:
            macd_buy_score -= 3

        if (curr_days_in_negative >= mnp):
            macd_buy_score += 1

        if (curr_days_in_negative >= tnp):
            macd_buy_score += 1

    #Check which percentile quarter do current -ve trend days fall
    if (curr_days_in_positive > 0):
        #Increase sell score at 25, 50 and 75 percentile crossing
        if (curr_days_in_positive >= bpp):
            macd_sell_score += 1
        else:
            macd_sell_score -= 3

        if (curr_days_in_positive >= mpp):
            macd_sell_score += 1

        if (curr_days_in_positive >= tpp):
            macd_sell_score += 1

    macd_max_score += 3

    #Get current stock price
    current_price = df['Close'][len(df)-1]

    #Save the last buy and sell signal dates for reference
    macd_buy_signal_date = df['Date'][last_buy_signal_index]
    buy_sig_price = df['Close'][last_buy_signal_index]
    buy_sig_price_str = f'sig_price:%5.3f' % df['Close'][last_buy_signal_index]
    macd_sell_signal_date = df['Date'][last_sell_signal_index]
    sell_sig_price = df['Close'][last_sell_signal_index]
    sell_sig_price_str = f'sig_price:%5.3f' % df['Close'][last_sell_signal_index]

    #If current price is less than the price when buy signal was generated then it is a bargain
    if (buy_sig_price > current_price):
        macd_buy_score += 2
        macd_sell_score -= 2
    else:
        macd_buy_score -= 2
        macd_sell_score += 2

    #If current price is greater than the price when sell signal was generated then it is expensive
    if (sell_sig_price < current_price):
        macd_sell_score += 2
        macd_buy_score -= 2
    else:
        macd_sell_score -= 2
        macd_buy_score += 2

    macd_max_score += 2

    #Round off diff values to take less space while displaying
    bnp_diff = round(bnp_diff, 3)
    mnp_diff = round(mnp_diff, 3)
    tnp_diff = round(tnp_diff, 3)

    bpp_diff = round(bpp_diff, 3)
    mpp_diff = round(mpp_diff, 3)
    tpp_diff = round(tpp_diff, 3)

    #Format the strings to log
    macd_buy_rec = f'macd_buy_score:{macd_buy_score}/{macd_max_score}'
    macd_sell_rec = f'macd_sell_score:{macd_sell_score}/{macd_max_score}'

    macd_buy_sell_sig_date = ''
    if (macd_trend == 'positive'):
        macd_buy_sell_stats = f'bsd:{macd_buy_signal_date},{buy_sig_price_str},pt_days:{curr_days_in_positive},pt_max_days:{max_days_in_positive},bpp:{bpp},mpp:{mpp},tpp:{tpp},curr_diff:{curr_macd_pdiff},max_diff:{max_macd_pdiff},bpp_diff:{bpp_diff},mpp_diff:{mpp_diff},tpp_diff:{tpp_diff}'
    else:
        macd_buy_sell_stats = f'ssd:{macd_sell_signal_date},{sell_sig_price_str},nt_days:{curr_days_in_negative},nt_max_days:{max_days_in_negative},bnp:{bnp},mnp:{mnp},tnp:{tnp},curr_diff:-{curr_macd_ndiff},max_diff:-{max_macd_ndiff},bnp_diff:{bnp_diff},mnp_diff:{mnp_diff},tnp_diff:{tnp_diff}'

    macd_signals = f'MACD trend:{macd_trend},{macd_buy_sell_stats},{macd_buy_rec},{macd_sell_rec}'
    
    return macd, macd_signal, macd_buy_score, macd_sell_score, macd_max_score, macd_signals