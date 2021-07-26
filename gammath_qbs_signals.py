# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd

MIN_CASH_BALANCE = 100000000

def get_qbs_signals(tsymbol, path):

    cash = 0
    sequity = -1
    dtcr = -1
    print('\nGetting Quarterly balance sheet signals')

    file_exists = (path / f'{tsymbol}_qbs.csv').exists()

    #Check if file exists and is it from another day
    if file_exists:
        print(f'\nQuarterly balance sheet for {tsymbol} exists')
        df = pd.read_csv(path / f'{tsymbol}_qbs.csv', index_col='Unnamed: 0')

        #Get the most recent quarter date
        mrqd = df.columns[0]

        try:
            #Cash position at the end of last reported quarter
            cash = df[mrqd]['Cash']
        except:
            print(f'\nCash item not found in quarterly balance sheet for {tsymbol}')
            cash = 0

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

    #TBD: Build on this later
    if (cash >= MIN_CASH_BALANCE):
        qbs_buy_score += 1
    else:
        qbs_sell_score += 1

    qbs_max_score += 1

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

    return qbs_buy_score, qbs_sell_score, qbs_max_score, qbs_signals
