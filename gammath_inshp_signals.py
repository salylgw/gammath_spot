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
    inshp_change = round(df_summ['heldPercentInsidersChange'][0], 3)
    inshp_change_dir = df_summ['heldPercentInsidersChangeDir'][0]

    print('inshp for ', tsymbol, ': ', inshp)

    if (inshp > 0):
        inshp_buy_score += 1
    else:
        inshp_sell_score += 1

    inshp_max_score += 1

    if (inshp_change_dir == 'up'):
        inshp_buy_score += 1
        inshp_sell_score -= 1
    elif (inshp_change_dir == 'down'):
        inshp_buy_score -= 1
        inshp_sell_score += 1

    inshp_max_score += 1

    if (inshp_change > 0):
        inshp_buy_score += 1
        inshp_sell_score -= 1
    elif (inshp_change < 0):
        inshp_buy_score -= 1
        inshp_sell_score += 1

    inshp_max_score += 1

    inshp_buy_rec = f'inshp_buy_score:{inshp_buy_score}/{inshp_max_score}'
    inshp_sell_rec = f'inshp_sell_score:{inshp_sell_score}/{inshp_max_score}'

    inshp_signals = f'inshp:{inshp},{inshp_buy_rec},{inshp_sell_rec},inshp_change:{inshp_change},dir:{inshp_change_dir}'

    return inshp_buy_score, inshp_sell_score, inshp_max_score, inshp_signals
