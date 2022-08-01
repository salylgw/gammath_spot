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

# Moving Technical 5Y Price Conjecture
# Prediction doesn't make sense without the accurate information on how the business is actually
# doing. In the absence of that, I'm approximating based on past performance and adapting to changes
# dynamically. Hence, I think of this as dynamic/moving price conjecture

import pandas as pd

def get_moving_technical_price_conjecture(df):

    MIN_TRADING_DAYS_FOR_5_YEARS = 249*5
    prices = df.Close
    prices_len = len(prices)
    last_price = prices[prices_len-1]

    #Get percent change per day for MIN_TRADING_DAYS_FOR_5_YEARS and get a mean of it
    mean_pct_change_per_day = prices[prices_len-MIN_TRADING_DAYS_FOR_5_YEARS:].pct_change().mean()

    #Calculated conjecture of price after approximately 5 years from last price based on average percentage change per day from approximately last 5 years
    moving_technical_conjecture_price_in_5y = round((last_price + (last_price*mean_pct_change_per_day*MIN_TRADING_DAYS_FOR_5_YEARS)), 3) #round it off to take less space in text file

    mtcp = f'Moving Technical Conjecture Of Price In 5Y: {moving_technical_conjecture_price_in_5y}'

    return moving_technical_conjecture_price_in_5y, mtcp
