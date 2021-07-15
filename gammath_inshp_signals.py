# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd

def get_inshp_signals(tsymbol, df_summ):

    print('\nGetting Insider holdings percentage signals')
    inshp_buy_score = 0
    inshp_sell_score = 0
    inshp_max_score = 0

    inshp = df_summ['heldPercentInsiders'][0]

    print('inshp for ', tsymbol, ': ', inshp)

    if (inshp > 0):
        if (inshp < 0.1):
            inshp_buy_score += 1
        else:
            inshp_sell_score += 1

    inshp_max_score += 1

    inshp_buy_rec = f'inshp_buy_score:{inshp_buy_score}/{inshp_max_score}'
    inshp_sell_rec = f'inshp_sell_score:{inshp_sell_score}/{inshp_max_score}'

    inshp_signals = f'inshp:{inshp},{inshp_buy_rec},{inshp_sell_rec}'

    return inshp_buy_score, inshp_sell_score, inshp_max_score, inshp_signals
