# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd

def get_peg_signals(tsymbol, df_summ):

    peg_dip_score = 0
    peg_max_score = 0

    try:
        peg = round(df_summ['pegRatio'][0], 3)
    except:
        raise ValueError('PEG value not found')

    if (peg > 0):
        if (peg < 3):
            peg_dip_score += 1
        else:
            peg_dip_score -= 1

    peg_max_score += 1

    peg_dip_rec = f'peg_dip_score:{peg_dip_score}/{peg_max_score}'

    peg_signals = f'PEG:{peg},{peg_dip_rec}'

    return peg_dip_score, peg_max_score, peg_signals
