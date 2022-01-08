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

def get_qbs_signals(tsymbol, path):

    cash = 0
    lti = 0
    sti = 0
    cash_earned_last_one_year = 0
    possible_remaining_cash = 0
    sequity = 0
    dtcr = 0

    qbs_gscore = 0
    qbs_max_score = 0

    file_exists = (path / f'{tsymbol}_qbs.csv').exists()

    #Check if file exists and is it from another day
    if file_exists:

        #Read Quarterly balance sheet CSV
        df = pd.read_csv(path / f'{tsymbol}_qbs.csv', index_col='Unnamed: 0')

        if (len(df) == 0):
            raise ValueError('QBS dataframe empty')
        else:

            #Get the most recent quarter date
            mrqd = df.columns[0]

            try:
                #Cash position at the end of last reported quarter
                cash = df[mrqd]['Cash']
                earnings_file_exists = (path / f'{tsymbol}_qe.csv').exists()
                if (earnings_file_exists):
                    dfe = pd.read_csv(path / f'{tsymbol}_qe.csv', index_col='Unnamed: 0')
                    try:
                        dfe_len = len(dfe)
                        if (dfe_len > 0):
                            if (dfe_len >= 4):
                                #Get the sum for last 4 quarters
                                cash_earned_last_one_year = dfe.Earnings[(dfe_len-4):].sum()
                    except:
                        cash_earned_last_one_year = 0
            except:
                cash = 0

            try:
                sti = df[mrqd]['Short Term Investments']
            except:
                sti = 0

            try:
                lti = df[mrqd]['Long Term Investments']
            except:
                lti = 0

            try:
                #Total shareholder equity
                sequity = df[mrqd]['Total Stockholder Equity']
            except:
                sequity = 0

            try:
                #Long term debt
                ldebt = df[mrqd]['Long Term Debt']
            except:
                ldebt = 0

            #Debt to capital ratio. TBD: Need to revisit the formula
            if ((ldebt > 0) and (sequity > 0)):
                dtcr = round((ldebt / (ldebt + sequity)), 3)

            #For now just check if cash earned is +ve
            if (cash_earned_last_one_year > 0):
                qbs_gscore += 1
            else:
                qbs_gscore -= 1

            qbs_max_score += 1

            #Add remaining cash to get an idea of cash position
            possible_remaining_cash += (cash + sti + lti)

            #For now just check if there is +ve remaining cash past last year's earnings
            if (possible_remaining_cash > cash_earned_last_one_year):
                qbs_gscore += 1
            else:
                qbs_gscore -= 1

            qbs_max_score += 1

            if (sequity > 0):
                qbs_gscore += 1
            else:
                qbs_gscore -= 1

            qbs_max_score += 1

            if (ldebt > 0) and (ldebt <= 0.5):
                qbs_gscore += 1
            else:
                qbs_gscore -= 1

            #Max score from debt data
            qbs_max_score += 1
    else:
        #This will show 0/4 when no balance sheet data
        raise ValueError('QBS file doesn\'t exist')

    qbs_grec = f'qbs_gscore:{qbs_gscore}/{qbs_max_score}'

    qbs_signals = f'qbs:dtcr:{dtcr},{qbs_grec}'

    return qbs_gscore, qbs_max_score, qbs_signals
