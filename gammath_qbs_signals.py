# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd

def get_qbs_signals(tsymbol, path):

    cash = 0
    lti = 0
    sti = 0
    cash_burnt_last_one_year = -1
    sequity = -1
    dtcr = -1
    print('\nGetting Quarterly balance sheet signals')

    file_exists = (path / f'{tsymbol}_qbs.csv').exists()

    #Check if file exists and is it from another day
    if file_exists:
        print(f'\nQuarterly balance sheet for {tsymbol} exists')
        df = pd.read_csv(path / f'{tsymbol}_qbs.csv')

        if (len(df) == 0):
            print(f'\nERROR: QBS balansheet dataframe is empty for {tsymbol}')
        else:
            df = pd.read_csv(path / f'{tsymbol}_qbs.csv', index_col='Unnamed: 0')

            #Get the most recent quarter date
            mrqd = df.columns[0]

            try:
                #Cash position at the end of last reported quarter
                cash = df[mrqd]['Cash']
                earnings_file_exists = (path / f'{tsymbol}_qe.csv').exists()
                if (earnings_file_exists):
                    dfe = pd.read_csv(path / f'{tsymbol}_qe.csv', index_col='Unnamed: 0')
                    try:
                        cash_burnt_last_one_year = dfe.Earnings.sum()
                        print('\nNumber of earnings is ', len(dfe))
                        if (len(dfe) > 4):
                            print(f'\nNumber Quaterly Earnings are more than one year duration for {tsymbol}')
                    except:
                        print(f'\nQuarterly earnings not found for {tsymbol}')
                        cash_burnt_last_one_year = 0
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

            #Debt to capital ratio. TBD: Need to revisit the formula for accuracy
            if ((ldebt > 0) and (sequity > 0)):
                dtcr = round(ldebt / (ldebt + sequity), 3)

    else:
        print(f'\nERROR: Quarterly balance sheet for {tsymbol} does NOT exist. Need to fetch it')

    qbs_buy_score = 0
    qbs_sell_score = 0
    qbs_max_score = 0

    if (cash_burnt_last_one_year > 0):
        possible_next_year_remaining_cash = cash_burnt_last_one_year + cash + sti + lti
    else:
        possible_next_year_remaining_cash = 0

    if (possible_next_year_remaining_cash > 0):
        qbs_buy_score += 2
        qbs_sell_score -= 2
    else:
        qbs_sell_score += 2
        qbs_buy_score -= 2

    qbs_max_score += 2

    if (sequity > 0):
        qbs_buy_score += 1
        qbs_sell_score -= 1
    else:
        qbs_sell_score += 1
        qbs_buy_score -= 1

    qbs_max_score += 1

    if (ldebt == 0):
        qbs_buy_score += 1
        qbs_sell_score -= 1
    elif (ldebt > 0):
        qbs_sell_score += 1
        qbs_buy_score -= 1

    qbs_max_score += 1

    if (dtcr > 0):
        if (dtcr >= 0.7):
            qbs_buy_score -= 3
            qbs_sell_score += 3
        else:
            qbs_buy_score += 1

            if (dtcr < 0.4):
                qbs_buy_score += 1

            if (dtcr < 0.2):
                qbs_buy_score += 1
                qbs_sell_score -= 1

    qbs_max_score += 3

    qbs_buy_rec = f'qbs_buy_score:{qbs_buy_score}/{qbs_max_score}'
    qbs_sell_rec = f'qbs_sell_score:{qbs_sell_score}/{qbs_max_score}'

    qbs_signals = f'qbs:{qbs_buy_rec},{qbs_sell_rec},dtcr:{dtcr}'

    print(f'\nQBS signals extracted for {tsymbol}')
    return qbs_buy_score, qbs_sell_score, qbs_max_score, qbs_signals
