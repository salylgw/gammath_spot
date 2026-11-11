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

#Use Principal Component Analysis to derive weighted micro-gScores for overall gScore

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
    tickers_dir = gut.get_tickers_dir()
    path = tickers_dir / f'{tsymbol}'
    try:
        df_micro_gscores_history = pd.read_csv(path / f'{tsymbol}_micro_gscores.csv', usecols=('Price', 'RSI', 'BBANDS', 'MACD', 'KF', 'OLS', 'MFI', 'Stoch', 'CECS', 'LSR'))
    except:
        print('\nERROR: Failed to open micro-gScores history for symbol ', tsymbol)
        return

    #Scale micro-gScores. Need to have mean at 0.0 for PCA
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_micro_gscores_history)

    #Use all component to extact explained varience ratio for each component
    pca = PCA(n_components=len(df_micro_gscores_history.columns))
    pca_data = pca.fit_transform(scaled_data)

    #Use variance ration for each component variance weights
    component_variance_weights = pca.explained_variance_ratio_
    component_loadings = pca.components_

    #Derive weighage for each component micro-gScore
    micro_gscore_weights = np.dot(component_variance_weights, component_loadings)

    #Derive Overall gScore using PCA-derive micro-gScore weights
    pca_derived_overall_gscores = np.dot(scaled_data, micro_gscore_weights)

    pd.DataFrame({'PCA_derived_gScore': pca_derived_overall_gscores}).to_csv(path / f'{tsymbol}_pcadgs.csv')
    return pca_derived_overall_gscores
