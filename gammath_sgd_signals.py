# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler

def get_sgd_signals(tsymbol, df):

    sgd_buy_score = 0
    sgd_sell_score = 0
    sgd_max_score = 0
    sgd_signals = ''

    prices_len = len(df.Close)
    lp = df.Close[prices_len-1]
    y_vals = np.array(df.Close)
    x_vals = np.array([x for x in range(prices_len)])

    #Multiple samples for single feature
    y_vals = y_vals.reshape(-1, 1)
    y_vals = y_vals.flatten()
    x_vals = x_vals.reshape(-1, 1)

    #Need to standardize the training data for SGD
    scaler = StandardScaler()
    scaler.fit(x_vals)
    x_vals = scaler.fit_transform(x_vals)

    #Stochastic Gradient Descent model;
    # WIP: experimenting; Using squared_loss loss function for now (not much different from OLS)
    #Need to permute the data after each iteration so using shuffle=True
    #Using default for max_iter (which is 1000)
    sgd = SGDRegressor(loss="squared_loss", fit_intercept=True, shuffle=True, epsilon=0.1, learning_rate='optimal', eta0=0.01, power_t=0.25, early_stopping=False, n_iter_no_change=10)

    #Fit the model for x and y values
    sgd.fit(x_vals, y_vals)

    #Get yprediction to plot the regression line along with price chart
    y_predictions = sgd.predict(x_vals)
    y_predictions_len = len(y_predictions)

    last_yp = y_predictions[y_predictions_len-1]
    print(last_yp)
    print(f'Last SGD prediction for {tsymbol} is {last_yp}')

    #Get goodness-of-fit score
    fit_score = round(sgd.score(x_vals, y_vals), 3)

    #Log the score for debugging
    print(f'SGD model fit_score for {tsymbol} is {fit_score}')

    #Flatten the predictions to keep it in same format as other chart data
    y_predictions = y_predictions.flatten()

    sgd_buy_rec = f'sgd_buy_rec:{sgd_buy_score}/{sgd_max_score}'
    sgd_sell_rec = f'sgd_sell_rec:{sgd_sell_score}/{sgd_max_score}'

    sgd_signals = f'SGD: {sgd_buy_rec},{sgd_sell_rec},sgd_fit_score:{fit_score}'

    return y_predictions, sgd_buy_score, sgd_sell_score, sgd_max_score, sgd_signals
