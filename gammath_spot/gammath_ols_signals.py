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
from pathlib import Path
from scipy.stats import spearmanr
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut
from functools import lru_cache

def local_add_constant(x):
    """Removing dependence on statsmodels API"""
    #Need first column with all 1s
    return np.column_stack([np.ones(len(x)), x])

#cache and reuse same length array (help during backtesting)
@lru_cache(maxsize=1)
def centered_x_and_sq_d_sum(n):
    """(x-mean_x) and sum of squares for x=0 to (n-1) """
    x_centered = np.arange(n, dtype=float) - (n-1) / 2.0
    x_centered.flags.writeable = False #No overwrites

    #sum of squared deviation
    return x_centered, (n*((n*n)-1)) / 12.0

class local_OLS:
    """Removing dependence on statsmodels API"""
    def __init__(self, y):
        #Convert X and Y to array
        self.y = y
        self.n = len(y)

    def fit(self):
        #Get the least squares solution using closed form [better for backtesting loop]
        y, n = self.y, self.n
        xc, ssd = centered_x_and_sq_d_sum(n)
        x_mean = (n-1)/2.0
        y_mean = y.mean()

        slope = np.dot(xc, y)/ssd
        intercept = y_mean - slope * x_mean
        self.params = np.array([intercept, slope])

        self.fittedvalues = intercept + slope * (xc + x_mean)
        self.resid = y - self.fittedvalues

        sum_sq_res = np.dot(self.resid, self.resid)
        yc = y - y_mean
        sum_sq_total = yc @ yc

        self.rsquared = 1.0 - (sum_sq_res / sum_sq_total)
        return self


