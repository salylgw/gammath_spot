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

#Linear Dynamic Price Estimation and Projection

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import (TimeSeriesSplit, GridSearchCV)
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import (r2_score, make_scorer)
from matplotlib import pyplot as plt
from scipy.stats import spearmanr
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

class GPEP:
    def __init__(self):
        self.Tickers_dir = Path('tickers')

    def do_sgd_regression(self, prices, single):

        mtdpy, mtd5y = gut.get_min_trading_days()
        prices_len = len(prices)

        #Convert to numpy array
        y_vals = np.array(prices)
        x_vals = np.array([x for x in range(prices_len)])

        #High prices take too many iterations to converge.
        #For approximate estimates, I'm dividing and multiplying by a fsctor (before and after respectively) to get a ballpark figure in reasonable time
        mean_price_unit = ((prices.mean())/1000)
        if (mean_price_unit < 1):
            factor = 1
        elif (mean_price_unit < 10):
            factor = 10
        elif (mean_price_unit < 100):
            factor = 100
        elif (mean_price_unit < 1000):
            factor = 1000

        y_vals = (y_vals/factor)

        #Multiple samples for single feature
        y_vals = y_vals.reshape(-1, 1)
        y_vals = y_vals.flatten()
        x_vals = x_vals.reshape(-1, 1)

        #Construct a pipeline of sequential steps/transforms and estimator
        try:
            #Need to standardize the training data for SGD
            pline = make_pipeline(StandardScaler(), SGDRegressor(fit_intercept=True, shuffle=False, random_state=20, eta0=0.01, early_stopping=False, max_iter=1000000, n_iter_no_change=10))
        except:
            raise RuntimeError('SGD pipeline creation failed')

        #Number of splits for cross validation
        #Test size needs to be at least 2 since we want to use R2 scorer
        TS_SPLITS = mtdpy

        #Use time series split for cross validation
        tss = TimeSeriesSplit(n_splits=TS_SPLITS)

        #Use GridSearchCV to find best params
        param_grid  = {'sgdregressor__loss': ('squared_error', 'huber', 'epsilon_insensitive', 'squared_epsilon_insensitive'), 'sgdregressor__learning_rate': ('constant', 'optimal', 'invscaling', 'adaptive')}

        #Use R2 scorer
        scorer = make_scorer(r2_score)

        #Search for best params (We can use n_jobs=-1 to use all processors if we want to run it on individual stocks separately)
        if (single == True):
            n_jobs = -1
        else:
            n_jobs = None

        model = GridSearchCV(estimator=pline, param_grid=param_grid, scoring=scorer, cv=tss, n_jobs=n_jobs)
        model.fit(x_vals, y_vals)

        #Predict based on the selected model
        ypredict = model.predict(x_vals)

        #Check the R2 score
        score = model.score(x_vals, y_vals)

        #Flatten the predictions to keep it in same format as other chart data
        y_predictions = ypredict.flatten()
        yp_len = len(y_predictions)

        #Get a pandas series for drawing the chart
        #Leave room for projection (additional min 5 years length)
        ypp_len = (yp_len + mtd5y)
        y_predictions_series = pd.Series(np.nan, pd.RangeIndex(ypp_len))

        #First half with estimates. Next half with np.nan
        y_predictions_series[0:yp_len] = y_predictions

        #Create a pandas series for projection values.
        #First half with np.nan. Next half with projections
        y_projections_series = pd.Series(np.nan, pd.RangeIndex(ypp_len), name='PP')

        #I haven't seen a line extension function so just constructing a line for projection
        #y = mx + c

        #Calculate the slope
        m = (y_predictions[yp_len-1] - y_predictions[0])/(x_vals[yp_len-1] - x_vals[0])

        #Calculate the intercept
        c = y_predictions[0]

        #Calculate points for the projection line
        projection_len = ypp_len-yp_len
        for i in range(projection_len):
            y_projections_series[yp_len+i] = ((m*(yp_len+i)) + c) #y = mx + c

        y_predictions_series *= factor
        y_projections_series *= factor

        return y_predictions_series, y_projections_series


    def get_moving_price_estimated_projection(self, tsymbol):
        mtdpy, mtd5y = gut.get_min_trading_days()

        path = self.Tickers_dir / f'{tsymbol}'

        try:
            df = pd.read_csv(path / f'{tsymbol}_history.csv')
        except:
            #Not a fatal error. Just log it and return
            print(f'\nStock history file not found for {tsymbol}')
            return

        df_len = len(df)
        if (df_len < mtd5y):
            #Not a fatal error. Just log it and return
            print(f'\nInsufficent stock history length for {tsymbol}')
            return

        prices = df.Close

        y_predictions_series, y_projections_series = self.do_sgd_regression(prices, False)

        #Actual length of the estimates/prediction
        yp_len = (len(y_predictions_series) - mtd5y)

        #Save projections for later reference. We don't need non-projection np.nan
        y_projections_series[yp_len:].to_csv(path / f'{tsymbol}_pp.csv', index=False)

        #Draw the charts
        figure, axes = plt.subplots(nrows=1, figsize=(28, 47))

        logo_file_found = True

        try:
            #Get the path of program/package
            pgm_dir_path, fn = os.path.split(__file__)

            #Append the data dir
            pgm_data_path = os.path.join(pgm_dir_path, 'data')

            #Read the logo
            logo_data = plt.imread(f'{pgm_data_path}/logo.png')
        except:
            logo_file_found = False

        #Create dataframe for plotting
        lpe_df = pd.DataFrame({tsymbol: prices, 'Estimate': y_predictions_series, 'Projection': y_projections_series})

        #Plot the chart
        lpe_df.plot(lw=1, title='Price Estimate and Projection')

        if (logo_file_found):
            #Attach the logo to the figure
            plt.figimage(logo_data)


        #Save it for later reference
        #Use PDF instead of png to save space)
        plt.savefig(path / f'{tsymbol}_pep.pdf', format='pdf')

        try:
            sgd_ic = round(spearmanr(y_predictions_series[0:yp_len], prices).correlation, 3)
        except:
            sgd_ic = np.nan
            #Not a fatal error. Just log it
            print(f'Failed to compute Information Coefficient for {tsymbol} SGD')

        try:
            #Append the signals file
            f = open(path / f'{tsymbol}_signal.txt', 'a')
        except:
            print('\nERROR: opening signal file for ', tsymbol, ': ', sys.exc_info()[0])
        else:
            #Log 3 months, 1 year and 5 year projection for quick reference
            projection_string = f'Moving Price Projection (approx. 3m, 1y, 5yrs): {round(y_projections_series[yp_len+60], 3)}, {round(y_projections_series[yp_len+mtdpy], 3)}, {round(y_projections_series[yp_len+mtd5y-1], 3)}, sgd_ic:{sgd_ic}'
            f.write(projection_string)
            f.close()


    def sp500_pep(self):

        mtdpy, mtd5y = gut.get_min_trading_days()

        #SP500-specific files are in ticker dir
        path = self.Tickers_dir
        try:
            #SP500 closing data
            sp500_closing_data = pd.read_csv(path / 'SP500_history.csv')
        except:
            print('SP500 closing price data not found')
            return 0
        else:
            #Drop nans
            prices = sp500_closing_data.Close.dropna()

        #Get the prediction and projection series
        y_predictions_series, y_projections_series = self.do_sgd_regression(prices, True)

        #Actual length of the estimates/prediction
        yp_len = (len(y_predictions_series) - mtd5y)

        #Save projections for later reference. We don't need non-projection np.nan
        y_projections_series[yp_len:].to_csv(path / f'SP500_pp.csv', index=False)

        #Draw the charts
        figure, axes = plt.subplots(nrows=1, figsize=(28, 47))

        logo_file_found = True

        try:
            #Get the path of program/package
            pgm_dir_path, fn = os.path.split(__file__)

            #Append the data dir
            pgm_data_path = os.path.join(pgm_dir_path, 'data')

            #Read the logo
            logo_data = plt.imread(f'{pgm_data_path}/logo.png')
        except:
            logo_file_found = False

        #Create dataframe for plotting
        lpe_df = pd.DataFrame({'SP500': prices, 'Estimate': y_predictions_series, 'Projection': y_projections_series})

        #Plot the chart
        lpe_df.plot(lw=1, title='Price Estimate and Projection')

        if (logo_file_found):
            #Attach the logo to the image
            plt.figimage(logo_data)

        #Save it for later reference. Use PDF instead of png to save space
        plt.savefig(path / f'SP500_pep.pdf', format='pdf')
