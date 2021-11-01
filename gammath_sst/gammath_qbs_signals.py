# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd

def get_qbs_signals(tsymbol, path):

    print(f'\nGetting Quarterly Balance Sheet signals for {tsymbol}')

    cash = 0
    lti = 0
    sti = 0
    cash_earned_last_one_year = 0
    possible_remaining_cash = 0
    sequity = 0
    dtcr = 0

    qbs_buy_score = 0
    qbs_sell_score = 0
    qbs_max_score = 0

    file_exists = (path / f'{tsymbol}_qbs.csv').exists()

    #Check if file exists and is it from another day
    if file_exists:
        print(f'\nQuarterly balance sheet for {tsymbol} exists')

        #Read Quarterly balance sheet CSV
        df = pd.read_csv(path / f'{tsymbol}_qbs.csv', index_col='Unnamed: 0')

        if (len(df) == 0):
            print(f'\nERROR: QBS balansheet dataframe is empty for {tsymbol}')
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
                            else:
                                print(f'\nNot enough Quarterly Earnings data for {tsymbol}. Earnings quarters: {dfe_len} ')
                        else:
                            print(f'\nERROR: Earnings dataframe is empty for {tsymbol}')
                    except:
                        print(f'\nQuarterly earnings not found for {tsymbol}')
                        cash_earned_last_one_year = 0
                else:
                    print(f'\nEarnings file not found for {tsymbol}')
            except:
                print(f'\nCash item not found in quarterly balance sheet for {tsymbol}')
                cash = 0

            try:
                sti = df[mrqd]['Short Term Investments']
            except:
                print(f'\nShort term investments item not found for {tsymbol}')
                sti = 0

            try:
                lti = df[mrqd]['Long Term Investments']
            except:
                print(f'\nLong term investments item not found for {tsymbol}')
                lti = 0

            try:
                #Total shareholder equity
                sequity = df[mrqd]['Total Stockholder Equity']
            except:
                print(f'\nTotal shareholder equity item not found in quarterly balance sheet for {tsymbol}')

            try:
                #Long term debt
                ldebt = df[mrqd]['Long Term Debt']
            except:
                print(f'\nLong Term Debt item not found in quarterly balance sheet for {tsymbol}')
                ldebt = 0

            #Debt to capital ratio. TBD: Need to revisit the formula
            if ((ldebt > 0) and (sequity > 0)):
                dtcr = round((ldebt / (ldebt + sequity)), 3)

            #For now just check if cash earned is +ve
            if (cash_earned_last_one_year > 0):
                qbs_buy_score += 1
                qbs_sell_score -= 1
            else:
                qbs_sell_score += 1
                qbs_buy_score -= 1

            qbs_max_score += 1

            #Add remaining cash to get an idea of cash position
            possible_remaining_cash += (cash + sti + lti)

            #For now just check if there is +ve remaining cash past last year's earnings
            if (possible_remaining_cash > cash_earned_last_one_year):
                qbs_buy_score += 1
                qbs_buy_score -= 1
            else:
                qbs_sell_score += 1
                qbs_buy_score -= 1

            qbs_max_score += 1

            if (sequity > 0):
                qbs_buy_score += 1
            else:
                qbs_sell_score += 1

            qbs_max_score += 1

            if (ldebt > 0) and (ldebt <= 0.5):
                qbs_buy_score += 1
                qbs_sell_score -= 1
            else:
                qbs_sell_score += 1
                qbs_buy_score -= 1

            #Max score from debt data
            qbs_max_score += 1
    else:
        print(f'\nERROR: Quarterly balance sheet for {tsymbol} does NOT exist.')
        #This will show 0/4 when no balance sheet data
        raise ValueError('QBS file doesn\'t exist')

    qbs_buy_rec = f'qbs_buy_score:{qbs_buy_score}/{qbs_max_score}'
    qbs_sell_rec = f'qbs_sell_score:{qbs_sell_score}/{qbs_max_score}'

    qbs_signals = f'qbs:{qbs_buy_rec},{qbs_sell_rec},dtcr:{dtcr}'

    print(f'\nQBS signals extracted for {tsymbol}')
    return qbs_buy_score, qbs_sell_score, qbs_max_score, qbs_signals
