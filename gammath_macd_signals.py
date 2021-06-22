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

MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9

def get_macd_signals(df):

    macd, macd_signal, macd_histogram = MACD(df.Close, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD)

    macd_len = len(macd)
    if (macd_len<=0):
        return

    macd_buy_score = 0
    macd_sell_score = 0
    macd_max_score = 0

    macd_trend = ''
    if (macd_histogram[macd_len-1] > 0):
        macd_trend = 'positive'
        macd_buy_score += 1
    else:
        macd_trend = 'negative'
        macd_sell_score += 1

    macd_max_score += 1

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

    for i in range(macd_len-1):
        if ((macd_histogram[i] <= 0) and (macd_histogram[i+1] > 0)):
            #Buy signal
            buy_sig = 1
            sell_sig = 0
            curr_days_in_positive = 1
            curr_days_in_negative = 0
            last_buy_signal_index = i+1
            curr_macd_pdiff = round(macd_histogram[i+1], 3)
        elif ((macd_histogram[i] >= 0) and (macd_histogram[i+1] < 0)):
            #Sell signal
            buy_sig = 0
            sell_sig = 1
            curr_days_in_negative = 1
            curr_days_in_positive = 0
            last_sell_signal_index = i+1
            curr_macd_ndiff = round(abs(macd_histogram[i+1]), 3)
        else:
            buy_sig = 0
            sell_sig = 0
            if (curr_days_in_positive != 0):
                curr_days_in_positive += 1
                curr_macd_pdiff = round(macd_histogram[i+1], 3)
            elif (curr_days_in_negative != 0):
                curr_days_in_negative += 1
                curr_macd_ndiff = round(abs(macd_histogram[i+1]), 3)

        if (max_days_in_positive < curr_days_in_positive):
            max_days_in_positive = curr_days_in_positive

        if (max_days_in_negative < curr_days_in_negative):
            max_days_in_negative = curr_days_in_negative
            
        if (max_macd_pdiff < curr_macd_pdiff):
            max_macd_pdiff = round(curr_macd_pdiff, 3)
            
        if (max_macd_ndiff < curr_macd_ndiff):
            max_macd_ndiff = round(curr_macd_ndiff, 3)

    if (buy_sig == 1):
        macd_buy_score += 1
    elif (sell_sig == 1):
        macd_sell_score += 1

    macd_max_score += 1

    #Save the last buy and sell signal dates
    macd_buy_signal_date = df['Date'][last_buy_signal_index]
    buy_sig_price = df['Close'][last_buy_signal_index]
    buy_sig_price_str = f'sig_price:%5.3f' % df['Close'][last_buy_signal_index]
    macd_sell_signal_date = df['Date'][last_sell_signal_index]
    sell_sig_price = df['Close'][last_sell_signal_index]
    sell_sig_price_str = f'sig_price:%5.3f' % df['Close'][last_sell_signal_index]

    if ((curr_macd_ndiff > 0) and (curr_macd_ndiff >= (max_macd_ndiff/2))):
        macd_buy_score += 1

    if ((curr_macd_pdiff > 0) and (curr_macd_pdiff >= (max_macd_pdiff/2))):
        macd_sell_score += 1

    macd_max_score += 1

    if (curr_days_in_negative >= max_days_in_negative/2):
        macd_buy_score += 1

    if (curr_days_in_positive >= max_days_in_positive/2):
        macd_sell_score += 1

    macd_max_score += 1

    #Get current stock price
    current_price = df['Close'][len(df)-1]

    if (buy_sig_price > current_price):
        macd_buy_score += 1
        macd_sell_score -= 1
    else:
        macd_buy_score -= 1
        macd_sell_score += 1
    
    if (sell_sig_price < current_price):
        macd_sell_score += 1
        macd_buy_score -= 1
    else:
        macd_sell_score -= 1
        macd_buy_score += 1

    macd_max_score += 1

    macd_buy_rec = f'macd_buy_score:{macd_buy_score}/{macd_max_score}'
    macd_sell_rec = f'macd_sell_score:{macd_sell_score}/{macd_max_score}'

    macd_buy_sell_sig_date = ''
    if (macd_trend == 'positive'):
        macd_buy_sell_stats = f'bsd:{macd_buy_signal_date},{buy_sig_price_str},pt_days:{curr_days_in_positive},pt_max_days:{max_days_in_positive},curr_diff:{curr_macd_pdiff},max_diff:{max_macd_pdiff}'
    else:
        macd_buy_sell_stats = f'ssd:{macd_sell_signal_date},{sell_sig_price_str},nt_days:{curr_days_in_negative},nt_max_days:{max_days_in_negative},curr_diff:-{curr_macd_ndiff},max_diff:-{max_macd_ndiff}'

    macd_signals = f'MACD trend:{macd_trend},{macd_buy_sell_stats},{macd_buy_rec},{macd_sell_rec}'
    
    return macd, macd_signal, macd_buy_score, macd_sell_score, macd_max_score, macd_signals
