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

import os
from pathlib import Path
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

#Estimate support and resistance lines

class GTRENDS:
    def __init__(self):
        self.Tickers_dir = Path('tickers')
        self.WEEKLY_TRADING_DAYS = 5
        self.y_support_series = pd.Series(dtype='float64')
        self.y_resistance_series = pd.Series(dtype='float64')

    #Get weekly lows and higs
    def get_weekly_lows_and_highs(self, df):

        df_len = len(df)

        #Weekly Lows
        start_index = (df_len-1)
        end_index = 0
        i = start_index
        curr_lowest = 0
        prev_lowest_val_index = -1
        curr_lowest_val_index = i
        weekly_low_indices = []
        while (i >= end_index):
            price = df.Close[i]
            if ((not curr_lowest) or (curr_lowest > price)):
                curr_lowest = price
                curr_lowest_val_index = i

            if (not (i % self.WEEKLY_TRADING_DAYS)):
                if (i > end_index):
                    while ((i > end_index) and (curr_lowest > df.Close[i-1])):
                        i -= 1
                        curr_lowest = df.Close[i]
                        curr_lowest_val_index = i

                if (prev_lowest_val_index != curr_lowest_val_index):
                    weekly_low_indices.append(curr_lowest_val_index)
                    prev_lowest_val_index = curr_lowest_val_index
                    curr_lowest = 0

            i -= 1

        #Save weekly lows in a data frame
        lmli_len = len(weekly_low_indices)
        df_lows = pd.DataFrame(columns=['OI', 'Date', 'Close'], index=pd.RangeIndex(lmli_len))
        df_lows_count = 0

        #Save it in correct order
        if (lmli_len):
            start_index = (lmli_len-1)
            end_index = 0
            i = start_index
            while (i >= end_index):
                df_lows.OI[df_lows_count] = weekly_low_indices[i]
                df_lows.Date[df_lows_count] = df.Date[weekly_low_indices[i]]
                df_lows.Close[df_lows_count] = df.Close[weekly_low_indices[i]]
                df_lows_count += 1
                i -= 1

        #Weekly Highs
        start_index = (df_len-1)
        end_index = 0
        i = start_index
        curr_highest = 0
        prev_highest_val_index = -1
        curr_highest_val_index = i
        weekly_high_indices = []
        while (i >= end_index):
            price = df.Close[i]
            if ((not curr_highest) or (curr_highest < price)):
                curr_highest = price
                curr_highest_val_index = i

            if (not (i % self.WEEKLY_TRADING_DAYS)):
                if (i > end_index):
                    while ((i > end_index) and (curr_highest < df.Close[i-1])):
                        i -= 1
                        curr_highest = df.Close[i]
                        curr_highest_val_index = i

                if (prev_highest_val_index != curr_highest_val_index):
                    weekly_high_indices.append(curr_highest_val_index)
                    prev_highest_val_index = curr_highest_val_index
                    curr_highest = 0

            i -= 1

        #Save weekly highs in a dataframe
        lmhi_len = len(weekly_high_indices)
        df_highs = pd.DataFrame(columns=['OI', 'Date', 'Close'], index=pd.RangeIndex(lmhi_len))
        df_highs_count = 0

        #Save it in correct order
        if (lmhi_len):
            start_index = (lmhi_len-1)
            end_index = 0
            i = start_index
            while (i >= end_index):
                df_highs.OI[df_highs_count] = weekly_high_indices[i]
                df_highs.Date[df_highs_count] = df.Date[weekly_high_indices[i]]
                df_highs.Close[df_highs_count] = df.Close[weekly_high_indices[i]]
                df_highs_count += 1
                i -= 1


        return df_lows, df_highs


    def get_closer_lp2(self, df, lp2_index):

        df_len = len(df)
        j = (df_len-1)
        val = df.Close[j]
        while (j > lp2_index):
            if (df.Close[j-1] < val):
                while ((j > lp2_index) and (df.Close[j-1] < val)):
                    j -= 1
                    val = df.Close[j]
                lp2_index = j
                break
            j -= 1

        return lp2_index

    def get_closer_lp1(self, df, lp1_index, lp2_index):

        df_len = len(df)
        j = lp2_index
        val = df.Close[j]
        while (j > lp1_index):
            if (df.Close[j-1] < val):
                while ((j > lp1_index) and (df.Close[j-1] < val)):
                    j -= 1
                    val = df.Close[j]
                lp1_index = j
                break
            j -= 1

        return lp1_index

    def get_closer_hp2(self, df, hp2_index):
        df_len = len(df)
        j = (df_len-1)
        val = df.Close[j]
        while (j > hp2_index):
            if (df.Close[j-1] > val):
                while ((j > hp2_index) and (df.Close[j-1] > val)):
                    j -= 1
                    val = df.Close[j]
                hp2_index = j
                break
            j -= 1

        return hp2_index

    def get_closer_hp1(self, df, hp1_index, hp2_index):
        j = hp2_index
        val = df.Close[j]
        while (j > hp1_index):
            if (df.Close[j-1] > val):
                while ((j > hp1_index) and (df.Close[j-1] > val)):
                    j -= 1
                    val = df.Close[j]
                hp1_index = j
                break
            j -= 1

        return hp1_index

    #Update support line if there are any crossing points
    def draw_correct_support_line(self, df, lp1_index, lp2_index):

        df_len = len(df)

        lp1 = df.Close[lp1_index]
        lp2 = df.Close[lp2_index]

        #Calculate slope for line between lp1 and lp2
        if (lp1_index == lp2_index):
            support_line_slope = 0
        else:
            support_line_slope = (lp2 - lp1)/(lp2_index - lp1_index)

        #Calculate the intercept
        support_line_c = (lp2 - (support_line_slope*lp2_index))

        #Check between lp2_index and (df_len-1)
        j = (df_len-1)
        ignore_lp1 = False
        while (j > lp2_index):
            val = df.Close[j]
            interim_lp = ((support_line_slope*j) + support_line_c)
            if (val < interim_lp):
                ignore_lp1 = True
                support_line_slope = 0
                lp1 = lp2
                lp1_index = lp2_index
                support_line_c = lp2
                break
            j -= 1

        if (not ignore_lp1):
            #Check between lp1_index and lp2_index
            j = (lp2_index-1)
            found_new_point = False
            while (j > lp1_index):
                val = df.Close[j]
                interim_lp = ((support_line_slope*j) + support_line_c)
                if (val < interim_lp):
                    support_line_slope = 0
                    lp1 = lp2
                    lp1_index = lp2_index
                    support_line_c = lp2
                    break
                j -= 1


        return lp1_index, lp2_index, support_line_slope, support_line_c

    #Update resistance line if there are any crossing points
    def draw_correct_resistance_line(self, df, hp1_index, hp2_index):
        df_len = len(df)
        hp1 = df.Close[hp1_index]
        hp2 = df.Close[hp2_index]
        #Calculate slope for line connecting hp1 and hp2
        if (hp1_index == hp2_index):
            resistance_line_slope = 0
        else:
            resistance_line_slope = (hp2 - hp1)/(hp2_index - hp1_index)

        #Calculate the intercept
        resistance_line_c = (hp2 - (resistance_line_slope*hp2_index))

        #Check between hp2_index and (df_len-1)
        j = (df_len-1)
        ignore_hp1 = False
        while (j > hp2_index):
            val = df.Close[j]
            interim_lp = ((resistance_line_slope*j) + resistance_line_c)
            if (val > interim_lp):
                ignore_hp1 = True
                resistance_line_slope = 0
                hp1 = hp2
                hp1_index = hp2_index
                resistance_line_c = hp2
                break
            j -= 1

        if (not ignore_hp1):
            #Check between hp1_index and hp2_index
            j = (hp2_index-1)
            while (j > hp1_index):
                val = df.Close[j]
                interim_lp = ((resistance_line_slope*j) + resistance_line_c)
                if (val > interim_lp):
                    hp1 = hp2
                    hp1_index = hp2_index
                    resistance_line_slope = 0
                    resistance_line_c = hp2
                    break
                j -= 1

        return hp1_index, hp2_index, resistance_line_slope, resistance_line_c

    #Plot charts
    def draw_trend_charts(self, tsymbol, path, df, sr_df):

        #Extract data
        df_len = len(df)
        x_vals = np.array([x for x in range(df_len)])
        lcp = df.Close[df_len-1]
        current_support_level_y = sr_df['CS_Y'][0]
        current_support_level_x = sr_df['CS_X'][0]
        current_resistance_level_y = sr_df['CR_Y'][0]
        current_resistance_level_x = sr_df['CR_X'][0]

        #Draw the charts
        figure, axes = plt.subplots(nrows=1, figsize=(14, 10))

        #Get DPI for the figure
        charts_dpi = figure.get_dpi()

        #Get the width and height in pixels for the figure
        charts_pw = figure.get_figwidth() * charts_dpi
        charts_ph = figure.get_figheight() * charts_dpi

        logo_file_found = True

        try:
            #Get the path of program/package
            pgm_dir_path, fn = os.path.split(__file__)

            #Append the data dir
            pgm_data_path = os.path.join(pgm_dir_path, 'data')

            #Read the logo
            logo_data = plt.imread(f'{pgm_data_path}/logo.png')
        except:
            logo_file_found = False

        #Need different widths for support/resistance lines compared to prices line
        plt.plot(x_vals, df.Close, lw=0.5, ls='-.', label=tsymbol)
        plt.plot(x_vals, self.y_support_series, lw=1, c='g', label='Current Approx. Moving Support Line')
        plt.plot(x_vals, self.y_resistance_series, lw=1, c='r', label='Current Approx. Moving Resistance Line')

        #Title for the chart
        plt.title('Current Approx. Moving Support and Resistance levels')

        #Need legend in the chart
        plt.legend()

        #We need to keep some distance between annotations to avoid overlap when
        #points are too close to each other. However, the distance seems to get
        #disproportionate.
        #Using arrowprops to clarify which text corresponds to which point

        #Support level
        plt.annotate(f'{round(current_support_level_y, 3)}', xy=(current_support_level_x, current_support_level_y), xytext=(current_support_level_x, (current_support_level_y-10)), arrowprops=dict(arrowstyle="->"))

        #Last price
        plt.annotate(f'{round(lcp, 3)}', xy=((df_len-1), lcp), xytext=((df_len-1)+10, lcp), arrowprops=dict(arrowstyle="->"))

        #Resistance level
        plt.annotate(f'{round(current_resistance_level_y, 3)}', xy=(current_resistance_level_x, current_resistance_level_y), xytext=(current_resistance_level_x, (current_resistance_level_y+10)), arrowprops=dict(arrowstyle="->"))

        if (logo_file_found):
            #Attach logo to the figure
            plt.figimage(logo_data, xo=charts_pw/2, yo=(charts_ph-100))

        #Save trend charts for later reference (Use PDF instead of png to save space)
        plt.savefig(path / f'{tsymbol}_tc.pdf', format='pdf')

    #Compute current estimated moving support and resistance level
    def compute_support_and_resistance_levels(self, tsymbol, path, df, need_charts):

        #Get stock history length
        df_len=len(df)

        start_index = 0
        end_index = df_len

        #last price
        lcp = df.Close[df_len-1]

        #Get lows and highs for each week
        df_lows, df_highs = self.get_weekly_lows_and_highs(df)

        support_line_slope = 0
        resistance_line_slope = 0
        lp1 = 0
        lp2 = 0
        hp1 = 0
        hp2 = 0
        curr_lowest = lcp
        curr_highest = lcp

        #Create a series to save the points
        #We want to draw it alongside closing prices so keeping it same length
        self.y_support_series = pd.Series(np.nan, pd.RangeIndex(df_len))
        self.y_resistance_series = pd.Series(np.nan, pd.RangeIndex(df_len))

        #Generate x-axis
        x_vals = np.array([x for x in range(df_len)])

        #Support line
        start_index = (len(df_lows)-1)
        end_index = 0
        step = -1

        lp2 = df_lows.Close[0]
        lp2_index = df_lows.OI[0]
        start_point = lp2_index
        start_value = lp2

        for i in range(start_index, end_index, step):
            lp2 = df_lows.Close[i]
            lp2_index = df_lows.OI[i]
            orig_lp2_index = lp2_index
            lp1 = df_lows.Close[i-1]
            lp1_index = df_lows.OI[i-1]
            orig_lp1_index = lp1_index

            #Calculate slope for line connecting lp1 and lp2
            if (lp1_index == lp2_index):
                support_line_slope = 0
            else:
                support_line_slope = (lp2 - lp1)/(x_vals[lp2_index] - x_vals[lp1_index])

            #Calculate the intercept
            support_line_c = (lp2 - (support_line_slope*x_vals[lp2_index]))

            #project y-value for last x-value
            lp = ((support_line_slope*(df_len-1)) + support_line_c)

            #Check if this is a relevant line between lp1 to lp2
            if (support_line_slope and (lcp > lp)):
                #Relevant line. Check if interim points are all less than line points
                lp1_index, lp2_index, support_line_slope, support_line_c = self.draw_correct_support_line(df, lp1_index, lp2_index)
                lp2 = df.Close[lp2_index]
                lp1 = df.Close[lp1_index]
                #project y-value for last x-value
                lp = ((support_line_slope*(df_len-1)) + support_line_c)

            #Checks to decide which points to use
            diff_2p = (lcp - lp)
            diff_lp2 = (lcp - lp2)
            diff_lp1 = (lcp - lp1)

            if (lcp > lp): #Valid line found
                #Use lp1 to lp2 line (by default)
                start_point = lp1_index
                start_value = lp1
                if (lcp > lp2): #Check if we should use lp2 instead
                    if (diff_lp2 <= diff_2p):
                        #Use lp2 line
                        support_line_slope = 0
                        #Find a closer lp2
                        lp2_index = self.get_closer_lp2(df, lp2_index)
                        start_point = lp2_index
                        start_value = df.Close[lp2_index]
            else: #Check if lp1 or lp2 qualify
                support_line_slope = 0 #Flat line
                lp2 = df.Close[orig_lp2_index]
                lp2_index = orig_lp2_index
                lp1 = df.Close[orig_lp1_index]
                lp1_index = orig_lp1_index
                #Find a closer lp2
                lp2_index = self.get_closer_lp2(df, lp2_index)
                if (lp2_index != orig_lp2_index):
                    lp2 = df.Close[lp2_index]
                    lp1_index = orig_lp2_index
                    lp1 = df.Close[lp1_index]

                diff_lp2 = (lcp - lp2)

                #Find a closer lp1
                lp1_index = self.get_closer_lp1(df, lp1_index, lp2_index)
                if (lp1_index != orig_lp1_index):
                    lp1 = df.Close[lp1_index]

                diff_lp1 = (lcp - lp1)

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

        #If this is a slant line, check if it is "too" far from last price
        if (support_line_slope and (lcp < lp1) and (lcp < lp2)):
            #Check if there is a better flat line
            #Start checking from lp2
            i = lp2_index
            while (i>=0):
                #We want the val to be less than last price
                if (df.Close[i] < lcp):
                    while ((i >= 1) and (df.Close[i-1] < df.Close[i])):
                        i -= 1
                    if (diff_2p > (lcp-df.Close[i])):
                        #Our line is farther so pick this point for flat line
                        support_line_slope = 0
                        #Use these coordinates
                        start_value = df.Close[i]
                        start_point = i
                    break
                i -= 1

        #Calculate intercept based on which points we picked
        support_line_c = (start_value - (support_line_slope*x_vals[start_point]))

        #Calculate points for drawing the line
        for j in range(start_point, (df_len)):
            self.y_support_series[j] = ((support_line_slope*j) + support_line_c)

        #Keep coordinates to annotate the chart
        current_support_level_y = self.y_support_series[df_len-1]
        current_support_level_x = (df_len-1)

        #Resistance line
        start_index = (len(df_highs)-1)
        end_index = 0
        step = -1

        hp2 = df_highs.Close[0]
        hp2_index = df_highs.OI[0]
        start_point = hp2_index
        start_value = hp2

        for i in range(start_index, end_index, step):
            hp2 = df_highs.Close[i]
            hp2_index = df_highs.OI[i]
            orig_hp2_index = hp2_index
            hp1 = df_highs.Close[i-1]
            hp1_index = df_highs.OI[i-1]
            orig_hp1_index = hp1_index

            #Calculate slope for line connecting hp1 and hp2
            if (hp1_index == hp2_index):
                resistance_line_slope = 0
            else:
                resistance_line_slope = (hp2 - hp1)/(x_vals[hp2_index] - x_vals[hp1_index])

            #Calculate the intercept
            resistance_line_c = (hp2 - (resistance_line_slope*x_vals[hp2_index]))

            #project y-value for last x-value
            lp = ((resistance_line_slope*(df_len-1)) + resistance_line_c)

            #Check if this is a relevant line between lp1 to lp2
            if (resistance_line_slope and (lcp < lp)):
                #Relevant line. Check if interim points are all less than line points
                hp1_index, hp2_index, resistance_line_slope, resistance_line_c = self.draw_correct_resistance_line(df, hp1_index, hp2_index)
                hp2 = df.Close[hp2_index]
                hp1 = df.Close[hp1_index]
                #project y-value for last x-value
                lp = ((resistance_line_slope*(df_len-1)) + resistance_line_c)

            #Checks to decide which points to use
            diff_2p = (lp - lcp)
            diff_hp2 = (hp2 - lcp)
            diff_hp1 = (hp1 - lcp)

            if (lcp < lp): #Valid line found
                #Use hp1 to hp2 line
                start_point = hp1_index
                start_value = hp1
                if (lcp < hp2):
                    if (diff_hp2 <= diff_2p): #Check if we should use hp2 instead
                        #Use hp2 line
                        resistance_line_slope = 0
                        #Find a closer hp2
                        hp2_index = self.get_closer_hp2(df, hp2_index)
                        start_point = hp2_index
                        start_value = df.Close[hp2_index]
            else: #Check if hp1 or hp2 can be used
                resistance_line_slope = 0
                hp2 = df.Close[orig_hp2_index]
                hp2_index = orig_hp2_index
                hp1 = df.Close[orig_hp1_index]
                hp1_index = orig_hp1_index
                if (hp2 > lcp):
                    #Find a closer hp2
                    hp2_index = self.get_closer_hp2(df, hp2_index)
                    if (hp2_index != orig_hp2_index):
                        hp1 = hp2
                        hp1_index = orig_hp2_index
                        hp2 = df.Close[hp2_index]

                diff_hp2 = (hp2 - lcp)

                if (hp1 > lcp):
                    #Find a closer hp1
                    hp1_index = self.get_closer_hp1(df, hp1_index, hp2_index)
                    if (hp1_index != orig_hp1_index):
                        hp1 = df.Close[hp1_index]

                diff_hp1 = (hp1 - lcp)

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

        #If this is a slant line, check if it is "too" far from last price
        if (resistance_line_slope and (lcp > hp1) and (lcp > hp2)):
            #Check if there is a better flat line
            #Start checking from hp2
            i = hp2_index
            while (i>=0):
                #We want the val to be more than last price
                if (df.Close[i] > lcp):
                    while ((i >= 1) and (df.Close[i-1] > df.Close[i])):
                        i -= 1
                    if (diff_2p > (df.Close[i]-lcp)):
                        #Our line is farther so pick this point for flat line
                        resistance_line_slope = 0
                        #Use these coordinates
                        start_value = df.Close[i]
                        start_point = i
                    break
                i -= 1

        #Calculate intercept based on which points we picked
        resistance_line_c = (start_value - (resistance_line_slope*x_vals[start_point]))

        #Calculate points for drawing the line
        for j in range(start_point, (df_len)):
            self.y_resistance_series[j] = ((resistance_line_slope*j) + resistance_line_c)

        #Keep coordinates to annotate the chart
        current_resistance_level_y = self.y_resistance_series[df_len-1]
        current_resistance_level_x = (df_len-1)

        #Create a dataframe for support and resistance data for different uses
        sr_df = pd.DataFrame(columns=['CS_Y', 'PDSL', 'CSDD', 'SLS', 'CS_X', 'CR_Y', 'RLS', 'PDRL', 'CRDD', 'CR_X'], index=range(1))
        sr_df['CS_Y'][0] = round(current_support_level_y, 3)
        sr_df['PDSL'][0] = round(((lcp - current_support_level_y)*100)/current_support_level_y, 3)
        sr_df['SLS'][0] = round(support_line_slope, 3)
        sr_df['CS_X'][0] = current_support_level_x
        sr_df['CR_Y'][0] = round(current_resistance_level_y, 3)
        sr_df['RLS'][0] = round(resistance_line_slope, 3)
        sr_df['PDRL'][0] = round(((current_resistance_level_y - lcp)*100)/current_resistance_level_y, 3)
        sr_df['CR_X'][0] = current_resistance_level_x

        if need_charts:
            self.draw_trend_charts(tsymbol, path, df, sr_df)

        return sr_df
