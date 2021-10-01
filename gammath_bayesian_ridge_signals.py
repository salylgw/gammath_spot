# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np
from sklearn.linear_model import BayesianRidge

def get_bridge_signals(tsymbol, df):

    bayesian_ridge_buy_score = 0
    bayesian_ridge_sell_score = 0
    bayesian_ridge_max_score = 0
    bayesian_ridge_signals = ''

    prices_len = len(df.Close)
    lp = df.Close[prices_len-1]
    y_vals = np.array(df.Close)
    x_vals = np.array([x for x in range(prices_len)])

    #Multiple samples for single feature
    y_vals = y_vals.reshape(-1, 1)
    y_vals = y_vals.flatten()
    x_vals = x_vals.reshape(-1, 1)

    #Bayesian Ridge regression model
    #WIP: experimenting with default params
    bayesian_ridge = BayesianRidge()

    #Fit the model for x and y values
    bayesian_ridge.fit(x_vals, y_vals)

    #Get yprediction to plot the OLS line along with price chart
    y_predictions = bayesian_ridge.predict(x_vals)
    y_predictions_len = len(y_predictions)

    last_yp = y_predictions[y_predictions_len-1]
    print(last_yp)
    print(f'Last Bayesian Ridge prediction for {tsymbol} is {last_yp}')

    #Get goodness-of-fit score
    fit_score = round(bayesian_ridge.score(x_vals, y_vals), 3)

    #Log the score for debugging
    print(f'Bayesian Ridge model fit_score for {tsymbol} is {fit_score}')

    #Flatten the predictions to keep it in same format as other chart data
    y_predictions = y_predictions.flatten()

    bayesian_ridge_buy_rec = f'bayesian_ridge_buy_rec:{bayesian_ridge_buy_score}/{bayesian_ridge_max_score}'
    bayesian_ridge_sell_rec = f'bayesian_ridge_sell_rec:{bayesian_ridge_sell_score}/{bayesian_ridge_max_score}'

    bayesian_ridge_signals = f'Bayesian Ridge: {bayesian_ridge_buy_rec},{bayesian_ridge_sell_rec},bayesian_ridge_fit_score:{fit_score}'

    return y_predictions, bayesian_ridge_buy_score, bayesian_ridge_sell_score, bayesian_ridge_max_score, bayesian_ridge_signals
