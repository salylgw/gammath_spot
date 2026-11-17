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

#This is a work-in-progress and has some TBDs (e.g. integrate into RL).
#Do not use yet

#Use Principal Component Analysis to derive weights for micro-gScores and calculate overall gScore
#The weight is derived based on how strongly each micro-gScore moves together with other micro-gScores
#AND
#The weight is derived based on how stable is a micro-gScore
#Following code is simplified as weight is derived from summing, overall components so order doesn't matter
#Variance ratios stay paired with own loadings as that is guaranteed by PCA

from pathlib import Path
import pandas as pd
import numpy as np
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

    max_abs_pca_derived_gscore_so_far = 0.0

    #Reference direction [based on micro-gScores where 1 means discounted and -1 means premium]
    reference = np.ones(num_dimensions)

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
        component_variance_weights = pca.explained_variance_ratio_
        component_loadings = pca.components_

        #How much each component points along the reference direction
        #Cancel out orientation
        alignment = component_loadings @ reference

        #Derive weightage for each standardized micro-gScore
        micro_gscore_weights = ((component_variance_weights * alignment) @ component_loadings)
        #convert to weights on uncentered micro-gScores
        weights = micro_gscore_weights / scaler.scale_

        #Make weight size comparable across steps
        weight_size = np.abs(weights).sum()
        if (weight_size > 0):
            weights = weights / weight_size

        #Current time_step score; 0 is not centered in micro gScores so no centering
        current_pca_derived_overall_gscore = (micro_gscore_data[time_step] @ weights)
        max_abs_pca_derived_gscore_so_far = max(max_abs_pca_derived_gscore_so_far, abs(current_pca_derived_overall_gscore))

        #Normalize PCA derived overall gscore (Maintain original scale of -1 to +1)
        if (max_abs_pca_derived_gscore_so_far > 0):
            pca_derived_overall_gscores[time_step] = current_pca_derived_overall_gscore/max_abs_pca_derived_gscore_so_far
        else:
            pca_derived_overall_gscores[time_step] = 0.0


    return pd.DataFrame({'Weighted_gScores': pca_derived_overall_gscores}, index=range(len(pca_derived_overall_gscores)))
