# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np
from sklearn.linear_model import Lasso

def get_lasso_signals(tsymbol, df):

    lasso_buy_score = 0
    lasso_sell_score = 0
    lasso_max_score = 0
    lasso_signals = ''

    prices_len = len(df.Close)
    lp = df.Close[prices_len-1]
    y_vals = np.array(df.Close)
    x_vals = np.array([x for x in range(prices_len)])

    #Multiple samples for single feature
    y_vals = y_vals.reshape(-1, 1)
    x_vals = x_vals.reshape(-1, 1)

    #Lasso regression model
    #WIP: experimenting with default params
    lasso = Lasso(alpha=0.1)

    #Fit the model for x and y values
    lasso.fit(x_vals, y_vals)

    #Get yprediction to plot the regression line along with price chart
    y_predictions = lasso.predict(x_vals)
    y_predictions_len = len(y_predictions)

    last_yp = y_predictions[y_predictions_len-1]
    print(last_yp)
    print(f'Last Lasso prediction for {tsymbol} is {last_yp}')

    #Get goodness-of-fit score
    fit_score = round(lasso.score(x_vals, y_vals), 3)

    #Log the score for debugging
    print(f'Lasso model fit_score for {tsymbol} is {fit_score}')

    #Flatten the predictions to keep it in same format as other chart data
    y_predictions = y_predictions.flatten()

    lasso_buy_rec = f'lasso_buy_rec:{lasso_buy_score}/{lasso_max_score}'
    lasso_sell_rec = f'lasso_sell_rec:{lasso_sell_score}/{lasso_max_score}'

    lasso_signals = f'Lasso: {lasso_buy_rec},{lasso_sell_rec},lasso_fit_score:{fit_score}'

    return y_predictions, lasso_buy_score, lasso_sell_score, lasso_max_score, lasso_signals
