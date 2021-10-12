# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from pykalman import KalmanFilter
import numpy as np

def get_kf_state_means(tsymbol, df):

    print(f'\nGetting Kalman filter signals for {tsymbol}')

    kf_buy_score = 0
    kf_sell_score = 0
    kf_max_score = 0
    kf_signals = ''

    #Initialize Kalman filter
    kf  = KalmanFilter(transition_matrices = [1], observation_matrices = [1], initial_state_mean = 0, initial_state_covariance = 1, observation_covariance = 1, transition_covariance=.01)

    #Get the state mean and covariance
    state_means, state_covariance = kf.filter(df.Close)

    #Extract state means into PD series
    ds_sm = pd.Series(state_means.flatten())
    prices = df.Close

    sm_len = len(ds_sm)
    prices_len = len(prices)

    #Get the most recent state mean to compare with most recent price
    last_sm = ds_sm[sm_len-1]
    last_price = prices[prices_len-1]

    #Check if current price is greater or less than current state mean
    if (last_price > last_sm):
        kf_buy_score -= 1
        kf_sell_score += 1
    else:
        kf_buy_score += 1
        kf_sell_score -= 1

    kf_max_score += 1

    #Use historical levels' comparison to current levels for computing buy/sell scores
    curr_below_mean_count = 0
    curr_above_mean_count = 0
    min_below_mean_days = 0
    min_above_mean_days = 0
    max_below_mean_days = 0
    max_above_mean_days = 0
    avg_below_mean_days = 0
    avg_above_mean_days = 0

    #init the below mean count PD series
    kf_below_mean_count_series = pd.Series(np.nan, pd.RangeIndex(sm_len))

    #init the above mean count PD series
    kf_above_mean_count_series = pd.Series(np.nan, pd.RangeIndex(sm_len))

    kf_below_mean_count_index = 0
    kf_above_mean_count_index = 0
    kf_max_below_mean_count = 0
    kf_max_above_mean_count = 0

    kf_neg_diff_index = 0
    kf_pos_diff_index = 0
    curr_diff = 0

    #Init the -ve diff PD series
    kf_neg_diff_series = pd.Series(np.nan, pd.RangeIndex(sm_len))

    #Init the +ve diff PD series
    kf_pos_diff_series = pd.Series(np.nan, pd.RangeIndex(sm_len))

    #Get historical below/above mean days stats (ignoring first 20 entries as means aren't at the desired values)
    for i in range(20, sm_len):

        price = prices[i]
        sm = ds_sm[i]

        if (price <= sm):
            #Price is below state mean

            #Compute current price diff compared to state mean
            curr_diff = (sm - price)

            #Save for statistical analysis
            kf_neg_diff_series[kf_neg_diff_index] = curr_diff
            kf_neg_diff_index += 1
            curr_below_mean_count += 1

            #Check if previous iteration was above mean and if so update and save counts
            if (curr_above_mean_count > 0):
                kf_above_mean_count_series[kf_above_mean_count_index] = curr_above_mean_count
                kf_above_mean_count_index += 1
                if (curr_above_mean_count > kf_max_above_mean_count):
                    kf_max_above_mean_count = curr_above_mean_count

                curr_above_mean_count = 0
        else:
            #Price is above state mean

            #Compute current price diff compared to state mean
            curr_diff = (price - sm)

            #Save for statistical analysis
            kf_pos_diff_series[kf_pos_diff_index] = curr_diff
            kf_pos_diff_index += 1
            curr_above_mean_count += 1

            #Check if previous iteration was below mean and if so update and save counts
            if (curr_below_mean_count > 0):
                kf_below_mean_count_series[kf_below_mean_count_index] = curr_below_mean_count
                kf_below_mean_count_index += 1
                if (curr_below_mean_count > kf_max_below_mean_count):
                    kf_max_below_mean_count = curr_below_mean_count

                curr_below_mean_count = 0

    kf_neg_diff_series = kf_neg_diff_series.dropna()
    kf_neg_diff_series = kf_neg_diff_series.sort_values()

    kf_pos_diff_series = kf_pos_diff_series.dropna()
    kf_pos_diff_series = kf_pos_diff_series.sort_values()

    #Get percentile values for -ve and +ve diffs
    nd_bp, nd_mp, nd_tp = kf_neg_diff_series.quantile([0.25, 0.5, 0.75])
    pd_bp, pd_mp, pd_tp = kf_pos_diff_series.quantile([0.25, 0.5, 0.75])

    #rounding for logging purposes
    curr_diff = round(curr_diff, 3)
    nd_bp = round(nd_bp, 3)
    nd_mp = round(nd_mp, 3)
    nd_tp = round(nd_tp, 3)
    pd_bp = round(pd_bp, 3)
    pd_mp = round(pd_mp, 3)
    pd_tp = round(pd_tp, 3)

    print(f'\n KF diff from means: nd_bp:{nd_bp}, nd_mp:{nd_mp}, nd_tp:{nd_tp}, pd_bp:{pd_bp}, pd_mp:{pd_mp}, pd_tp:{pd_tp}')

    #Use current diff to factor into buy/sell score
    if (curr_below_mean_count > 0):
        print('\nUsing negative diff from KF means')

        #bigger the difference could mean better price compared to mean
        #scores are based on curr_diff greater than 25, 50, 75 percentile
        if (curr_diff > nd_bp):
            kf_buy_score += 1
            kf_sell_score -= 1

        kf_max_score += 1

        if (curr_diff > nd_mp):
            kf_buy_score += 1
            kf_sell_score -= 1

        kf_max_score += 1

        if (curr_diff > nd_tp):
            kf_buy_score += 1
            kf_sell_score -= 1

        kf_max_score += 1

    else:
        print('\nUsing positive diff from KF means')

        #bigger the difference could mean better price compared to mean
        #scores are based on curr_diff greater than 25, 50, 75 percentile
        if (curr_diff > pd_bp):
            kf_sell_score += 1
            kf_buy_score -= 1

        kf_max_score += 1

        if (curr_diff > pd_mp):
            kf_sell_score += 1
            kf_buy_score -=1

        kf_max_score += 1

        if (curr_diff > pd_tp):
            kf_sell_score += 1
            kf_buy_score -= 1

        kf_max_score += 1

    if (curr_below_mean_count > kf_max_below_mean_count):
        kf_max_below_mean_count = curr_below_mean_count

    if (curr_above_mean_count > kf_max_above_mean_count):
        kf_max_above_mean_count = curr_above_mean_count

    print('\nCleanup and organize counts series')

    kf_below_mean_count_series = kf_below_mean_count_series.dropna()
    kf_below_mean_count_series = kf_below_mean_count_series.sort_values()

    kf_above_mean_count_series = kf_above_mean_count_series.dropna()
    kf_above_mean_count_series = kf_above_mean_count_series.sort_values()

    print('\nGet percentiles mean counts')

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

    #Compute buy/sell scores based on where current below mean count falls in 25, 50, 75 percentile
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

    kf_buy_rec = f'kf_buy_score:{kf_buy_score}/{kf_max_score}'
    kf_sell_rec = f'kf_sell_score:{kf_sell_score}/{kf_max_score}'

    if (curr_below_mean_count > 0):
        kf_signals = f'KF: {kf_buy_rec},{kf_sell_rec},cbmdc: {curr_below_mean_count}, bp:{bp}, mp:{mp}, tp:{tp}, mbmdc: {kf_max_below_mean_count}, cd:{curr_diff},nd_bp:{nd_bp},nd_mp:{nd_mp},nd_tp:{nd_tp}'
    else:
        kf_signals = f'KF: {kf_buy_rec},{kf_sell_rec},camdc: {curr_above_mean_count}, bp:{bp_am}, mp:{mp_am}, tp:{tp_am}, mamdc: {kf_max_above_mean_count}, cd:{curr_diff},pd_bp:{pd_bp},pd_mp:{pd_mp},pd_tp:{pd_tp}'

    #return state means also to plot the charts
    return state_means, kf_buy_score, kf_sell_score, kf_max_score, kf_signals