def get_ols_signals(tsymbol, df, path):

    mtdpy, mtd5y = gut.get_min_trading_days()

    ols_gscore = 0
    ols_max_score = 0
    ols_signals = ''
    curr_diff_sign = ''
    curr_diff_quantile_str = 'quantile ignored'
    slope_sign_5y = ''
    slope_sign_1y = ''

    #Get the price data for y-axis
    prices_len = len(df.Close)

    #We want at least 5 years of price history for generating 5Y LS line slope
    #OLS line slope is critical to conclude if dollar cost averaging strategy should be used
    if (prices_len < mtd5y):
        raise ValueError('price history too short')

    #use to_numpy instead of np.array to avoid unnecessary memcpy
    y_vals = df.Close.to_numpy(dtype=float)

    #OLS using local method

    #Model last 1 year data
    index_1y = mtdpy

    model_1y = local_OLS(y_vals[-index_1y:]).fit()

    #Model last 5 years data
    model = local_OLS(y_vals).fit()

    #Get yprediction to plot the 1y OLS line along with the price chart
    y1_predictions = model_1y.fittedvalues

    y1_predictions_len = len(y1_predictions)

    #Get yprediction to plot the 5y OLS line along with price chart
    y_predictions = model.fittedvalues

    y_predictions_len = len(y_predictions)

    #pd dataframe for 1Y predictions. Will need all elements in same size so need to fill in nan elsewhere
    y1_series = pd.Series(np.nan, pd.RangeIndex(prices_len))

    #Set the dtype for next step
    y1_predictions = pd.Series(y1_predictions, dtype='float64')

    #Put the 1y predictions in right place
    y1_series[len(y1_series)-y1_predictions_len:] = y1_predictions

    #Get the 1y residual values
    resid_1y = model_1y.resid
    resid_1y_len = len(resid_1y)

    #Get the 5y residual values
    resid_5y = model.resid
    resid_5y_len = len(resid_5y)

    #Get the R2 value for determining goodness-of-fit for 1y OLS
    fit_score_1y = round(model_1y.rsquared, 3)

    #Log the 1y score for debugging

    #Get the R2 value for determining goodness-of-fit for 5y OLS
    fit_score_5y = round(model.rsquared, 3)

    #Log the score for debugging

    #Slope of 1Y OLS line (just need to do y2-y1 to get the direction)
    slope_dir_1y = model_1y.params[1];
    if (slope_dir_1y < 0):
        slope_sign_1y = '-ve'
    else:
        slope_sign_1y = '+ve'

    #Slope of OLS line
    slope_dir_5y = model.params[1];
    if (slope_dir_5y < 0):
        slope_sign_5y = '-ve'
    else:
        slope_sign_5y = '+ve'

    curr_1y_pdiff = 0
    curr_1y_ndiff = 0
    curr_1y_diff = 0
    residual_1y = 0
    bp_1y = 0
    mp_1y = 0
    tp_1y = 0

    curr_5y_pdiff = 0
    curr_5y_ndiff = 0
    curr_5y_diff = 0
    residual_5y = 0
    bp_5y = 0
    mp_5y = 0
    tp_5y = 0

    ls_1y_ndiff_series = pd.Series(np.nan, pd.RangeIndex(resid_1y_len))
    ls_1y_ndiff_count_index = 0

    ls_1y_pdiff_series = pd.Series(np.nan, pd.RangeIndex(resid_1y_len))
    ls_1y_pdiff_count_index = 0

    ls_5y_ndiff_series = pd.Series(np.nan, pd.RangeIndex(resid_5y_len))
    ls_5y_ndiff_count_index = 0

    ls_5y_pdiff_series = pd.Series(np.nan, pd.RangeIndex(resid_5y_len))
    ls_5y_pdiff_count_index = 0

    #Get info on biggest 1y diff
    for i in range(resid_1y_len):
        residual_1y = resid_1y[i]

        if (residual_1y <= 0):
            curr_1y_ndiff = abs(residual_1y)
            ls_1y_ndiff_series[ls_1y_ndiff_count_index] = curr_1y_ndiff
            ls_1y_ndiff_count_index += 1
        else:
            curr_1y_pdiff = residual_1y
            ls_1y_pdiff_series[ls_1y_pdiff_count_index] = curr_1y_pdiff
            ls_1y_pdiff_count_index += 1

    ls_1y_ndiff_series = ls_1y_ndiff_series.dropna(how='all')
    ls_1y_pdiff_series = ls_1y_pdiff_series.dropna(how='all')

    if (residual_1y <= 0):
        #Get 1y percentile values for -ve residuals
        bp_1y, mp_1y, tp_1y = ls_1y_ndiff_series.quantile([0.25, 0.5, 0.75])
        curr_1y_diff = curr_1y_ndiff
    else:
        #Get 1y percentile values for +ve residuals
        bp_1y, mp_1y, tp_1y = ls_1y_pdiff_series.quantile([0.25, 0.5, 0.75])
        curr_1y_diff = curr_1y_pdiff

    #Get info on biggest 5y diff
    if ((prices_len != y_predictions_len) or (prices_len != len(resid_5y))):
        raise RuntimeError('Price data and prediction data length mismatched')
    else:
        for i in range(prices_len):
            residual_5y = resid_5y[i]

            if (residual_5y <= 0):
                curr_5y_ndiff = abs(residual_5y)
                ls_5y_ndiff_series[ls_5y_ndiff_count_index] = curr_5y_ndiff
                ls_5y_ndiff_count_index += 1
            else:
                curr_5y_pdiff = residual_5y
                ls_5y_pdiff_series[ls_5y_pdiff_count_index] = curr_5y_pdiff
                ls_5y_pdiff_count_index += 1

    ls_5y_ndiff_series = ls_5y_ndiff_series.dropna(how='all')
    ls_5y_pdiff_series = ls_5y_pdiff_series.dropna(how='all')

    if (residual_5y <= 0):
        #Get 5y percentile values for -ve residuals
        bp_5y, mp_5y, tp_5y = ls_5y_ndiff_series.quantile([0.25, 0.5, 0.75])
        curr_5y_diff = curr_5y_ndiff
    else:
        #Get 5y percentile values for +ve residuals
        bp_5y, mp_5y, tp_5y = ls_5y_pdiff_series.quantile([0.25, 0.5, 0.75])
        curr_5y_diff = curr_5y_pdiff


    #Best fit-score is 1; Using 0.9-1.0 as good fit (5y or 1y)
    fits_1y = ((fit_score_1y <= 1) and (fit_score_1y >= 0.9))
    fits_5y = ((fit_score_5y <= 1) and (fit_score_5y >= 0.9))

    #First establish which residual, diff and percentile values we will use based on fitness

    #5y residual is preferred as that is based on larger sample
    if (fits_5y):
        residual = residual_5y
        curr_diff = curr_5y_diff
        bp = bp_5y
        mp = mp_5y
        tp = tp_5y
        fit_score = fit_score_5y
    elif (fits_1y):
        residual = residual_1y
        curr_diff = curr_1y_diff
        bp = bp_1y
        mp = mp_1y
        tp = tp_1y
        fit_score = fit_score_1y
    else:
        residual = residual_5y
        curr_diff = curr_5y_diff
        bp = bp_5y
        mp = mp_5y
        tp = tp_5y
        fit_score = fit_score_5y

    if (slope_dir_1y <= 0):
        #Slope is -ve for last 1 year so no need to check fits or residuals
        ols_gscore -= 10
    else:
        #Finer scoring based on percentile only when there is a fit
        if (fits_5y or fits_1y):
            if (residual <= 0):
                #Below OLS line
                if (curr_diff < mp):
                    curr_diff_quantile_str = 'bottom half'

                if (curr_diff >= bp):
                    ols_gscore += 1

                    if (curr_diff >= mp):
                        ols_gscore += 2
                        curr_diff_quantile_str = 'middle quantile'

                    if (curr_diff >= tp):
                        ols_gscore += 2
                        curr_diff_quantile_str = 'top quantile'
            else:
                #Above OLS line
                if (curr_diff < mp):
                    curr_diff_quantile_str = 'bottom half'

                if (curr_diff >= bp):
                    ols_gscore -= 1

                    if (curr_diff >= mp):
                        ols_gscore -= 2
                        curr_diff_quantile_str = 'middle quantile'

                        if (curr_diff >= tp):
                            ols_gscore -= 2
                            curr_diff_quantile_str = 'top quantile'

        if (slope_dir_5y <= 0):
            #Slope is -ve for 5y but 1y is +ve so possible sign of recovery
            if (residual <= 0):
                #Below OLS line
                ols_gscore += 3
            else:
                #Above OLS line
                ols_gscore -= 3
        else:
            #Both slopes are +ve
            #Slope is -ve for 5y but 1y is +ve so possible sign of recovery
            if (residual <= 0):
                #Below OLS line
                ols_gscore += 5
            else:
                #Above OLS line
                ols_gscore -= 5


    ols_max_score += 10

    if (residual <= 0):
        curr_diff_sign = '-ve'
    else:
        curr_diff_sign = '+ve'

    #Return OLS lines data in a dataframe for plotting charts
    ols_df = pd.DataFrame({tsymbol: df.Close.to_numpy(), 'OLS': y_predictions, 'OLS_1Y': y1_series})

    #Get Information Coefficient using Spearman rank correlation coefficient
    try:
        ols_ic = round(spearmanr(ols_df.OLS.dropna(), df.Close.dropna()).correlation, 3)
    except:
        ols_ic = np.nan
        #Not a fatal error. Just log it
        print(f'Failed to compute Information Coefficient for {tsymbol} OLS')

    ols_grec = f'ols_ic:{ols_ic},ols_gscore:{ols_gscore}/{ols_max_score}'

    ols_signals = f'OLS: ols_fit_score:{fit_score},1y_slope:{slope_sign_1y},5y_slope:{slope_sign_5y},curr_diff:{curr_diff_sign},{curr_diff_quantile_str},{ols_grec}'

    #Set date as index for dataframe
    ols_df = ols_df.set_index(df.Date)

    return ols_df, ols_gscore, ols_max_score, ols_signals
