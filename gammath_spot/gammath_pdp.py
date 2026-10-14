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

# Dynamic Price direction probability for next day with respect overall sample
import numpy as np
import pandas as pd
import sys

# Get overall empirical overall Price direction probability and empirical direction probability for next day based on price history
# Note: This treats flat as up so there is inherent bias
def get_price_dir_probability(df):
    prices = df.Close
    prices_len = len(prices)

    #Can't assume how many consecutive days a stock will go up or down so use full length
    MAX_COUNTS_LEN = prices_len
    last_falling_days_count = 0
    last_rising_days_count = 0
    total_up_days = 0
    total_down_days = 0

    #zero-initialize
    price_consec_up_dir_counts = [0 for x in range(MAX_COUNTS_LEN)]
    price_consec_down_dir_counts = [0 for x in range(MAX_COUNTS_LEN)]

    #The intent is to arrange these as follows:
    # Step 1: Get "exact count" for 'i' number of up/down days
    # Step 2: Get "at least" count for 'i' number of up/down days to show count for 'i' or more number of up/down days

    #Get historical exact number of only-n-days up/down days
    for i in range(1, prices_len):
        if (prices[i-1] <= prices[i]): #equal or rising

            total_up_days += 1

            if (last_falling_days_count and (last_falling_days_count < MAX_COUNTS_LEN)):
                price_consec_down_dir_counts[last_falling_days_count] += 1
                last_falling_days_count = 0

            last_rising_days_count += 1

        elif (prices[i-1] > prices[i]): #falling

            total_down_days += 1

            if (last_rising_days_count and (last_rising_days_count < MAX_COUNTS_LEN)):
                price_consec_up_dir_counts[last_rising_days_count] += 1
                last_rising_days_count = 0

            last_falling_days_count += 1

    #Get overall up/down probability
    overall_up_probability = round(total_up_days/(prices_len-1), 3)
    overall_down_probability = round(total_down_days/(prices_len-1), 3)

    price_consec_up_dir_counts[1:] = np.cumsum(price_consec_up_dir_counts[:0:-1])[::-1]
    price_consec_down_dir_counts[1:] = np.cumsum(price_consec_down_dir_counts[:0:-1])[::-1]

    next_up_p = 0
    next_down_p = 0

    if (last_falling_days_count):
        curr_count, ref_consec_counts, falling = last_falling_days_count, price_consec_down_dir_counts, True
    else:
        curr_count, ref_consec_counts, falling = last_rising_days_count, price_consec_up_dir_counts, False

    #Compute conditional probability (rather it is gauging how often this happened in past n days of data)
    if curr_count and ((curr_count + 1) < MAX_COUNTS_LEN) and (ref_consec_counts[curr_count] > 0):
        p_streak_continues = ref_consec_counts[curr_count+1] / ref_consec_counts[curr_count]
        next_down_p = round((p_streak_continues if falling else (1 - p_streak_continues)), 3)
        next_up_p = round(((1 - p_streak_continues) if falling else p_streak_continues), 3)

    pdp = f'Overall_empirical_PDP: UP: {overall_up_probability} DOWN: {overall_down_probability}\nNext_day_empirical_PDP: UP: {next_up_p} DOWN: {next_down_p}'

    return next_up_p, pdp
