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

#TBD. Price direction probability is WIP (Work-In-Progress) and untested. Please do NOT use

import pandas as pd
import numpy as np

def get_price_dir_probability(df):

    MAX_COUNTS_LEN = 100
    prices = df.Close
    prices_len = len(prices)
    last_falling_days_count = 0
    last_rising_days_count = 0
    total_up_days = 0
    total_down_days = 0
    
    #zero-initialize
    price_consec_up_dir_counts = [0 for x in range(MAX_COUNTS_LEN)]
    price_consec_down_dir_counts = [0 for x in range(MAX_COUNTS_LEN)]

    #Get historical exact number of n-days up, down days
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

    overall_up_probability = round(total_up_days/(prices_len-1), 3)
    overall_down_probability = round(total_down_days/(prices_len-1), 3)

    #Get historical "all n-days" up, down counts
    for i in range(1, MAX_COUNTS_LEN):
        total = 0
        for j in range(i+1, MAX_COUNTS_LEN):
            total += price_consec_up_dir_counts[j]*i

        price_consec_up_dir_counts[i] += total

    for i in range(1, MAX_COUNTS_LEN):
        total = 0
        for j in range(i+1, MAX_COUNTS_LEN):
            total += price_consec_down_dir_counts[j]*i

        price_consec_down_dir_counts[i] += total

    curr_count = 0
    next_up_p = 0
    next_down_p = 0

    #Compute probabilities
    if (last_falling_days_count):
        curr_count = last_falling_days_count
        next_down_p = round(price_consec_down_dir_counts[last_falling_days_count+1]/(prices_len-1), 3)
        next_up_p = round(1 - next_down_p, 3)
    elif (last_rising_days_count):
        curr_count = last_rising_days_count
        next_up_p = round(price_consec_up_dir_counts[last_rising_days_count+1]/(prices_len-1), 3)
        next_down_p = round(1 - next_up_p, 3)

    pdp = f'Overall_PDP: UP: {overall_up_probability} DOWN: {overall_down_probability}\nNext_day_PDP: UP: {next_up_p} DOWN: {next_down_p}'

    return next_up_p, pdp
