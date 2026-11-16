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
from scipy.optimize import linear_sum_assignment
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

def get_pca_derived_gscores(df_micro_gscores_history):
    mtdpy, _ = gut.get_min_trading_days()

    micro_gscore_data = df_micro_gscores_history.values
    time_steps, num_dimensions = micro_gscore_data.shape

    pca_derived_overall_gscores = np.full(time_steps, np.nan)
    prev_components = None

    max_abs_pca_derived_gscore_so_far = 0.0

    for time_step in range(mtdpy, time_steps):
        #Obtain data upto time_step [must not lookahead]
        micro_gscore_data_so_far = micro_gscore_data[:time_step]

        #Scale micro-gScores. Need to have mean at 0.0 for PCA
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(micro_gscore_data_so_far)

        #Use all component to extact explained varience ratio for each component
        pca = PCA(n_components=num_dimensions)
        #PCA on standardized data is equivalent of eigenvalue decomposition of correlation matrix
        pca.fit(scaled_data)

        #Use variance ratio for each component variance weights
        component_variance_weights = pca.explained_variance_ratio_.copy()
        component_loadings = pca.components_.copy()

        #Inter-window sign consistency
        if prev_components is not None:
            #Need to match new component to previous most similar component
            similarity = np.abs(component_loadings @ prev_components.T)
            rows, columns = linear_sum_assignment(-similarity)
            order = np.empty_like(rows)
            order[columns] = rows

            #Reorder variance weights together with loadings
            component_loadings = component_loadings[order]
            component_variance_weights = component_variance_weights[order]
            #Need to align signs with matched previous components
            signs = np.sign(np.sum(component_loadings * prev_components, axis=1))
            signs[signs == 0] = 1
            component_loadings = component_loadings * signs[:, None]


        prev_components = component_loadings.copy()

        #Derive weightage for each standardized component micro-gScore
        micro_gscore_weights = np.dot(component_variance_weights, component_loadings)
        #convert to weights on uncentered micro-gScores
        weights = micro_gscore_weights / scaler.scale_

        #Make weight size comparable across steps
        weight_size = np.abs(weights).sum()
        if (weight_size > 0):
            weights = weights / weight_size

        #Current time_step score
        current_pca_derived_overall_gscore = (micro_gscore_data[time_step] - scaler.mean_) @ weights
        max_abs_pca_derived_gscore_so_far = max(max_abs_pca_derived_gscore_so_far, abs(current_pca_derived_overall_gscore))

        #Normalize PCA derived overall gscore (Maintain original scale of -1 to +1)
        if (max_abs_pca_derived_gscore_so_far > 0):
            pca_derived_overall_gscores[time_step] = current_pca_derived_overall_gscore/max_abs_pca_derived_gscore_so_far
        else:
            pca_derived_overall_gscores[time_step] = 0.0


    return pd.DataFrame({'Variance_ratio_weighted_gScores': pca_derived_overall_gscores}, index=range(len(pca_derived_overall_gscores)))
