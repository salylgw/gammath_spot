# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np
import statsmodels.api as sm

def get_ols_signals(tsymbol, df):

    ols_buy_score = 0
    ols_sell_score = 0
    ols_max_score = 0
    ols_signals = ''

    prices_len = len(df.Close)
    y_vals = np.array(df.Close)
    x_vals = sm.add_constant([x for x in range(prices_len)])

    #OLS using statsmodels
    model = sm.OLS(y_vals, x_vals).fit()

    #Get yprediction to plot the OLS line along with price chart
    y_predictions = model.predict()
    y_predictions_len = len(y_predictions)

    last_yp = y_predictions[y_predictions_len-1]
    print(f'Last OLS prediction for {tsymbol} is {last_yp}')

    resid = model.resid
    resid_len = len(resid)

    #Get the R2 value for determining goodness-of-fit
    fit_score = round(model.rsquared, 3)

    #Log the score for debugging
    print(f'LR OLS  model fit score for {tsymbol} is {fit_score}')

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

    ls_ndiff_series = pd.Series(np.nan, pd.RangeIndex(prices_len))
    ls_ndiff_count_index = 0

    ls_pdiff_series = pd.Series(np.nan, pd.RangeIndex(prices_len))
    ls_pdiff_count_index = 0

    #Get info on biggest diff
    if ((prices_len != y_predictions_len) or (prices_len != len(resid))):
        print('Price data and prediction data length mismatched')
    else:
        for i in range(prices_len):
            residual = resid[i]

            if (residual <= 0):
                ls_ndiff_series[ls_ndiff_count_index] = abs(residual)
                ls_ndiff_count_index += 1
                if (max_ndiff < curr_ndiff):
                    max_ndiff = curr_ndiff
            else:
                ls_pdiff_series[ls_pdiff_count_index] = residual
                ls_pdiff_count_index += 1
                if (max_pdiff < curr_pdiff):
                    max_pdiff = curr_pdiff

    ls_ndiff_series = ls_ndiff_series.dropna()
    ls_ndiff_series = ls_ndiff_series.sort_values()

    ls_pdiff_series = ls_pdiff_series.dropna()
    ls_pdiff_series = ls_pdiff_series.sort_values()

    #Get percentile values
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

    #Best score is 1; Using 0.9-1.0 as good fit
    if ((fit_score <= 1) and (fit_score >= 0.9)):
        if (residual <= 0):
            #Below OLS line
            if (curr_diff > bp):
                ols_buy_score += 1
                ols_sell_score -= 1
            else:
                ols_buy_score -= 3
                ols_sell_score += 3

            if (curr_diff > mp):
                ols_buy_score += 1
                ols_sell_score -= 1

            if (curr_diff > tp):
                ols_buy_score += 1
                ols_sell_score -= 1
        else:
            #Above OLS line
            if (curr_diff > bp):
                ols_buy_score -= 1
                ols_sell_score += 1

            if (curr_diff > mp):
                ols_buy_score -= 1
                ols_sell_score += 1

            if (curr_diff > tp):
                ols_buy_score -= 1
                ols_sell_score += 1
    else:
        #Less weight for lesser score
        if (residual <= 0):
            #Below OLS line
            if (curr_diff > mp):
                ols_buy_score += 1
                ols_sell_score -= 1
        else:
            #Above OLS line
            if (curr_diff > mp):
                ols_buy_score -= 1
                ols_sell_score += 1

    ols_max_score += 3

    curr_diff = round(curr_diff, 3)
    max_diff = round(max_diff, 3)
    bp = round(bp, 3)
    mp = round(mp, 3)
    tp = round(tp, 3)

    ols_buy_rec = f'ols_buy_rec:{ols_buy_score}/{ols_max_score}'
    ols_sell_rec = f'ols_sell_rec:{ols_sell_score}/{ols_max_score}'

    ols_signals = f'OLS: {ols_buy_rec},{ols_sell_rec},ols_fit_score:{fit_score},cdiff:{curr_diff},bp:{bp},mp:{mp},tp:{tp},max_diff:{max_diff}'

    return y_predictions, ols_buy_score, ols_sell_score, ols_max_score, ols_signals
