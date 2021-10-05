# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge

def get_ridge_signals(tsymbol, df):

    ridge_buy_score = 0
    ridge_sell_score = 0
    ridge_max_score = 0
    ridge_signals = ''

    prices_len = len(df.Close)
    lp = df.Close[prices_len-1]
    y_vals = np.array(df.Close)
    x_vals = np.array([x for x in range(prices_len)])

    #Multiple samples for single feature
    y_vals = y_vals.reshape(-1, 1)
    y_vals = y_vals.flatten()
    x_vals = x_vals.reshape(-1, 1)

    #Ridge regression model
    #WIP: experimenting
#    ridge = Ridge(fit_intercept=False, max_iter=None, normalize=False, random_state=None, solver='auto')

    ridge = Ridge(fit_intercept=True, max_iter=None, normalize=False, random_state=19, solver='auto')

    #Fit the model for x and y values
    ridge.fit(x_vals, y_vals)

    #Get yprediction to plot the regression line along with price chart
    y_predictions = ridge.predict(x_vals)
    y_predictions_len = len(y_predictions)

    last_yp = y_predictions[y_predictions_len-1]
    print(last_yp)
    print(f'Last Ridge prediction for {tsymbol} is {last_yp}')

    #Get goodness-of-fit score
    fit_score = round(ridge.score(x_vals, y_vals), 3)

    #Log the score for debugging
    print(f'Ridge model fit_score for {tsymbol} is {fit_score}')

    #Flatten the predictions to keep it in same format as other chart data
    y_predictions = y_predictions.flatten()

    ridge_buy_rec = f'ridge_buy_rec:{ridge_buy_score}/{ridge_max_score}'
    ridge_sell_rec = f'ridge_sell_rec:{ridge_sell_score}/{ridge_max_score}'

    ridge_signals = f'Ridge: {ridge_buy_rec},{ridge_sell_rec},ridge_fit_score:{fit_score}'

    return y_predictions, ridge_buy_score, ridge_sell_score, ridge_max_score, ridge_signals
