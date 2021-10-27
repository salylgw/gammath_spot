# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

NUM_TRADING_DAYS_PER_YEAR = 252

def get_ols_signals(tsymbol, df, path):

    print(f'\nGetting OLS signals for {tsymbol}')

    ols_buy_score = 0
    ols_sell_score = 0
    ols_max_score = 0
    ols_signals = ''
    fits_1y = False
    fits_5y = False

    prices_len = len(df.Close)
    lp = df.Close[prices_len-1]
    y_vals = np.array(df.Close)
    x_vals = np.array([x for x in range(prices_len)])

    #Multiple samples for single feature
    y_vals = y_vals.reshape(-1, 1)
    y_vals = y_vals.flatten()
    y_vals_len = len(y_vals)
    x_vals = x_vals.reshape(-1, 1)
    x_vals_len = len(x_vals)

    try:
        #Linear regression model (Ordinary Least Squares)
        #Fit the model for x and y values (5 years)
        ols = LinearRegression(fit_intercept=True, normalize=False).fit(x_vals, y_vals)

        #Get yprediction to plot the regression line along with price chart
        y_predictions = ols.predict(x_vals)
        #Flatten the predictions to keep it in same format as other chart data
        y_predictions = y_predictions.flatten()
        y_predictions_len = len(y_predictions)
        last_yp = y_predictions[y_predictions_len-1]

        #Get goodness-of-fit score
        fit_score = round(ols.score(x_vals, y_vals), 3)

        #Log the score for debugging
        print(f'ols model 5Y fit_score for {tsymbol} is {fit_score}')

        #Model last 1 year data
        index_1y = NUM_TRADING_DAYS_PER_YEAR
        y1_vals = y_vals[(y_vals_len-index_1y):]
        x1_vals = x_vals[(x_vals_len-index_1y):]

        #Fit the model for x and y values (1 year)
        ols_1y = LinearRegression(fit_intercept=True, normalize=False).fit(x1_vals, y1_vals)

        #Get yprediction to plot the regression line along with price chart
        y1_predictions = ols_1y.predict(x1_vals)

        #Flatten the predictions to keep it in same format as other chart data
        y1_predictions = y1_predictions.flatten()
        y1_predictions_len = len(y1_predictions)
        last_y1p = y1_predictions[y1_predictions_len-1]

        #Get goodness-of-fit score
        fit_1y_score = round(ols_1y.score(x1_vals, y1_vals), 3)

        #Log the score for debugging
        print(f'ols model 1Y fit_score for {tsymbol} is {fit_1y_score}')

        #Best score is 1; Using 0.9-1.0 as good fit (5y or 1y)
        fits_1y = ((fit_1y_score <= 1) and (fit_1y_score >= 0.9))
        fits_5y = ((fit_score <= 1) and (fit_score >= 0.9))

        #Slope of 1Y OLS line (just need to do y2-y1 to get the direction)
        slope_dir_1y = (y1_predictions[y1_predictions_len-1] - y1_predictions[0])
        print(f'LR 1Y OLS  line slope for {tsymbol} is {slope_dir_1y}')

        #Slope of OLS line
        slope_dir_5y = (y_predictions[y_predictions_len-1] - y_predictions[0])
        print(f'LR 5Y OLS  line slope for {tsymbol} is {slope_dir_5y}')

        #pd dataframe for 1Y predictions. Will need all elements in same size so need to fill in nan elsewhere
        y1_series = pd.Series(np.nan, pd.RangeIndex(prices_len))

        #Put the 1y predictions in right place
        y1_series[len(y1_series)-y1_predictions_len:] = y1_predictions

    except:
        print(f'\nERROR: Linear Regression failed for {tsymbol} while generating OLS signals')
        return

    ols_buy_rec = f'ols_buy_rec:{ols_buy_score}/{ols_max_score}'
    ols_sell_rec = f'ols_sell_rec:{ols_sell_score}/{ols_max_score}'

    if (fits_5y):
        ols_signals = f'OLS: {ols_buy_rec},{ols_sell_rec},ols_1y_fit_score:{fit_1y_score},ols_fit_score:{fit_score}'
    else:
        ols_signals = f'OLS: {ols_buy_rec},{ols_sell_rec},ols_1y_fit_score:{fit_1y_score},ols_fit_score:{fit_score}'

    return y1_series, y_predictions, ols_buy_score, ols_sell_score, ols_max_score, ols_signals
