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

from pathlib import Path
import pandas as pd
import numpy as np

def get_qbs_signals(tsymbol, path, df_summ):

    cash = 0
    lti = 0
    sti = 0
    cash_earned_last_one_year = 0
    possible_remaining_cash = 0
    sequity = 0
    dtcr = 0

    qbs_gscore = 0
    qbs_max_score = 0
    cr_string = ''
    qr_string = ''
    qbs_string = ''

    cr = 0
    qr = 0

    #Check for current ratio for debt obligation readiness
    try:
        cr = df_summ['currentRatio'][0]
        if (np.isnan(cr)):
            cr_string = 'No current ratio data'
        else:
            cr = round(cr, 3)
            cr_string = f'{cr}'

            #Check if current ratio is >= 1
            if (cr >= 1):
                qbs_gscore += 1
            else:
                qbs_gscore -= 1
    except:
        cr_string = 'No current ratio data'

    qbs_max_score += 1

    #Check for quick ratio for debt obligation ease
    try:
        qr = df_summ['quickRatio'][0]
        if (np.isnan(qr)):
            qr_string = 'No quick ratio data'
        else:
            qr = round(qr, 3)
            qr_string = f'{qr}'
            #Check if quick ratio >= 1
            if (qr >= 1):
                qbs_gscore += 1
            else:
                qbs_gscore -= 1
    except:
        qr_string = 'No quick ratio data'

    qbs_max_score += 1

    file_exists = (path / f'{tsymbol}_qbs.csv').exists()

    #Check if file exists and is it from another day
    if file_exists:

        #Read Quarterly balance sheet CSV
        df = pd.read_csv(path / f'{tsymbol}_qbs.csv', index_col='Unnamed: 0')

        if (len(df) == 0):
            qbs_max_score += 2

            #This will show 0/2 for balance sheet component of qbs micro-gScore
            qbs_string += 'No balance sheet data'

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
                        qbs_string += ' No earnings data'
            except:
                cash = 0
                qbs_string += ' No cash data'

            try:
                sti = df[mrqd]['Short Term Investments']
            except:
                sti = 0
                qbs_string += ' No short term investments data'

            try:
                lti = df[mrqd]['Long Term Investments']
            except:
                lti = 0
                qbs_string += ' No long term investments data'

            #Add remaining cash to get an idea of cash position
            possible_remaining_cash += (cash + sti + lti)

            try:
                #Total shareholder equity
                sequity = df[mrqd]['Total Stockholder Equity']
                if (sequity > 0):
                    qbs_gscore += 1
                else:
                    qbs_gscore -= 1
            except:
                sequity = 0
                qbs_string += ' No shareholder equity data'

            qbs_max_score += 1

            try:
                #Long term debt
                ldebt = df[mrqd]['Long Term Debt']
            except:
                ldebt = 0
                qbs_string += ' No long term debt data'

            #Debt to capital ratio. TBD: Need to revisit the formula
            if ((ldebt > 0) and (sequity > 0)):
                dtcr = round((ldebt / (ldebt + sequity)), 3)
                if (dtcr <= 0.5):
                    qbs_gscore += 1
                else:
                    qbs_gscore -= 1

            #Max score from debt data
            qbs_max_score += 1
    else:

        qbs_max_score += 2

        #This will show 0/2 for balance sheet component of qbs micro-gScore
        qbs_string += 'No balance sheet data'


    qbs_grec = f'qbs_gscore:{qbs_gscore}/{qbs_max_score}'

    qbs_signals = f'qbs:dtcr:{dtcr},cr:{cr_string},qr:{qr_string},{qbs_string},{qbs_grec}'

    return qbs_gscore, qbs_max_score, qbs_signals
