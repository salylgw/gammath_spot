# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd

#Get percentage held by institutions for tsymbol
def get_ihp_signals(tsymbol, df_summ):

    print(f'\nGetting Institutional holdings percentage signals for {tsymbol}')

    ihp_buy_score = 0
    ihp_sell_score = 0
    ihp_max_score = 0

    #Get data about percentage held from summary dataframe
    ihp = df_summ['heldPercentInstitutions'][0]

    print('ihp for ', tsymbol, ': ', ihp)

    if (ihp > 0):
        if (ihp > 0.5):
            ihp_buy_score += 1
        else:
            ihp_sell_score += 1

        if (ihp > 0.7):
            ihp_buy_score += 1
        else:
            ihp_sell_score += 1

    ihp_max_score += 2

    #Round it off to take less space when displaying
    ihp = round(ihp, 3)

    #At some point, we can add percent change. Right now requires to be checked using local old val with new val; REVISIT

    ihp_buy_rec = f'ihp_buy_score:{ihp_buy_score}/{ihp_max_score}'
    ihp_sell_rec = f'ihp_sell_score:{ihp_sell_score}/{ihp_max_score}'

    ihp_signals = f'IHP:{ihp},{ihp_buy_rec},{ihp_sell_rec}'

    return ihp_buy_score, ihp_sell_score, ihp_max_score, ihp_signals
