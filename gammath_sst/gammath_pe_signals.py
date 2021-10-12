# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd

Tickers_dir = Path('./tickers')

def get_pe_signals(tsymbol, df_summ):

    print(f'\nGetting PE signals for {tsymbol}')

    path = Tickers_dir
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    pe_buy_score = 0
    pe_sell_score = 0
    pe_max_score = 0

    if not (path / 'SP500_SEC_PES.csv').exists():
        print('\nStock PE info file not found for ticker ', tsymbol)
    else:
        print('\nSP500_SEC_PES file found')
        df_sp = pd.read_csv(path / 'SP500_SEC_PES.csv')

    tpe = round(df_summ['trailingPE'][0], 3)
    fpe = round(df_summ['forwardPE'][0], 3)
    avg_tpe = 0
    avg_fpe = 0

    print(f'\nTPE {tsymbol}: {tpe}')
    print(f'\nFPE {tsymbol}: {fpe}')

    len_df_sp = len(df_sp)
    print('\nSP500 list size: ', len_df_sp, 'First symbol: ', df_sp['Symbol'][0])

    for i in range(len_df_sp):
        if (df_sp['Symbol'][i] == tsymbol):
            print('\nFound ticker in SP500 list for ', tsymbol)
            avg_tpe = round(df_sp['LS_AVG_TPE'][i], 3)
            avg_fpe = round(df_sp['LS_AVG_FPE'][i], 3)

            print('Avg TPE for ', tsymbol, 'is ', avg_tpe)
            print('Avg FPE for ', tsymbol, 'is ', avg_fpe)

            if ((tpe > 0) and (avg_tpe > 0)):
                #If below average trailing PE then improve buy score else improve sell score
                if (tpe < avg_tpe):
                    pe_buy_score += 1
                    pe_sell_score -= 1
                else:
                    pe_sell_score += 1
                    pe_buy_score -= 1

            pe_max_score += 1

            if ((fpe > 0) and (avg_fpe > 0)):
                #If below average forward PE then improve buy score else improve sell score
                if (fpe < avg_fpe):
                    pe_buy_score += 1
                    pe_sell_score -= 1
                else:
                    pe_sell_score += 1
                    pe_buy_score -= 1

            pe_max_score += 1

            #If forward PE is less than trailing PE then view this as a +ve sign
            if ((fpe > 0) and (tpe > 0)):
                if (fpe <= tpe):
                    pe_buy_score += 2
                    pe_sell_score -= 2
                else:
                    pe_buy_score -= 2
                    pe_sell_score += 2

            pe_max_score += 2

            break

    if (i == (len_df_sp-1)):
        print('\nReference PE data not found for sector and/or ticker ', tsymbol)

        pe_buy_score = 0
        pe_sell_score = 0

        #No data viewed as a -ve so have an impact on total score
        pe_max_score = 4

    pe_buy_rec = f'pe_buy_score:{pe_buy_score}/{pe_max_score}'
    pe_sell_rec = f'pe_sell_score:{pe_sell_score}/{pe_max_score}'

    pe_signals = f'TPE:{tpe},ATPE:{avg_tpe},FPE:{fpe},AFPE:{avg_fpe},{pe_buy_rec},{pe_sell_rec}'

    return pe_buy_score, pe_sell_score, pe_max_score, pe_signals
