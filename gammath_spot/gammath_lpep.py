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

#This is a Work-In-Progress. Please do not use

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import (TimeSeriesSplit, GridSearchCV)
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import (r2_score, make_scorer)

def get_moving_price_estimate(tsymbol, prices):

    prices_len = len(prices)

    #Convert to numpy array
    y_vals = np.array(prices)
    x_vals = np.array([x for x in range(prices_len)])

    #Multiple samples for single feature
    y_vals = y_vals.reshape(-1, 1)
    y_vals = y_vals.flatten()
    x_vals = x_vals.reshape(-1, 1)

    #Construct a pipeline of sequential steps/transforms and estimator
    try:
        #Need to standardize the training data for SGD
        pline = make_pipeline(StandardScaler(), SGDRegressor(fit_intercept=True, shuffle=False, random_state=20, eta0=0.01, early_stopping=False, n_iter_no_change=10))
    except:
        raise RuntimeError('SGD pipeline creation failed')

    #Number of splits for cross validation
    #Test size needs to be at least 2 since we want to use R2 scorer
    TS_SPLITS = 249

    #Use time series split for cross validation
    tss = TimeSeriesSplit(n_splits=TS_SPLITS)

    #Use GridSearchCV to find best params
    param_grid  = {'sgdregressor__loss': ('squared_error', 'huber', 'epsilon_insensitive', 'squared_epsilon_insensitive'), 'sgdregressor__learning_rate': ('constant', 'optimal', 'invscaling', 'adaptive'), 'sgdregressor__max_iter': (100000, 1000000)}

    #Use R2 scorer
    scorer = make_scorer(r2_score)

    #Search for best params
    model = GridSearchCV(estimator=pline, param_grid=param_grid, scoring=scorer, cv=tss)
    model.fit(x_vals, y_vals)

    #Predict based on the selected model
    ypredict = model.predict(x_vals)

    #Check the R2 score
    score = model.score(x_vals, y_vals)
