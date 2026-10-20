# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-Present, Salyl Bhagwat, Gammath Works
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
__copyright__ = 'Copyright (c) 2021-Present, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut


def kf_state_means(observed_vals, transition_covariance=1.0, observation_covariance=1.0,
                   initial_state_mean = 0.0, initial_state_covariance=1.0):
    """Replace pykalman to use local single dimension KER-adaptive Kalman filter that returns filtered state means
    Just takes the 1-D Pandas series price inputs and returns 1-D np.ndarray of shape (n,)
    """
    z = np.asarray(observed_vals, dtype=float).ravel()
    n = z.size

    Q = float(transition_covariance)
    R_initial = float(observation_covariance)
    state_means = np.empty(n, dtype=float)

    x_prediction = float(initial_state_mean)
    p_prediction = float(initial_state_covariance)

    KER_factor = gut.get_curr_ker(z)
    KER_factor[:14] = 0.0

    for t in range(n):
        if t > 0:
            #Predict step (best guess for new state is previous estimate. Uncertainty grows by Q)
            x_prediction = x_est
            p_prediction = p_est + Q

        if np.isnan(z[t]):
            x_est, p_est = x_prediction, p_prediction
        else:
            #KER factor for observation noise (high KER means low noise and low KER means high noise)
            R = R_initial * (1.0 / (KER_factor[t] + 0.05))

            #Update step
            residual_innovation = z[t] - x_prediction
            #residual variance = pred uncertainty + measurement noise
            s = p_prediction + R
            #Kalman gain (near 0 then trust the prediction; near 1 then trust the price)
            k = p_prediction / s
            x_est = x_prediction + k * residual_innovation
            p_est = (1.0-k) * p_prediction

        state_means[t] = x_est

    return state_means, KER_factor[len(KER_factor)-1]

def get_kf_state_means(tsymbol, df):

    kf_gscore = 0
    kf_max_score = 0
    kf_signals = ''
    curr_ker = 0
    curr_count_quantile_str = ''
    curr_diff_quantile_str = ''

    prices = df.Close
    prices_len = len(prices)
    sm_len = 0

    #Generate state means based on closing prices
    if (prices_len > 0):
        #Get the state mean and covariance
        state_means, curr_ker = kf_state_means(df.Close)

        #Extract state means into PD series
        ds_sm = pd.Series(state_means)
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
    kf_pos_diff_series = kf_pos_diff_series.dropna()

    #Use current diff to factor into dip score based on which quantile it falls in
    if (curr_below_mean_count > 0):

        #Get values at 25/50/75 percentile for -ve diffs
        bp, mp, tp = kf_neg_diff_series.quantile([0.25, 0.5, 0.75])

        #bigger the difference could mean better price compared to mean
        #scores are based on curr_diff greater than 25, 50, 75 percentile
        if (curr_diff < mp):
            curr_diff_quantile_str = 'bottom half'

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
            curr_diff_quantile_str = 'bottom half'

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
    kf_above_mean_count_series = kf_above_mean_count_series.dropna()

    #Compute buy/sell scores based on where current below mean count falls in 25, 50, 75 percentile
    if (curr_below_mean_count > 0):
        #Get percentile values for below mean counts
        bp, mp, tp = kf_below_mean_count_series.quantile([0.25, 0.5, 0.75])

        if (curr_below_mean_count < mp):
            curr_count_quantile_str = 'bottom half'

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
            curr_count_quantile_str = 'bottom half'

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
    kf_df = pd.DataFrame({tsymbol: df.Close, 'KER-Adaptive Kalman Filter': ds_sm})

    kf_grec = f'kf_gscore:{kf_gscore}/{kf_max_score}'

    if (curr_below_mean_count > 0):
        kf_signals = f'KF:-ve_days:{curr_count_quantile_str},-ve_diff:{curr_diff_quantile_str},{kf_grec}'
    else:
        kf_signals = f'KF:+ve_days:{curr_count_quantile_str},+ve_diff:{curr_diff_quantile_str},{kf_grec}'


    # Set date as index
    kf_df = kf_df.set_index(df.Date)

    return kf_df, kf_gscore, kf_max_score, kf_signals, curr_ker
