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


def get_reco_signals(tsymbol, path):

    buy_recos = ('Above Average', 'Accumulate', 'Add', 'Buy', 'Conviction Buy', 'Gradually Accumulate', 'Long-Term Buy', 'Long-term Buy', 'Market Outperform', 'Outperform', 'Outperformer', 'Overweight', 'Positive', 'Sector Outperform', 'Strong Buy', 'Top Pick')

    reco_gscore = 0
    reco_max_score = 0

    try:
        file_exists = (path / f'{tsymbol}_reco.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            df = pd.read_csv(path / f'{tsymbol}_reco.csv')
            len_df = len(df)
            if (len_df == 0):
                #This will allow doing our own fundamental analysis.
                reco_max_score = 0
            else:
                #We only want recent data so get shorter of last 25% of recommendations from entire list; 25% to align with approximately quarterly updates
                df_25p_index = len_df - int((len_df * 25) / 100)
                if (df_25p_index < len_df):
                    start_index = df_25p_index
                else:
                    start_index = 0

                #Shorter list for recent recommendations
                shorter_df = df[start_index:len_df]

                total_recos = len(shorter_df)

                buy_count = 0
                sell_count = 0

                #Extract count for buy/sell/positive recommendations
                for grade in shorter_df['To Grade']:
                    if (grade in buy_recos):
                        buy_count += 1
                    else:
                        sell_count += 1


                #Get the percentage of +ve recommendations
                buy_percentage = buy_count*100/total_recos

                #Reduce buy score and increase sell score
                if (buy_percentage < 50):
                    reco_gscore -= 4
                else:
                    reco_gscore += 2

                    if (buy_percentage >= 75):
                        reco_gscore += 2

                reco_max_score += 4

                #Extract count for recent upgrades/downgrades recommendations
                up_count = 0
                down_count = 0

                for action in shorter_df['Action']:
                    if (action == 'up'):
                        up_count += 1
                    elif (action == 'down'):
                        down_count += 1

                #Get the percentage of +ve recommendations
                total_up_down_count = up_count + down_count
                if (total_up_down_count > 0):
                    up_percentage = (up_count*100)/total_up_down_count
                else:
                    up_percentage = 0

                #More weightage to recent upgrade/downgrade compared to buy/sell reco
                if (up_percentage < 50):
                    reco_gscore -= 6
                else:
                    reco_gscore += 3

                    if (up_percentage >= 75):
                        reco_gscore += 3

                reco_max_score += 6

        else:
            #This will show 0/0 where expert recommendations don't exist.
            reco_max_score = 0
    except:
        raise RuntimeError('Quarterly Recommendations scoring failed')


    reco_signals = f'reco:reco_gscore:{reco_gscore}/{reco_max_score}'

    return reco_gscore, reco_max_score, reco_signals
