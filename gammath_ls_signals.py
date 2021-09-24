# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np
from sklearn import linear_model

def get_ls_signals(tsymbol, df):

    ls_buy_score = 0
    ls_sell_score = 0
    ls_max_score = 0
    ls_signals = ''

    prices_len = len(df.Close)
    y_vals = np.array(df.Close)
    x_vals = np.array([x for x in range(prices_len)])

    #Multiple samples for single feature
    y_vals = y_vals.reshape(-1, 1)
    x_vals = x_vals.reshape(-1, 1)

    #Linear Regression object
    lreg = linear_model.LinearRegression()

    #Fit the model for x and y values
    lreg.fit(x_vals, y_vals)

    #Get yprediction to plot the OLS line along with price chart
    y_predictions = lreg.predict(x_vals)

    #Get the R2 coeff/prediction score
    pscore = round(lreg.score(x_vals, y_vals), 3)

    #Log the score for debugging
    print(f'LR model pscore for {tsymbol} is {pscore}')

    #Flatten it to keep it in same format as other chart data
    y_predictions = y_predictions.flatten()

    y_predictions_len = len(y_predictions)

    max_ndiff = 0
    max_pdiff = 0
    curr_pdiff = 0
    curr_ndiff = 0
    curr_diff = 0
    max_diff = 0
    cprice = 0
    cpredict = 0
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
    if (prices_len != y_predictions_len):
        print('Price data and prediction data length mismatched')
    else:
        for i in range(prices_len):
            cprice = df.Close[i]
            cpredict = y_predictions[i]

            if (cprice <= cpredict):
                curr_ndiff = (cpredict - cprice)
                ls_ndiff_series[ls_ndiff_count_index] = curr_ndiff
                ls_ndiff_count_index += 1
                if (max_ndiff < curr_ndiff):
                    max_ndiff = curr_ndiff
            else:
                curr_pdiff = (cprice - cpredict)
                ls_pdiff_series[ls_pdiff_count_index] = curr_pdiff
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

    cp = df.Close[prices_len-1]
    cyp = y_predictions[y_predictions_len-1]

    if (cp <= cyp):
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
    if ((pscore <= 1) and (pscore >= 0.9)):
        if (cp <= cyp):
            #Below OLS line
            if (curr_diff > bp):
                ls_buy_score += 1
                ls_sell_score -= 1
            else:
                ls_buy_score -= 3
                ls_sell_score += 3

            if (curr_diff > mp):
                ls_buy_score += 1
                ls_sell_score -= 1

            if (curr_diff > tp):
                ls_buy_score += 1
                ls_sell_score -= 1
        else:
            #Above OLS line
            if (curr_diff > bp):
                ls_buy_score -= 1
                ls_sell_score += 1

            if (curr_diff > mp):
                ls_buy_score -= 1
                ls_sell_score += 1

            if (curr_diff > tp):
                ls_buy_score -= 1
                ls_sell_score += 1
    else:
        #Less weight for lesser score
        if (cp <= cyp):
            #Below OLS line
            if (curr_diff > mp):
                ls_buy_score += 1
                ls_sell_score -= 1
        else:
            #Above OLS line
            if (curr_diff > mp):
                ls_buy_score -= 1
                ls_sell_score += 1

    ls_max_score += 3

    curr_diff = round(curr_diff, 3)
    max_diff = round(max_diff, 3)
    bp = round(bp, 3)
    mp = round(mp, 3)
    tp = round(tp, 3)

    ls_buy_rec = f'ls_buy_rec:{ls_buy_score}/{ls_max_score}'
    ls_sell_rec = f'ls_sell_rec:{ls_sell_score}/{ls_max_score}'

    ls_signals = f'LS: {ls_buy_rec},{ls_sell_rec},pscore:{pscore},cdiff:{curr_diff},bp:{bp},mp:{mp},tp:{tp},max_diff:{max_diff}'

    return y_predictions, ls_buy_score, ls_sell_score, ls_max_score, ls_signals
