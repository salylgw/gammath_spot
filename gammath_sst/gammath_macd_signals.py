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

def get_macd_signals(tsymbol, df, path):

    MACD_FAST_PERIOD = 12
    MACD_SLOW_PERIOD = 26
    MACD_SIGNAL_PERIOD = 9

    macd_dip_score = 0
    macd_max_score = 0

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

    #Get percentile values for +ve trend days counts
    bpp, mpp, tpp = macd_pos_days_count_series.quantile([0.25, 0.5, 0.75])

    #Get percentile values for -ve diff
    bnp_diff, mnp_diff, tnp_diff = macd_neg_diff_count_series.quantile([0.25, 0.5, 0.75])

    #Get percentile values for +ve diff
    bpp_diff, mpp_diff, tpp_diff = macd_pos_diff_count_series.quantile([0.25, 0.5, 0.75])

    #Buy/Sell signal moment is only a small part of the equation; No scoring on the start of the indication

    #Check which percentile quarter do current -ve and +ve trend days fall
    if (curr_days_in_negative > 0):
        #It has just crossed over to sell side so don't buy at least until we hit 25 percentile of -ve days
        if (curr_days_in_negative < bnp):
            macd_dip_score -= 10
        else:
            #Increase buy score at 25, 50 and 75 percentile crossing
            if (curr_days_in_negative >= bnp):
                macd_dip_score += 1

            if (curr_days_in_negative >= mnp):
                macd_dip_score += 2

            if (curr_days_in_negative >= tnp):
                macd_dip_score += 2

            #Check which percentile quarter do current -ve and +ve diff fall
            if (curr_macd_ndiff > 0):
                #Increase buy score at 50 and 25 percentile diffs
                if (curr_macd_ndiff <= mnp_diff):
                    macd_dip_score += 2

                if (curr_macd_ndiff <= bnp_diff):
                    macd_dip_score += 3

    elif (curr_days_in_positive > 0):
        #It has just crossed over to buy side so buy only until we hit 25 percentile of +ve days
        if (curr_days_in_positive < bpp):
            if (curr_macd_pdiff < mpp_diff):
                macd_dip_score += 5
            else:
                macd_dip_score -= 5
        else:
            #Increase sell score at 25, 50 and 75 percentile crossing
            if (curr_days_in_positive >= bpp):
                macd_dip_score -= 1

            if (curr_days_in_positive >= mpp):
                macd_dip_score -= 2

            if (curr_days_in_positive >= tpp):
                macd_dip_score -= 2

            if (curr_macd_pdiff > 0):
                #Increase sell score at 50 and 75 percentile crossing

                if (curr_macd_pdiff >= mpp_diff):
                    macd_dip_score -= 2

                if (curr_macd_pdiff >= tpp_diff):
                    macd_dip_score -= 3


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

    #Round off diff values to take less space while displaying
    bnp_diff = round(bnp_diff, 3)
    mnp_diff = round(mnp_diff, 3)
    tnp_diff = round(tnp_diff, 3)

    bpp_diff = round(bpp_diff, 3)
    mpp_diff = round(mpp_diff, 3)
    tpp_diff = round(tpp_diff, 3)

    #Format the strings to log
    macd_dip_rec = f'macd_dip_score:{macd_dip_score}/{macd_max_score}'

    macd_buy_sell_sig_date = ''
    if (macd_trend == 'positive'):
        macd_buy_sell_stats = f'bsd:{macd_buy_signal_date},{buy_sig_price_str},pt_days:{curr_days_in_positive},pt_max_days:{max_days_in_positive},bpp:{bpp},mpp:{mpp},tpp:{tpp},curr_diff:{curr_macd_pdiff},max_diff:{max_macd_pdiff},bpp_diff:{bpp_diff},mpp_diff:{mpp_diff},tpp_diff:{tpp_diff}'
    else:
        macd_buy_sell_stats = f'ssd:{macd_sell_signal_date},{sell_sig_price_str},nt_days:{curr_days_in_negative},nt_max_days:{max_days_in_negative},bnp:{bnp},mnp:{mnp},tnp:{tnp},curr_diff:-{curr_macd_ndiff},max_diff:-{max_macd_ndiff},bnp_diff:{bnp_diff},mnp_diff:{mnp_diff},tnp_diff:{tnp_diff}'

    macd_signals = f'MACD trend:{macd_trend},{macd_buy_sell_stats},{macd_dip_rec}'
    
    return macd, macd_signal, macd_dip_score, macd_max_score, macd_signals
