# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2022, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021-2022, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression

#This is a WIP. Just getting APIs to work. Lot will change in this file before it gets integrated into scoring

#from scipy.special import expit
#    1 / (1 + np.exp(-val))
#    return expit(vals)

#Temp sigmoid for experimentation
def price_sigmoid(prices):

    prices_len = len(prices)

    #Zero-initialize the sigmoid
    prices_sigmoid = pd.Series(0, pd.RangeIndex(prices_len))

    #First element of sigmoid is set to 0; next ascending val then 1 else 0
    for i in range(prices_len-1):
        if (prices[i] < prices[i+1]):
            prices_sigmoid[i+1] = 1
        else:
            prices_sigmoid[i+1] = 0


    return (prices_sigmoid)

#WIP: This is just to get Logistic regression API to work. Algorithm will be updated later
def get_lgstic_signals(tsymbol, df, path):
    lgstic_signals = ''

    prices_len = len(df.Close)
    lp = df.Close[prices_len-1]
    prices = df.Close
    sigmoid_vals = price_sigmoid(prices)

    y_vals = np.array(sigmoid_vals)
    x_vals = np.array([x for x in range(prices_len)])

    #Multiple samples for single feature
    y_vals = y_vals.reshape(-1, 1)
    x_vals = x_vals.reshape(-1, 1)
    y_vals = np.ravel(y_vals)

    #Logistic regression model
    #WIP: experimenting with the API
    lrm = LogisticRegression(fit_intercept=True, random_state=20, solver='liblinear', max_iter=1000, multi_class='auto').fit(x_vals, y_vals)

    #Get yprediction
    y_predictions = lrm.predict(x_vals)
    y_predictions_len = len(y_predictions)

    last_yp = y_predictions[y_predictions_len-1]

    #Get y probability estimates
    y_proba = lrm.predict_proba(x_vals)
    y_proba_len = len(y_proba)

    last_yproba = y_proba[y_proba_len-1]

    #Get goodness-of-fit score
    fit_score = round(lrm.score(x_vals, y_vals), 3)

    lgstic_signals = f'Logistic: lgstic_fit_score:{fit_score},probab_pred:{last_yproba} for labels:{lrm.classes_}'

    return lgstic_signals
