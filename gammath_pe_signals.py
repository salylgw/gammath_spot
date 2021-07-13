# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd

def get_pe_signals(df, df_summ):

    pe_buy_score = 0
    pe_sell_score = 0
    pe_max_score = 0

    pe_buy_rec = f'pe_buy_score:{pe_buy_score}/{pe_max_score}'
    pe_sell_rec = f'pe_sell_score:{pe_sell_score}/{pe_max_score}'

    pe_signals = ''
    
    return pe_buy_score, pe_sell_score, pe_max_score, pe_signals
