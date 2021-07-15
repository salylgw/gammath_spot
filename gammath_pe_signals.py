# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd

def get_pe_signals(tsymbol, df_summ):

    print('\nGetting PE signals')
    pe_buy_score = 0
    pe_sell_score = 0
    pe_max_score = 0

    p = Path('.')

    if not (p / 'SP500_US_ONLY_SEC_PES.csv').exists():
        print('\nStock PE info file not found for ticker ', tsymbol)
    else:
        print('\nSP500_US_ONLY_SEC_PES file found')
        df_sp = pd.read_csv(p / 'SP500_US_ONLY_SEC_PES.csv')

    tpe = df_summ['trailingPE'][0]
    fpe = df_summ['forwardPE'][0]

    print('TPE: ', tpe)
    print('FPE: ', fpe)

    len_df_sp = len(df_sp)
    print('\nSP500 list size: ', len_df_sp, 'First symbol: ', df_sp['Symbol'][0])

    for i in range(len_df_sp):
        if (df_sp['Symbol'][i] == tsymbol):
            print('\nFound ticker in SP500 list for ', tsymbol)
            avg_tpe = df_sp['LS_AVG_TPE'][i]
            avg_fpe = df_sp['LS_AVG_FPE'][i]

            print('Abg TPE for ', tsymbol, 'is ', avg_tpe)
            print('Abg FPE for ', tsymbol, 'is ', avg_fpe)

            if (tpe > 0):
                if (tpe < avg_tpe):
                    pe_buy_score += 1
                else:
                    pe_sell_score += 1

            if (fpe > 0):
                if (fpe < avg_fpe):
                    pe_buy_score += 1
                else:
                    pe_sell_score +=1

            break

    if (i == (len_df_sp-1)):
        print('\nReference Avg PE for sector not found for ticker ', tsymbol)
        pe_buy_score = 0
        pe_sell_score = 0

    pe_max_score += 2

    pe_buy_rec = f'pe_buy_score:{pe_buy_score}/{pe_max_score}'
    pe_sell_rec = f'pe_sell_score:{pe_sell_score}/{pe_max_score}'

    pe_signals = f'TPE:{tpe},FPE:{fpe},{pe_buy_rec},{pe_sell_rec}'

    return pe_buy_score, pe_sell_score, pe_max_score, pe_signals