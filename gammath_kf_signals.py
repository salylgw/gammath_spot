# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from pykalman import KalmanFilter
import numpy as np

def get_kf_means_covariance(df):

    kf_buy_score = 0
    kf_sell_score = 0
    kf_max_score = 0
    kf_signals = ''

    #Initialize Kalman filter
    kf  = KalmanFilter(transition_matrices = [1], observation_matrices = [1], initial_state_mean = 0, initial_state_covariance = 1, observation_covariance = 1, transition_covariance=.01)

    state_means, state_covariance = kf.filter(df.Close)

    #Extract state means into PD series
    ds_sm = pd.Series(state_means.flatten())
    prices = df.Close

    sm_len = len(ds_sm)
    prices_len = len(prices)

    last_sm = ds_sm[sm_len-1]
    last_price = prices[prices_len-1]

    if (last_price > last_sm):
        kf_buy_score -= 1
        kf_sell_score += 1
    else:
        kf_buy_score += 1
        kf_sell_score -= 1

    kf_max_score += 1

    curr_below_mean_count = 0
    curr_above_mean_count = 0
    min_below_mean_days = 0
    min_above_mean_days = 0
    max_below_mean_days = 0
    max_above_mean_days = 0
    avg_below_mean_days = 0
    avg_above_mean_days = 0

    kf_below_mean_count_series = pd.Series(np.nan, pd.RangeIndex(sm_len))
    kf_above_mean_count_series = pd.Series(np.nan, pd.RangeIndex(sm_len))
    kf_below_mean_count_index = 0
    kf_above_mean_count_index = 0
    kf_max_below_mean_count = 0
    kf_max_above_mean_count = 0

    #Get below/above mean days stats
    for i in range(sm_len):
        if (prices[i] <= ds_sm[i]):
            curr_below_mean_count += 1
            if (curr_above_mean_count > 0):
                kf_above_mean_count_series[kf_above_mean_count_index] = curr_above_mean_count
                kf_above_mean_count_index += 1
                if (curr_above_mean_count > kf_max_above_mean_count):
                    kf_max_above_mean_count = curr_above_mean_count

                curr_above_mean_count = 0
        else:
            curr_above_mean_count += 1
            if (curr_below_mean_count > 0):
                kf_below_mean_count_series[kf_below_mean_count_index] = curr_below_mean_count
                kf_below_mean_count_index += 1
                if (curr_below_mean_count > kf_max_below_mean_count):
                    kf_max_below_mean_count = curr_below_mean_count

                curr_below_mean_count = 0

    if (curr_below_mean_count > kf_max_below_mean_count):
        kf_max_below_mean_count = curr_below_mean_count

    if (curr_above_mean_count > kf_max_above_mean_count):
        kf_max_above_mean_count = curr_above_mean_count

    kf_below_mean_count_series = kf_below_mean_count_series.dropna()
    kf_below_mean_count_series = kf_below_mean_count_series.sort_values()

    kf_above_mean_count_series = kf_above_mean_count_series.dropna()
    kf_above_mean_count_series = kf_above_mean_count_series.sort_values()

    #Get percentile values for below mean counts
    bp, mp, tp = kf_below_mean_count_series.quantile([0.25, 0.5, 0.75])

    bp = round(bp, 3)
    mp = round(mp, 3)
    tp = round(tp, 3)

    print(f'\n KF below mean days count percentile values are {bp}, {mp}, {tp}')

    #Get percentile values for above mean counts
    bp_am, mp_am, tp_am = kf_above_mean_count_series.quantile([0.25, 0.5, 0.75])

    bp_am = round(bp_am, 3)
    mp_am = round(mp_am, 3)
    tp_am = round(tp_am, 3)

    print(f'\n KF above mean days count percentile values are {bp_am}, {mp_am}, {tp_am}')

    if (curr_below_mean_count > bp):
        kf_buy_score += 1
        kf_sell_score -= 1

    if (curr_above_mean_count > bp_am):
        kf_sell_score += 1
        kf_buy_score -= 1

    kf_max_score += 1

    if (curr_below_mean_count > mp):
        kf_buy_score += 1
        kf_sell_score -= 1

    if (curr_above_mean_count > mp_am):
        kf_sell_score += 1
        kf_buy_score -= 1

    kf_max_score += 1

    if (curr_below_mean_count > tp):
        kf_buy_score += 1
        kf_sell_score -= 1

    if (curr_above_mean_count > tp_am):
        kf_sell_score += 1
        kf_buy_score -= 1

    kf_max_score += 1

    kf_buy_rec = f'kf_buy_rec:{kf_buy_score}/{kf_max_score}'
    kf_sell_rec = f'kf_sell_rec:{kf_sell_score}/{kf_max_score}'

    if (curr_below_mean_count > 0):
        kf_signals = f'KF: {kf_buy_rec},{kf_sell_rec},cbmdc: {curr_below_mean_count}, bp:{bp}, mp:{mp}, tp:{tp}, mbmdc: {kf_max_below_mean_count}'
    else:
        kf_signals = f'KF: {kf_buy_rec},{kf_sell_rec},camdc: {curr_above_mean_count}, bp:{bp_am}, mp:{mp_am}, tp:{tp_am}, mamdc: {kf_max_above_mean_count}'

    return state_means, state_covariance, kf_buy_score, kf_sell_score, kf_max_score, kf_signals
