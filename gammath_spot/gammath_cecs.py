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

# Current env confidence score
# Use broad market fear gauge and individual stock change for the day
# to gauge confidence to buy
 
import pandas as pd
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

def get_current_env_confidence_score(df):
    #Default env confidence score same as broad fear gauge score
    current_env_confidence_score = gut.compute_broad_fg_gscore()

    price_changes = df['Close'].pct_change(fill_method=None)

    #Get mean percent change per day
    bp, mp, tp = price_changes.quantile([0.25, 0.50, 0.75])
    last_price_change = price_changes[len(price_changes)-1]

    # Price change and broad fear gauge are not in different direction.
    # Derive score based on price change percentiles
    if ((last_price_change * current_env_confidence_score) < 0):
        if (last_price_change <= bp):
            current_env_confidence_score = -1.0
        elif (last_price_change <= mp):
            current_env_confidence_score = -0.5
        elif (last_price_change >= tp):
            current_env_confidence_score = 1.0
        else:
            current_env_confidence_score = 0.5

    display_fraction = f'{round(current_env_confidence_score*10):d}/10'
    cecs_string = f'Current Environment Confidence Score: {display_fraction}'

    return current_env_confidence_score, cecs_string
