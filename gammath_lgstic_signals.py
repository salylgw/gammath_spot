# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np
#from scipy.special import expit
from sklearn.linear_model import LogisticRegression

#Temp sigmoid for experimentation as expit isn't useful
def price_sigmoid(prices):
#    1 / (1 + np.exp(-val))
#    return expit(vals)
    prices_len = len(prices)

    #Zero-initialize the sigmoid
    prices_sigmoid = pd.Series(0, pd.RangeIndex(prices_len))

#    max_price = prices.max()
#    mean_price = prices.mean()
#    for i in range(prices_len):
#        prices_sigmoid[i] = prices[i]/max_price
#        if (prices[i] < mean_price):
#            prices_sigmoid[i] = 0
#        else:
#            prices_sigmoid[i] = 1

    #First element of sigmoid is set to 0; next ascending val then 1 else 0
    for i in range(prices_len-1):
        if (prices[i] < prices[i+1]):
            prices_sigmoid[i+1] = 1
        else:
            prices_sigmoid[i+1] = 0


    return (prices_sigmoid)

#WIP: Just getting APIs to work... lot more needs to be done
def get_lgstic_signals(tsymbol, df, path):
    lgstic_buy_score = 0
    lgstic_sell_score = 0
    lgstic_max_score = 0
    lgstic_signals = ''

    prices_len = len(df.Close)
    lp = df.Close[prices_len-1]
    prices = df.Close
    sigmoid_vals = price_sigmoid(prices)

#    df_sigmoids = pd.read_csv(path / f'{tsymbol}_bbp_sigmoid.csv')
#    sigmoid_vals = df_sigmoids['Sigmoid']

    y_vals = np.array(sigmoid_vals)
    x_vals = np.array([x for x in range(prices_len)])

    #Multiple samples for single feature
    y_vals = y_vals.reshape(-1, 1)
    x_vals = x_vals.reshape(-1, 1)
    y_vals = np.ravel(y_vals)

    #Logistic regression model
    #WIP: experimenting
    lrm = LogisticRegression(fit_intercept=True, random_state=20, solver='liblinear', max_iter=1000, multi_class='auto').fit(x_vals, y_vals)

    #Get yprediction
    y_predictions = lrm.predict(x_vals)
    y_predictions_len = len(y_predictions)

    last_yp = y_predictions[y_predictions_len-1]
    print(f'Last Logistic regression prediction for {tsymbol} is {last_yp}')

    #Get y probability estimates
    y_proba = lrm.predict_proba(x_vals)
    y_proba_len = len(y_proba)

    last_yproba = y_proba[y_proba_len-1]
    print(f'Last Logistic regression probability prediction for {tsymbol} is {last_yproba}, corresponding to labels {lrm.classes_}')

    #Get goodness-of-fit score
    fit_score = round(lrm.score(x_vals, y_vals), 3)

    #Log the score for debugging
    print(f'Logistic regression model fit_score for {tsymbol} is {fit_score}')

    #Flatten the predictions to keep it in same format as other chart data
    y_predictions = y_predictions.flatten()

    lgstic_buy_rec = f'lgstic_buy_rec:{lgstic_buy_score}/{lgstic_max_score}'
    lgstic_sell_rec = f'lgstic_sell_rec:{lgstic_sell_score}/{lgstic_max_score}'

    lgstic_signals = f'Logistic: {lgstic_buy_rec},{lgstic_sell_rec},lgstic_fit_score:{fit_score}'

    return y_predictions, lgstic_buy_score, lgstic_sell_score, lgstic_max_score, lgstic_signals
