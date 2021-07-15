# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd

def get_peg_signals(tsymbol, df_summ):

    print('\nGetting PEG signals')
    peg_buy_score = 0
    peg_sell_score = 0
    peg_max_score = 0

    p = Path('.')

    peg = df_summ['pegRatio'][0]

    print('PEG ratio for ', tsymbol, ': ', peg)

    if (peg > 0):
        if (peg < 3):
            peg_buy_score += 1
        else:
            peg_sell_score += 1

    peg_max_score += 1

    peg_buy_rec = f'peg_buy_score:{peg_buy_score}/{peg_max_score}'
    peg_sell_rec = f'peg_sell_score:{peg_sell_score}/{peg_max_score}'

    peg_signals = f'PEG:{peg},{peg_buy_rec},{peg_sell_rec}'

    return peg_buy_score, peg_sell_score, peg_max_score, peg_signals