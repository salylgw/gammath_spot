# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works
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
__copyright__ = 'Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import roc_auc_score

#Get UP/DOWN probabilities for next week and month
def get_lgstic_signals(tsymbol, df, path):

    lgstic_signals = ''

    prices_len = len(df.Close)
    lp = df.Close[prices_len-1]
    prices = df.Close

    #Get price sigmoid (approx. 1-week interval)
    sigmoid_vals_5d = gut.get_price_sigmoid(prices, 5)

    y_vals_5d = np.array(sigmoid_vals_5d)
    x_vals_5d = np.array([x for x in range(len(y_vals_5d))])

    #Multiple samples for single feature
    y_vals_5d = y_vals_5d.reshape(-1, 1)
    x_vals_5d = x_vals_5d.reshape(-1, 1)
    y_vals_5d = np.ravel(y_vals_5d)

    #Regularization params to pick from based on cross-validation
    reg_params = np.logspace(-4, 4, 8)

    #Logistic regression model with cross validation
    lrm = LogisticRegressionCV(Cs=reg_params, fit_intercept=True, random_state=20, solver='liblinear', max_iter=10000, multi_class='ovr').fit(x_vals_5d, y_vals_5d)

    #Get y probability estimates
    y_5d_proba = lrm.predict_proba(x_vals_5d)
    y_5d_proba_len = len(y_5d_proba)

    #Get ROC area under curve for debug purposes
    auc_5d = roc_auc_score(y_vals_5d, y_5d_proba[:, 1])
    last_5d_yproba = y_5d_proba[y_5d_proba_len-1]

    #Save "after 5 days" up probability for micro-gScore dataframe
    a5dup = round(last_5d_yproba[1], 3)

    #Get accuracy score (using default scoring "accuracy score" for classification)
    accuracy_score_5d = round(lrm.score(x_vals_5d, y_vals_5d), 3)

    #Get price sigmoid (approx. 1-month interval)
    sigmoid_vals_20d = gut.get_price_sigmoid(prices, 20)

    y_vals_20d = np.array(sigmoid_vals_20d)
    x_vals_20d = np.array([x for x in range(len(y_vals_20d))])

    #Multiple samples for single feature
    y_vals_20d = y_vals_20d.reshape(-1, 1)
    x_vals_20d = x_vals_20d.reshape(-1, 1)
    y_vals_20d = np.ravel(y_vals_20d)

    #Logistic regression model
    lrm = LogisticRegressionCV(Cs=reg_params, fit_intercept=True, random_state=20, solver='liblinear', max_iter=10000, multi_class='ovr').fit(x_vals_20d, y_vals_20d)

    #Get y probability estimates
    y_20d_proba = lrm.predict_proba(x_vals_20d)
    y_20d_proba_len = len(y_20d_proba)

    #Get ROC area under curve for debug purposes
    auc_20d = roc_auc_score(y_vals_20d, y_20d_proba[:, 1])
    last_20d_yproba = y_20d_proba[y_20d_proba_len-1]

    #Save "after 20 days" up probability for micro-gScore dataframe
    a20dup = round(last_20d_yproba[1], 3)

    #Get accuracy score (using default scoring "accuracy score" for classification)
    accuracy_score_20d = round(lrm.score(x_vals_20d, y_vals_20d), 3)

    #Log output for quick reference
    lgstic_signals = f'Probability after approx. a week: UP:{a5dup}, DOWN: {round((1-a5dup), 3)},accu_score:{accuracy_score_5d}\nProbability after approx. a month: UP:{a20dup}, DOWN: {round((1-a20dup), 3)},accu_score:{accuracy_score_20d}'

    return a5dup, a20dup, lgstic_signals
