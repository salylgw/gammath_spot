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

#TBD. Moving Technical Price Estimate is WIP (Work-In-Progress) and untested. Please do NOT use

import pandas as pd
import numpy as np

def get_moving_technical_price_estimate(df):

    MIN_TRADING_DAYS_FOR_5_YEARS = 249*5
    prices = df.Close
    prices_len = len(prices)
    mean_pct_change_per_day = prices[prices_len-MIN_TRADING_DAYS_FOR_5_YEARS:].pct_change().mean()

    moving_technical_estimated_price_in_5y = (prices[prices_len-1]*mean_pct_change_per_day*MIN_TRADING_DAYS_FOR_5_YEARS)

    mtep = f'Moving Technical Estimated Price In 5Y: {moving_technical_estimated_price_in_5y}'

    return mtep
