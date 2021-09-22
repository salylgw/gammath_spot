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

    #Check the score for fit validity
    score = lreg.score(x_vals, y_vals)

    #For now, just log it for debugging purposes
    print(f'LR model score for {tsymbol} is {score}')

    #Get yprediction to plot the OLS line along with price chart
    y_predictions = lreg.predict(x_vals)

    #Flatten it to keep it in same format as other chart data
    y_predictions = y_predictions.flatten()

    y_predictions_len = len(y_predictions)

    #For now, just check the last values
    if (df.Close[prices_len-1] <= y_predictions[y_predictions_len-1]):
        #Below OLS
        ls_buy_score += 1
        ls_sell_score -= 1
    else:
        ls_buy_score -= 1
        ls_sell_score += 1

    ls_max_score += 1

    ls_buy_rec = f'ls_buy_rec:{ls_buy_score}/{ls_max_score}'
    ls_sell_rec = f'ls_sell_rec:{ls_sell_score}/{ls_max_score}'

    ls_signals = f'LS: {ls_buy_rec},{ls_sell_rec}'

    return y_predictions, ls_buy_score, ls_sell_score, ls_max_score, ls_signals
