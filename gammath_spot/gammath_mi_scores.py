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

# Get mutual information score

import pandas as pd
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut
from sklearn.feature_selection import (mutual_info_regression, mutual_info_classif)

def get_mi_scores(features, target_variable, type):

    if (len(features) <= 0):
        raise ValueError('Invalid features data')

    #Check if it is for regression or classification
    if (type == 'regression'):
        mi = mutual_info_regression(features, target_variable)
        mi_pd_series = pd.Series(mi, index=features.columns)
    elif (type == 'classification'):
        #Get price sigmoid (1-day interval)
        ps = gut.get_price_sigmoid(target_variable, 1)

        mi = mutual_info_classif(features, ps)
        mi_pd_series = pd.Series(mi, index=features.columns)
    else:
        raise ValueError('Invalid type')

    return mi_pd_series
