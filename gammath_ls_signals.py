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

    #For now, just log it for debugging purposes
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

    #Get info on biggest diff
    if (prices_len != y_predictions_len):
        print('Price data and prediction data length mismatched')
    else:
        for i in range(prices_len):
            cprice = df.Close[i]
            cpredict = y_predictions[i]

            if (cprice <= cpredict):
                curr_ndiff = (cpredict - cprice)
                if (max_ndiff < curr_ndiff):
                    max_ndiff = curr_ndiff
            else:
                curr_pdiff = (cprice - cpredict)
                if (max_pdiff < curr_pdiff):
                    max_pdiff = curr_pdiff

    #Only use this method when R2 coeff is closer to 1
    if ((pscore <= 1) and (pscore >= 0.9)):
        if (df.Close[prices_len-1] <= y_predictions[y_predictions_len-1]):
            #Below OLS
            ls_buy_score += 1
            ls_sell_score -= 1
            curr_diff = curr_ndiff
            max_diff = max_ndiff
        else:
            ls_buy_score -= 1
            ls_sell_score += 1
            curr_diff = curr_pdiff
            max_diff = max_pdiff

        ls_max_score += 1


    ls_buy_rec = f'ls_buy_rec:{ls_buy_score}/{ls_max_score}'
    ls_sell_rec = f'ls_sell_rec:{ls_sell_score}/{ls_max_score}'

    ls_signals = f'LS: {ls_buy_rec},{ls_sell_rec},pscore:{pscore},cdiff:{curr_diff},max_diff:{max_diff}'

    return y_predictions, ls_buy_score, ls_sell_score, ls_max_score, ls_signals
