# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path

def get_ols_signals(tsymbol, df, path):

    print(f'\nGetting OLS signals for {tsymbol}')

    ols_buy_score = 0
    ols_sell_score = 0
    ols_max_score = 0
    ols_signals = ''

    #Get the price data for y-axis
    prices_len = len(df.Close)

    if (prices_len <= 0):
        print(f'\nERROR: Incorrect length of Price dataframe for {tsymbol} while generating OLS signals')
        ols_signals = f'OLS:ERROR'
        return

    y_vals = np.array(df.Close)
    y_vals_len = len(y_vals)
    try:
        x_vals = sm.add_constant([x for x in range(prices_len)])
    except:
        print(f'\nERROR: Stats models add const API failed for {tsymbol} while generating OLS signals')
        return

    x_vals_len = len(x_vals)

    #OLS using statsmodels API

    #Model last 1 year data
    index_1y = 252 #~252 trading days/year
    try:
        model_1y = sm.OLS(y_vals[(y_vals_len-index_1y):], x_vals[(x_vals_len-index_1y):]).fit()
    except:
        print(f'\nERROR: Stats models OLS API failed for {tsymbol} while generating OLS signals')
        return

    #Model last 5 years data
    try:
        model = sm.OLS(y_vals, x_vals).fit()
    except:
        print(f'\nERROR: Stats models OLS API failed for {tsymbol} while generating OLS signals')
        return

    #Get yprediction to plot the 1y OLS line along with the price chart
    try:
        y1_predictions = model_1y.predict()
    except:
        print(f'\nERROR: Stats models OLS predict API failed for {tsymbol} while generating OLS signals')
        return

    y1_predictions_len = len(y1_predictions)

    #Get yprediction to plot the 5y OLS line along with price chart
    try:
        y_predictions = model.predict()
    except:
        print(f'\nERROR: Stats models OLS predict API failed for {tsymbol} while generating OLS signals')
        return
    y_predictions_len = len(y_predictions)

    #pd dataframe for 1Y predictions. Will need all elements in same size so need to fill in nan elsewhere
    y1_series = pd.Series(np.nan, pd.RangeIndex(prices_len))

    #Put the 1y predictions in right place
    y1_series[len(y1_series)-y1_predictions_len:] = y1_predictions

    #Get the 1y residual values
    resid_1y = model_1y.resid
    resid_1y_len = len(resid_1y)
    print(f'LR OLS 1y resid len for {tsymbol} is {resid_1y_len}')

    #Get the 5y residual values
    resid = model.resid
    resid_len = len(resid)
    print(f'LR OLS 5y resid len for {tsymbol} is {resid_len}')

    #Get the R2 value for determining goodness-of-fit for 1y OLS
    fit_score_1y = round(model_1y.rsquared, 3)

    #Log the 1y score for debugging
    print(f'LR 1Y OLS model fit score for {tsymbol} is {fit_score_1y}')

    #Get the R2 value for determining goodness-of-fit for 5y OLS
    fit_score = round(model.rsquared, 3)

    #Log the score for debugging
    print(f'LR 5Y OLS  model fit score for {tsymbol} is {fit_score}')

    #Slope of 1Y OLS line (just need to do y2-y1 to get the direction)
    slope_dir_1y = (y1_predictions[y1_predictions_len-1] - y1_predictions[0])
    print(f'LR 1Y OLS  line slope for {tsymbol} is {slope_dir_1y}')

    #Slope of OLS line
    slope_dir_5y = (y_predictions[y_predictions_len-1] - y_predictions[0])
    print(f'LR 5Y OLS  line slope for {tsymbol} is {slope_dir_5y}')

    max_1y_ndiff = 0
    max_1y_pdiff = 0
    curr_1y_pdiff = 0
    curr_1y_ndiff = 0
    curr_1y_diff = 0
    max_1y_diff = 0
    residual_1y = 0
    bnp_1y = 0
    mnp_1y = 0
    tnp_1y = 0
    bpp_1y = 0
    mpp_1y = 0
    tpp_1y = 0
    bp_1y = 0
    mp_1y = 0
    tp_1y = 0

    max_ndiff = 0
    max_pdiff = 0
    curr_pdiff = 0
    curr_ndiff = 0
    curr_diff = 0
    max_diff = 0
    residual = 0
    bnp = 0
    mnp = 0
    tnp = 0
    bpp = 0
    mpp = 0
    tpp = 0
    bp = 0
    mp = 0
    tp = 0

    ls_1y_ndiff_series = pd.Series(np.nan, pd.RangeIndex(resid_1y_len))
    ls_1y_ndiff_count_index = 0

    ls_1y_pdiff_series = pd.Series(np.nan, pd.RangeIndex(resid_1y_len))
    ls_1y_pdiff_count_index = 0

    ls_ndiff_series = pd.Series(np.nan, pd.RangeIndex(prices_len))
    ls_ndiff_count_index = 0

    ls_pdiff_series = pd.Series(np.nan, pd.RangeIndex(prices_len))
    ls_pdiff_count_index = 0

    #Get info on biggest 1y diff
    for i in range(resid_1y_len):
        residual_1y = resid_1y[i]

        if (residual_1y <= 0):
            curr_1y_ndiff = abs(residual_1y)
            ls_1y_ndiff_series[ls_1y_ndiff_count_index] = curr_1y_ndiff
            ls_1y_ndiff_count_index += 1
            if (max_1y_ndiff < curr_1y_ndiff):
                max_1y_ndiff = curr_1y_ndiff
        else:
            curr_1y_pdiff = residual_1y
            ls_1y_pdiff_series[ls_1y_pdiff_count_index] = curr_1y_pdiff
            ls_1y_pdiff_count_index += 1
            if (max_1y_pdiff < curr_1y_pdiff):
                max_1y_pdiff = curr_1y_pdiff

    ls_1y_ndiff_series = ls_1y_ndiff_series.dropna(how='all')
    ls_1y_ndiff_series = ls_1y_ndiff_series.sort_values()

    ls_1y_pdiff_series = ls_1y_pdiff_series.dropna(how='all')
    ls_1y_pdiff_series = ls_1y_pdiff_series.sort_values()

    #Get 1y percentile values for residuals
    bnp_1y, mnp_1y, tnp_1y = ls_1y_ndiff_series.quantile([0.25, 0.5, 0.75])
    print(f'\n 1Y OLS neg percentile: {bnp_1y}, {mnp_1y}, {tnp_1y}')

    bpp_1y, mpp_1y, tpp_1y = ls_1y_pdiff_series.quantile([0.25, 0.5, 0.75])
    print(f'\n 1Y OLS pos percentile: {bpp_1y}, {mpp_1y}, {tpp_1y}')

    if (residual_1y <= 0):
        curr_1y_diff = curr_1y_ndiff
        max_1y_diff = max_1y_ndiff
        bp_1y = bnp_1y
        mp_1y = mnp_1y
        tp_1y = tnp_1y
    else:
        curr_1y_diff = curr_1y_pdiff
        max_1y_diff = max_1y_pdiff
        bp_1y = bpp_1y
        mp_1y = mpp_1y
        tp_1y = tpp_1y

    #Get info on biggest 5y diff
    if ((prices_len != y_predictions_len) or (prices_len != len(resid))):
        print('Price data and prediction data length mismatched')
    else:
        for i in range(prices_len):
            residual = resid[i]

            if (residual <= 0):
                curr_ndiff = abs(residual)
                ls_ndiff_series[ls_ndiff_count_index] = curr_ndiff
                ls_ndiff_count_index += 1
                if (max_ndiff < curr_ndiff):
                    max_ndiff = curr_ndiff
            else:
                curr_pdiff = residual
                ls_pdiff_series[ls_pdiff_count_index] = curr_pdiff
                ls_pdiff_count_index += 1
                if (max_pdiff < curr_pdiff):
                    max_pdiff = curr_pdiff

    ls_ndiff_series = ls_ndiff_series.dropna(how='all')
    ls_ndiff_series = ls_ndiff_series.sort_values()

    ls_pdiff_series = ls_pdiff_series.dropna(how='all')
    ls_pdiff_series = ls_pdiff_series.sort_values()

    #Get 5y percentile values for residuals
    bnp, mnp, tnp = ls_ndiff_series.quantile([0.25, 0.5, 0.75])
    print(f'\n OLS neg percentile: {bnp}, {mnp}, {tnp}')

    bpp, mpp, tpp = ls_pdiff_series.quantile([0.25, 0.5, 0.75])
    print(f'\n OLS pos percentile: {bpp}, {mpp}, {tpp}')

    if (residual <= 0):
        curr_diff = curr_ndiff
        max_diff = max_ndiff
        bp = bnp
        mp = mnp
        tp = tnp
    else:
        curr_diff = curr_pdiff
        max_diff = max_pdiff
        bp = bpp
        mp = mpp
        tp = tpp


    #Best score is 1; Using 0.9-1.0 as good fit (5y or 1y)
    fits_1y = ((fit_score_1y <= 1) and (fit_score_1y >= 0.9))
    fits_5y = ((fit_score <= 1) and (fit_score >= 0.9))

    # Only check the fit and compute additional scores if the 1Y OLS line slope is +ve
    if (slope_dir_1y > 0):

        print(f'\n1Y OLS line slope is +ve for {tsymbol}')

        if (fits_1y or fits_5y):
            if (fits_5y):
                if (residual <= 0):

                    #Below OLS line
                    ols_buy_score += 4

                    if (curr_diff > bp):
                        ols_buy_score += 1

                        if (curr_diff > mp):
                            ols_buy_score += 2

                            if (curr_diff > tp):
                                ols_buy_score += 3
