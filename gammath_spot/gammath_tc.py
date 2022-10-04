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

from pathlib import Path
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from talib import HT_TRENDLINE

#This is experimental and Work-In-Progress
#Please do not use yet

def get_monthly_lows_and_highs(df):
    MAX_COUNTS_LEN = 100
    MONTHLY_TRADING_DAYS = 21
    WEEKLY_TRADING_DAYS = 5

    df_len = len(df)

    #Monthly Lows
    df_lows = pd.DataFrame(columns=['OI', 'Date', 'Close'], index=pd.RangeIndex(MAX_COUNTS_LEN))
    df_highs = pd.DataFrame(columns=['OI', 'Date', 'Close'], index=pd.RangeIndex(MAX_COUNTS_LEN))

    df_lows_count = 0
    df_highs_count = 0

    end_index = (df_len - MONTHLY_TRADING_DAYS)
    i = 0
    curr_lowest = df.Close[i]
    prev_lowest_val_index = 0
    curr_lowest_val_index = i
    while (i < end_index):
        price = df.Close[i]

        if ((not curr_lowest) or (curr_lowest > price)):
            curr_lowest = price
            curr_lowest_val_index = i

        month_boundary = ((i % MONTHLY_TRADING_DAYS) == 0)
        last_index = (i == (end_index-1))

        if (month_boundary and (not last_index)):
            #Get lowest on this line to avoid a point that is end-of-month but not really lowest on line
            while ((curr_lowest > df.Close[i+1]) and (i > (end_index-1))):
                i += 1
                curr_lowest = df.Close[i]
                curr_lowsest_val_index = i

        #Only need to update check for last index
        last_index = (i == (end_index-1))

        if ((month_boundary or last_index) and (prev_lowest_val_index != curr_lowest_val_index)):
            df_lows.OI[df_lows_count] = curr_lowest_val_index
            df_lows.Date[df_lows_count] = df.Date[curr_lowest_val_index]
            df_lows.Close[df_lows_count] = df.Close[curr_lowest_val_index]
            prev_lowest_val_index = curr_lowest_val_index
            df_lows_count += 1
            curr_lowest = 0

        i += 1

    #Monthly Highs
    end_index = (df_len - MONTHLY_TRADING_DAYS)
    i = 0
    curr_highest = df.Close[i]
    prev_highest_val_index = 0
    curr_highest_val_index = i
    while (i < end_index):
        price = df.Close[i]

        if ((not curr_highest) or (curr_highest < price)):
            curr_highest = price
            curr_highest_val_index = i

        month_boundary = ((i % MONTHLY_TRADING_DAYS) == 0)
        last_index = (i == (end_index-1))

        if (month_boundary and (not last_index)):
            #Get highest on this line to avoid a point that is end-of-month but not really highest on line
            while ((curr_highest < df.Close[i+1]) and (i > (end_index-1))):
                i += 1
                curr_highest = df.Close[i]
                curr_highest_val_index = i

        #Only need to update check for last index
        last_index = (i == (end_index-1))

        if ((month_boundary or last_index) and (prev_highest_val_index != curr_highest_val_index)):
            df_highs.OI[df_highs_count] = curr_highest_val_index
            df_highs.Date[df_highs_count] = df.Date[curr_highest_val_index]
            df_highs.Close[df_highs_count] = df.Close[curr_highest_val_index]
            prev_highest_val_index = curr_highest_val_index
            df_highs_count += 1
            curr_highest = 0

        i += 1


    #Last month
    #Lows
    #Look between end to month boundary

    start_index = (df_len-1)
    end_index = (start_index-MONTHLY_TRADING_DAYS)
    i = start_index
    curr_lowest = df.Close[i]
    prev_lowest_val_index = 0
    curr_lowest_val_index = i
    last_month_low_indices = []
    while (i > end_index):
        price = df.Close[i]
        if (curr_lowest > price):
            curr_lowest = price
            curr_lowest_val_index = i

        if ((not (i % WEEKLY_TRADING_DAYS)) or (i == (end_index+1))):
            while ((curr_lowest > df.Close[i-1]) and (i > (end_index + 1))):
                i -= 1
                curr_lowest = df.Close[i]
                curr_lowest_val_index = i

            if (prev_lowest_val_index != curr_lowest_val_index):
                last_month_low_indices.append(curr_lowest_val_index)
                prev_lowest_val_index = curr_lowest_val_index

        i -= 1

    #Last month
    #Highs
    #Look between end to month boundary

    start_index = (df_len-1)
    end_index = (start_index-MONTHLY_TRADING_DAYS)
    i = start_index
    curr_highest = df.Close[i]
    prev_highest_val_index = 0
    curr_highest_val_index = i
    last_month_high_indices = []
    while (i > end_index):
        price = df.Close[i]
        if (curr_highest < price):
            curr_highest = price
            curr_highest_val_index = i

        if ((not (i % WEEKLY_TRADING_DAYS)) or (i == (end_index+1))):
            while ((curr_highest < df.Close[i-1]) and (i > (end_index + 1))):
                i -= 1
                curr_highest = df.Close[i]
                curr_highest_val_index = i

            if (prev_highest_val_index != curr_highest_val_index):
                last_month_high_indices.append(curr_highest_val_index)
                prev_highest_val_index = curr_highest_val_index

        i -= 1


    #Rearrange in correct order
    lmli_len = len(last_month_low_indices)
    if (lmli_len):
        start_index = (lmli_len-1)
        end_index = 0
        i = start_index
        while (i >= end_index):
            df_lows.OI[df_lows_count] = last_month_low_indices[i]
            df_lows.Date[df_lows_count] = df.Date[last_month_low_indices[i]]
            df_lows.Close[df_lows_count] = df.Close[last_month_low_indices[i]]
            df_lows_count += 1
            i -= 1

    #Rearrange in correct order
    lmhi_len = len(last_month_high_indices)
    if (lmhi_len):
        start_index = (lmhi_len-1)
        end_index = 0
        i = start_index
        while (i >= end_index):
            df_highs.OI[df_highs_count] = last_month_high_indices[i]
            df_highs.Date[df_highs_count] = df.Date[last_month_high_indices[i]]
            df_highs.Close[df_highs_count] = df.Close[last_month_high_indices[i]]
            df_highs_count += 1
            i -= 1

    #Remove extra rows
    df_lows = df_lows.truncate(after=(df_lows_count-1))
    df_highs = df_highs.truncate(after=(df_highs_count-1))

    return df_lows, df_highs

