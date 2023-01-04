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

# Get mutual information score for micro-gScores

import pandas as pd
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut
from sklearn.feature_selection import (mutual_info_regression, mutual_info_classif)

def get_mi_scores(gscores):

    if (len(gscores) <= 0):
        raise ValueError('Invalid micro gscores data')

    #micro-gscore MI for price correlation
    mi = mutual_info_regression(gscores.drop(['Date', 'Close'], axis=1), gscores.Close)
    mi_scores_regr = pd.Series(mi, index=gscores.columns.drop(['Date', 'Close']))

    #Get price sigmoid (1-day interval)
    ps = gut.get_price_sigmoid(gscores.Close, 1)

    #micro-gscore MI for direction correlation
    mi = mutual_info_classif(gscores.drop(['Date', 'Close'], axis=1), ps)
    mi_scores_classif = pd.Series(mi, index=gscores.columns.drop(['Date', 'Close']))

    return mi_scores_regr, mi_scores_classif