#                    else: #Diff isn't much; keep buy/sell scores as is
                else:
                    #Above OLS line
                    ols_sell_score += 4

                    if (curr_diff > bp):
                        ols_sell_score += 1

                        if (curr_diff > mp):
                            ols_sell_score += 2

                            if (curr_diff > tp):
                                ols_sell_score += 3
#                    else: #Diff isn't much; keep buy/sell scores as is
            elif (fits_1y):
                if (residual_1y <= 0):
                    #Below OLS line
                    ols_buy_score += 4

                    if (curr_1y_diff > bp_1y):
                        ols_buy_score += 1

                        if (curr_1y_diff > mp_1y):
                            ols_buy_score += 2

                            if (curr_1y_diff > tp_1y):
                                ols_buy_score += 3
#                    else: #Diff isn't much; keep buy/sell scores as is
                else:
                    #Above OLS line
                    ols_sell_score += 4

                    if (curr_1y_diff > bp_1y):
                        ols_sell_score += 1

                        if (curr_1y_diff > mp_1y):
                            ols_sell_score += 2

                            if (curr_1y_diff > tp_1y):
                                ols_sell_score += 3
#                    else: #Diff isn't much; keep buy/sell scores as is
        else:
            #Less weight for lesser lesser fit
            if (residual_1y <= 0):
                #Below OLS line
                if (curr_1y_diff > mp_1y):
                    ols_buy_score += 4
            else:
                #Above OLS line
                if (curr_1y_diff > mp_1y):
                    ols_sell_score += 4
    else:
        print(f'\nOLS line slope is -ve for {tsymbol}')
        ols_sell_score += 10
        ols_buy_score -= 10

    ols_max_score += 10

    curr_diff = round(curr_diff, 3)
    max_diff = round(max_diff, 3)
    bp = round(bp, 3)
    mp = round(mp, 3)
    tp = round(tp, 3)

    curr_1y_diff = round(curr_1y_diff, 3)
    max_1y_diff = round(max_1y_diff, 3)
    bp_1y = round(bp_1y, 3)
    mp_1y = round(mp_1y, 3)
    tp_1y = round(tp_1y, 3)

    ols_buy_rec = f'ols_buy_rec:{ols_buy_score}/{ols_max_score}'
    ols_sell_rec = f'ols_sell_rec:{ols_sell_score}/{ols_max_score}'

    if (fits_5y):
        ols_signals = f'OLS: {ols_buy_rec},{ols_sell_rec},ols_1y_fit_score:{fit_score_1y},ols_fit_score:{fit_score},cdiff:{curr_diff},bp:{bp},mp:{mp},tp:{tp},max_diff:{max_diff}'
    else:
        ols_signals = f'OLS: {ols_buy_rec},{ols_sell_rec},ols_1y_fit_score:{fit_score_1y},ols_fit_score:{fit_score},cdiff_1y:{curr_1y_diff},bp_1y:{bp_1y},mp_1y:{mp_1y},tp_1y:{tp_1y},max_1y_diff:{max_1y_diff}'

    return y1_series, y_predictions, ols_buy_score, ols_sell_score, ols_max_score, ols_signals