#Generate charts showing moving trends
def generate_trend_charts(tsymbol, df, path):
    df_len=len(df)

    start_index = 0
    end_index = df_len

    #last price
    lcp = df.Close[df_len-1]

    #Get lows and highs for each month
    df_lows, df_highs = get_monthly_lows_and_highs(df)

    low_slope = 0
    high_slope = 0
    lp1 = 0
    lp2 = 0
    hp1 = 0
    hp2 = 0
    curr_lowest = lcp
    curr_highest = lcp

    #Create a series to save the points
    y_low_series = pd.Series(np.nan, pd.RangeIndex(df_len))
    y_high_series = pd.Series(np.nan, pd.RangeIndex(df_len))

    #Generate x-axis
    x_vals = np.array([x for x in range(df_len)])

    start_index = (len(df_lows)-1)
    end_index = 0
    step = -1

    lp2 = df_lows.Close[0]
    lp2_index = df_lows.OI[0]
    start_point = lp2_index
    start_value = lp2

    #Low line
    for i in range(start_index, end_index, step):
        lp2 = df_lows.Close[i]
        lp2_index = df_lows.OI[i]
        lp1 = df_lows.Close[i-1]
        lp1_index = df_lows.OI[i-1]

        #Calculate slope for line connecting lp1 and lp2
        if (lp1_index == lp2_index):
            low_slope = 0
        else:
            low_slope = (lp2 - lp1)/(x_vals[lp2_index] - x_vals[lp1_index])

        #Calculate the intercept
        low_line_c = (lp2 - (low_slope*x_vals[lp2_index]))

        #project y-value for last x-value
        lp = ((low_slope*(df_len-1)) + low_line_c)

        #Checks to decide which points to use
        diff_2p = (lcp - lp)
        diff_lp2 = (lcp - lp2)
        diff_lp1 = (lcp - lp1)

        if (low_slope and (lcp > lp)): #Valid line found
            #Use lp1 to lp2 line (by default)
            start_point = lp1_index
            start_value = lp1
            if (lcp > lp2): #Check if we should use lp2 instead
                if (diff_lp2 < diff_2p):
                    #Use lp2 line
                    low_slope = 0
                    start_point = lp2_index
                    start_value = lp2
        else: #Check if lp1 or lp2 qualify
            low_slope = 0 #Flat line
            if (lcp > lp2):
                #Choose between lp2 and lp1
                if (lcp > lp1):
                    if (diff_lp2 < diff_lp1):
                        start_point = lp2_index
                        start_value = lp2
                    else:
                        start_point = lp1_index
                        start_value = lp1
                else:
                    start_point = lp2_index
                    start_value = lp2
            else:
                #Check if lp1 qualifies
                if (lcp > lp1):
                    start_point = lp1_index
                    start_value = lp1
                else:
                    #Valid line not found
                    continue

        break

    #We have a slant line that is possibly far from last price
    #Check if there is a better flat line
    if (low_slope and (lcp < lp1) and (lcp < lp2)):
        #Start from lp2_index
        i = lp2_index
        while (i>=0):
            #We want the val to be less than last price
            if (df.Close[i] < lcp):
                #Make sure it is lowest in this leg
                while ((i > 0) and (df.Close[i-1] < df.Close[i])):
                    i -= 1

                if (diff_2p > (lcp-df.Close[i])):
                    #Our line is farther so pick this point for flat line
                    low_slope = 0
                    #Use these coordinates
                    start_value = df.Close[i]
                    start_point = i
                    break
            i -= 1

    #Calculate intercept based on which points we picked
    low_line_c = (start_value - (low_slope*x_vals[start_point]))

    #Calculate points for drawing the line
    for j in range(start_point, (df_len)):
        y_low_series[j] = ((low_slope*j) + low_line_c)

    start_index = (len(df_highs)-1)
    end_index = 0
    step = -1

    hp2 = df_highs.Close[0]
    hp2_index = df_highs.OI[0]
    start_point = hp2_index
    start_value = hp2

    #High line
    for i in range(start_index, end_index, step):
        hp2 = df_highs.Close[i]
        hp2_index = df_highs.OI[i]
        hp1 = df_highs.Close[i-1]
        hp1_index = df_highs.OI[i-1]

        #Calculate slope for line connecting hp1 and hp2
        if (hp1_index == hp2_index):
            high_slope = 0
        else:
            high_slope = (hp2 - hp1)/(x_vals[hp2_index] - x_vals[hp1_index])

        #Calculate the intercept
        high_line_c = (hp2 - (high_slope*x_vals[hp2_index]))

        #project y-value for last x-value
        lp = ((high_slope*(df_len-1)) + high_line_c)

        #Checks to decide which points to use
        diff_2p = (lp - lcp)
        diff_hp2 = (hp2 - lcp)
        diff_hp1 = (hp1 - lcp)

        if (high_slope and (lcp < lp)): #Valid line found
            #Use hp1 to hp2 line
            start_point = hp1_index
            start_value = hp1
            if (lcp < hp2):
                if (diff_hp2 < diff_2p): #Check if we should use hp2 instead
                    #Use hp2 line
                    low_slope = 0
                    start_point = hp2_index
                    start_value = hp2
        else: #Check if hp1 or hp2 can be used
            high_slope = 0
            if (lcp < hp2):
                if (lcp < hp1):
                    if (diff_hp2 < diff_hp1):
                        start_point = hp2_index
                        start_value = hp2
                    else:
                        start_point = hp1_index
                        start_value = hp1
                else:
                    start_point = hp2_index
                    start_value = hp2
            else:
                if (lcp < hp1):
                    start_point = hp1_index
                    start_value = hp1
                else:
                    #Valid line not found
                    continue

        break

    #We have a slant line that is possibly far from last price
    #Check if there is a better flat line
    if (high_slope and (lcp > hp1) and (lcp > hp2)):
        #Start from hp2_index
        i = hp2_index
        while (i>=0):
            #We want the val to be more than last price
            if (df.Close[i] > lcp):
                while ((i > 0) and (df.Close[i-1] > df.Close[i])):
                    i -= 1
                if (diff_2p > (df.Close[i]-lcp)):
                    #Our line is farther so pick this point for flat line
                    high_slope = 0
                    #Use these coordinates
                    start_value = df.Close[i]
                    start_point = i
                    break
            i -= 1

    #Calculate intercept based on which points we picked
    high_line_c = (start_value - (high_slope*x_vals[start_point]))

    #Calculate points for drawing the line
    for j in range(start_point, (df_len)):
        y_high_series[j] = ((high_slope*j) + high_line_c)


    #Generate instantaneous trendline using Hilbert transform
    trendline = HT_TRENDLINE(df.Close)

    #Draw the charts
    figure, axes = plt.subplots(nrows=2, figsize=(28, 14))

    #Save the data frame for drawing charts
    df_trendline = pd.DataFrame({tsymbol: df.Close, 'Trend line': trendline})

    #Plot the chart
    df_trendline.plot(ax=axes[0],lw=1,title='Instantaneous Trendline')

    #Need different widths for support/resistance lines compared to prices line
    plt.plot(x_vals, df.Close, lw=0.5, ls='-.', c='b', label=tsymbol)
    plt.plot(x_vals, y_low_series, lw=1, c='g', label='Current Approx. Moving Support Line')
    plt.plot(x_vals, y_high_series, lw=1, c='r', label='Current Approx. Moving Resistance Line')

    plt.title('Current Approx. Moving Support and Resistance levels')
    plt.legend()

    #Save it for later reference (Use PDF instead of png to save space)
    plt.savefig(path / f'{tsymbol}_tc.pdf', format='pdf')

