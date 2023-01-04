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
from pykalman import KalmanFilter
import numpy as np
from scipy.stats import spearmanr

def get_kf_state_means(tsymbol, df):

    kf_gscore = 0
    kf_max_score = 0
    kf_signals = ''

    curr_count_quantile_str = ''
    curr_diff_quantile_str = ''

    prices = df.Close
    prices_len = len(prices)
    sm_len = 0

    #Generate state means based on closing prices
    if (prices_len > 0):
        try:
            #Initialize Kalman filter with default params
            kf = KalmanFilter()

            #Get the state mean and covariance
            state_means, state_covariance = kf.filter(df.Close)
        except:
            raise RuntimeError('Failed to generate Kalman Filter State Means and Covariance')

        #Extract state means into PD series
        ds_sm = pd.Series(state_means.flatten())
        sm_len = len(ds_sm)

    if ((sm_len <= 0) or (prices_len <= 0)):
        raise ValueError('Incorrect length of data frame')

    #Get the most recent state mean to compare with most recent price
    last_sm = ds_sm[sm_len-1]
    last_price = prices[prices_len-1]

    #Use historical levels' comparison to current levels for computing buy/sell scores
    curr_below_mean_count = 0
    curr_above_mean_count = 0

    #init the below mean count PD series
    kf_below_mean_count_series = pd.Series(np.nan, pd.RangeIndex(sm_len))

    #init the above mean count PD series
    kf_above_mean_count_series = pd.Series(np.nan, pd.RangeIndex(sm_len))

    kf_below_mean_count_index = 0
    kf_above_mean_count_index = 0

    kf_neg_diff_index = 0
    kf_pos_diff_index = 0
    curr_diff = 0

    #Init the -ve diff PD series
    kf_neg_diff_series = pd.Series(np.nan, pd.RangeIndex(sm_len))

    #Init the +ve diff PD series
    kf_pos_diff_series = pd.Series(np.nan, pd.RangeIndex(sm_len))

    #Collect historical below/above mean days and diff stats (ignoring first 20 entries as means aren't at the desired values)
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
                curr_below_mean_count = 0

    kf_neg_diff_series = kf_neg_diff_series.dropna()
    kf_neg_diff_series = kf_neg_diff_series.sort_values()

    kf_pos_diff_series = kf_pos_diff_series.dropna()
    kf_pos_diff_series = kf_pos_diff_series.sort_values()

    #Use current diff to factor into dip score based on which quantile it falls in
    if (curr_below_mean_count > 0):

        #Get values at 25/50/75 percentile for -ve diffs
        bp, mp, tp = kf_neg_diff_series.quantile([0.25, 0.5, 0.75])

        #bigger the difference could mean better price compared to mean
        #scores are based on curr_diff greater than 25, 50, 75 percentile
        if (curr_diff < mp):
            curr_diff_quantile_str = 'bottom quantile'

        if (curr_diff >= bp):
            kf_gscore += 2

        kf_max_score += 2

        if (curr_diff >= mp):
            kf_gscore += 2
            curr_diff_quantile_str = 'middle quantile'

        kf_max_score += 2

        if (curr_diff >= tp):
            kf_gscore += 3
            curr_diff_quantile_str = 'top quantile'

        kf_max_score += 3

    else:

        #Get values at 25/50/75 percentile for +ve diffs
        bp, mp, tp = kf_pos_diff_series.quantile([0.25, 0.5, 0.75])

        #bigger the difference could mean better price compared to mean
        #scores are based on curr_diff greater than 25, 50, 75 percentile
        if (curr_diff < mp):
            curr_diff_quantile_str = 'bottom quantile'

        if (curr_diff >= bp):
            kf_gscore -= 2

        kf_max_score += 2

        if (curr_diff >= mp):
            kf_gscore -= 2
            curr_diff_quantile_str = 'middle quantile'

        kf_max_score += 2

        if (curr_diff >= tp):
            kf_gscore -= 3
            curr_diff_quantile_str = 'top quantile'

        kf_max_score += 3

    kf_below_mean_count_series = kf_below_mean_count_series.dropna()
    kf_below_mean_count_series = kf_below_mean_count_series.sort_values()

    kf_above_mean_count_series = kf_above_mean_count_series.dropna()
    kf_above_mean_count_series = kf_above_mean_count_series.sort_values()

    #Compute buy/sell scores based on where current below mean count falls in 25, 50, 75 percentile
    if (curr_below_mean_count > 0):
        #Get percentile values for below mean counts
        bp, mp, tp = kf_below_mean_count_series.quantile([0.25, 0.5, 0.75])

        if (curr_below_mean_count < mp):
            curr_count_quantile_str = 'bottom quantile'

        if (curr_below_mean_count >= bp):
            kf_gscore += 1

        kf_max_score += 1

        if (curr_below_mean_count >= mp):
            kf_gscore += 1
            curr_count_quantile_str = 'middle quantile'

        kf_max_score += 1

        if (curr_below_mean_count >= tp):
            kf_gscore += 1
            curr_count_quantile_str = 'top quantile'

        kf_max_score += 1

    else:
        #Get percentile values for above mean counts
        bp, mp, tp = kf_above_mean_count_series.quantile([0.25, 0.5, 0.75])

        if (curr_above_mean_count < mp):
            curr_count_quantile_str = 'bottom quantile'

        if (curr_above_mean_count >= bp):
            kf_gscore -= 1

        kf_max_score += 1

        if (curr_above_mean_count >= mp):
            kf_gscore -= 1
            curr_count_quantile_str = 'middle quantile'

        kf_max_score += 1

        if (curr_above_mean_count >= tp):
            kf_gscore -= 1
            curr_count_quantile_str = 'top quantile'

        kf_max_score += 1

    #Return KF state means in a dataframe for plotting charts
    kf_df = pd.DataFrame({tsymbol: df.Close, 'Kalman Filter': ds_sm})

    #Get Information Coefficient using Spearman rank correlation coefficient
    try:
        kf_ic = round(spearmanr(kf_df['Kalman Filter'].dropna(), df.Close.dropna()).correlation, 3)
    except:
        kf_ic = np.nan
        #Not a fatal error. Just log it
        print(f'Failed to compute Information Coefficient for {tsymbol} KF')

    kf_grec = f'kf_ic:{kf_ic},kf_gscore:{kf_gscore}/{kf_max_score}'

    if (curr_below_mean_count > 0):
        kf_signals = f'KF:-ve_days:{curr_count_quantile_str},-ve_diff:{curr_diff_quantile_str},{kf_grec}'
    else:
        kf_signals = f'KF:+ve_days:{curr_count_quantile_str},+ve_diff:{curr_diff_quantile_str},{kf_grec}'


    # Set date as index
    kf_df = kf_df.set_index(df.Date)

    return kf_df, kf_gscore, kf_max_score, kf_signals
