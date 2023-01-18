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

import pandas as pd
import numpy as np
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut


def get_price_signals(tsymbol, df):
    mtdpy, mtd5y = gut.get_min_trading_days()

    PRICE_PERCENT_CUTOFF = 85

    price_gscore = 0
    price_max_score = 0
    price_signals = ''
    curr_count_quantile_str = ''
    curr_price_1y_quantile_str = ''

    prices = df.Close
    prices_len = len(prices)
    if (prices_len <= 0):
        raise ValueError('Invalid Price data for generating signals')

    lp = prices[prices_len-1]

    #Limit to 3 digits after decimal point
    curr_price = f'curr_price: %5.3f' % lp

    nftwlh = ''

    #Get consecutive falling and rising days count
    last_falling_days_count = 0
    max_falling_days_count = 0
    last_rising_days_count = 0
    max_rising_days_count = 0

    price_consec_falling_days_count_series = pd.Series(np.nan, pd.RangeIndex(prices_len))
    price_consec_falling_days_count_index = 0

    price_consec_rising_days_count_series = pd.Series(np.nan, pd.RangeIndex(prices_len))
    price_consec_rising_days_count_index = 0

    for i in range(prices_len-1):
        if (prices[i] > prices[i+1]):
            last_falling_days_count += 1

            if (last_rising_days_count > 0):
                price_consec_rising_days_count_index += 1

            last_rising_days_count = 0

            price_consec_falling_days_count_series[price_consec_falling_days_count_index] = last_falling_days_count

            if (last_falling_days_count > max_falling_days_count):
                max_falling_days_count = last_falling_days_count
        elif (prices[i] < prices[i+1]):
            last_rising_days_count += 1

            if (last_falling_days_count > 0):
                price_consec_falling_days_count_index += 1

            last_falling_days_count = 0

            price_consec_rising_days_count_series[price_consec_rising_days_count_index] = last_rising_days_count

            if (last_rising_days_count > max_rising_days_count):
                max_rising_days_count = last_rising_days_count
        else:
            last_falling_days_count = 0
            last_rising_days_count = 0

    price_consec_falling_days_count_series = price_consec_falling_days_count_series.dropna()

    #Lower counts will be too many so drop them to get approx percentile past lower numbers
    price_consec_falling_days_count_series = price_consec_falling_days_count_series.drop_duplicates()
    price_consec_falling_days_count_series = price_consec_falling_days_count_series.sort_values()

    price_consec_rising_days_count_series = price_consec_rising_days_count_series.dropna()

    #Lower counts will be too many so drop them to get approx percentile past lower numbers
    price_consec_rising_days_count_series = price_consec_rising_days_count_series.drop_duplicates()
    price_consec_rising_days_count_series = price_consec_rising_days_count_series.sort_values()

    try:
        #50-day average
        fiftyDayAverage = df.Close[prices_len-1-50:].mean()
    except:
        fiftyDayAverage = 0

    try:
        #200-day average
        twoHundredDayAverage = df.Close[prices_len-1-200:].mean()
    except:
        twoHundredDayAverage = 0

    try:
        #52-week low
        yearly_lowest_val = df.Low[prices_len-1-mtdpy:].min()
    except:
        yearly_lowest_val = 0

    try:
        #52-week high
        yearly_highest_val = df.High[prices_len-1-mtdpy:].max()
    except:
        yearly_highest_val = 0

    if (yearly_lowest_val > 0):
        if (lp <= yearly_lowest_val):
            #New 52-week low; Log it for information
            nftwlh = 'new fiftyTwoWeekLow'

    if (yearly_highest_val <= 0):
        #New 52-week high; Log it for information
        nftwlh = 'new fiftyTwoWeekHigh'

    if (last_falling_days_count > 0):
        price_dir = 'falling'
        #Get percentile values
        bp, mp, tp = price_consec_falling_days_count_series.quantile([0.25, 0.5, 0.75])

        #Log quantile for days count
        if (last_falling_days_count < mp):
            curr_count_quantile_str = 'day-count in bottom quantile'
        elif (last_falling_days_count < tp):
            curr_count_quantile_str = 'day-count in middle quantile'
        else:
            curr_count_quantile_str = 'day-count in top quantile'

        price_gscore -= 1

        if (last_falling_days_count >= bp):
            price_gscore -= 2

        #Checkout price wrt 50-day average, 200-day average and 52-week low
        if (fiftyDayAverage > 0):
            if (lp > fiftyDayAverage):
                price_gscore -= 1

        if (twoHundredDayAverage > 0):
            if (lp > twoHundredDayAverage):
                price_gscore -= 1

        if (yearly_highest_val > 0):
            pct_val = lp*100/yearly_highest_val

            #If we are closer to 52-week high then indicate premium; else indicate the discount score
            if (pct_val >= PRICE_PERCENT_CUTOFF):
                price_gscore -= 3

    elif (last_rising_days_count > 0):
        price_dir = 'rising'
        bp, mp, tp = price_consec_rising_days_count_series.quantile([0.25, 0.5, 0.75])

        #Log quantile for days count
        if (last_rising_days_count < mp):
            curr_count_quantile_str = 'day-count in bottom quantile'
        elif (last_rising_days_count < tp):
            curr_count_quantile_str = 'day-count in middle quantile'
        else:
            curr_count_quantile_str = 'day-count in top quantile'

        price_gscore += 1
        if (last_rising_days_count <= bp):
            price_gscore += 2

        #Checkout price wrt 50-day average, 200-day average and 52-week low
        if (fiftyDayAverage > 0):
            if (lp <= fiftyDayAverage):
                price_gscore += 1

        if (twoHundredDayAverage > 0):
            if (lp <= twoHundredDayAverage):
                price_gscore += 1

        if (yearly_lowest_val > 0):
            pct_val = yearly_lowest_val*100/lp

            #If current price is not too far from 52-week low then increase discount score
            if (pct_val >= PRICE_PERCENT_CUTOFF):
                price_gscore += 3
    else:
        price_dir = 'unclear'

    price_max_score += 8

    #Get current price percentiles for most recent 52-week range
    one_year_prices = df['Close'][(prices_len-mtdpy):]
    bp, mp, tp = one_year_prices.quantile([0.25, 0.5, 0.75])

    #Log quantile for current price in 52-week range
    if (lp < mp):
        curr_price_1y_quantile_str = 'in 1Y bottom quantile'
    elif (lp < tp):
        curr_price_1y_quantile_str = 'in 1Y middle quantile'
    else:
        curr_price_1y_quantile_str = 'in 1Y top quantile'

    #If price is in lower percentile then higher buy score
    #If price is in higher percentile then higher sell score
    if ((lp <= bp) or (lp >= tp)):
        if (lp <= bp):
            price_gscore += 2
        elif (lp >= tp):
            price_gscore -= 2
    else:
        if ((lp > bp) and (lp < mp)):
            price_gscore += 1

    price_max_score += 2

    price_grec = f'price_gscore:{price_gscore}/{price_max_score}'

    price_signals = f'price: {price_dir},{curr_count_quantile_str},{curr_price}:{curr_price_1y_quantile_str},{price_grec},{nftwlh}'

    return price_gscore, price_max_score, price_signals
