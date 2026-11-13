# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-Present, Salyl Bhagwat, Gammath Works
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
__copyright__ = 'Copyright (c) 2021-Present, Salyl Bhagwat, Gammath Works'

#This is a work-in-progress and has lot of TBDs (e.g. lookback window, invoked in historian v/s backtester, integrated into RL etc.).
#Do not use yet
#Use Principal Component Analysis to derive variance-ratio-weighted micro-gScores for overall gScore calculation

from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

def get_pca_derived_gscores(tsymbol):
    mtdpy, _ = gut.get_min_trading_days()

    tickers_dir = gut.get_tickers_dir()
    path = tickers_dir / f'{tsymbol}'
    try:
        df_micro_gscores_history = pd.read_csv(path / f'{tsymbol}_micro_gscores.csv', usecols=('Price', 'RSI', 'BBANDS', 'MACD', 'KF', 'OLS', 'MFI', 'Stoch', 'CECS', 'LSR'))
    except:
        print('\nERROR: Failed to open micro-gScores history for symbol ', tsymbol)
        return

    micro_gscore_data = df_micro_gscores_history.values
    time_steps, num_dimensions = micro_gscore_data.shape

    pca_derived_overall_gscores = []
    prev_components = None

    for time_step in range(mtdpy, time_steps):
        #Obtain data upto time_step [must not lookahead]
        micro_gscore_data_so_far = micro_gscore_data[:time_step]

        #Scale micro-gScores. Need to have mean at 0.0 for PCA
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(micro_gscore_data_so_far)

        #Use all component to extact explained varience ratio for each component
        pca = PCA(n_components=num_dimensions)
        #Data is already identical to Pearson correlation matrix of input data
        pca.fit(scaled_data)

        #Use variance ration for each component variance weights
        component_variance_weights = pca.explained_variance_ratio_
        component_loadings = pca.components_

        #Intra-window sign consistency
        if prev_components is not None:
            for i in range(len(component_loadings)):
                if np.dot(component_loadings[i], prev_components[i]) < 0:
                    component_loadings[i] *= -1

        prev_components = component_loadings.copy()

        #Derive weighage for each component micro-gScore
        micro_gscore_weights = np.dot(component_variance_weights, component_loadings)

        #Current time_step score
        current_scaled_data = scaler.transform(micro_gscore_data[time_step].reshape(1, -1))
        current_pca_derived_overall_gscore = np.dot(current_scaled_data, micro_gscore_weights)[0]
        pca_derived_overall_gscores.append(current_pca_derived_overall_gscore)


    pca_derived_overall_gscores = np.array(pca_derived_overall_gscores)
    #Maintain original scale of -1 to +1
    pca_derived_overall_gscores /= np.max(np.abs(pca_derived_overall_gscores))
    pca_derived_overall_gscores = np.round(pca_derived_overall_gscores, decimals=3)

    #Fill initial MTDPY with nan
    overall_gscores = np.full(time_steps, np.nan)
    overall_gscores[mtdpy:] = pca_derived_overall_gscores
    pd.DataFrame({'PCA_derived_gScore': overall_gscores}, index=df_micro_gscores_history.index).to_csv(path / f'{tsymbol}_pcadgs.csv')

    return overall_gscores
