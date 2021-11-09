# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd

def get_beta_signals(tsymbol, df_summ):

    print(f'\nGetting beta signals for {tsymbol}')

    beta_dip_score = 0
    beta_max_score = 0

    try:
        #Get the beta value from summary DF
        beta = df_summ['beta'][0]
    except:
        raise ValueError('Beta value not found')

    print('Beta for ', tsymbol, ': ', beta)

    if (beta > 0):
        #Closer to 1 is near market and is better
        if (beta < 2):
            beta_dip_score += 1
        else:
            beta_dip_score -= 1

    beta_max_score += 1

    #round it off for taking less space when displaying
    beta = round(beta, 3)

    beta_dip_rec = f'beta_dip_score:{beta_dip_score}/{beta_max_score}'

    beta_signals = f'BETA:{beta},{beta_dip_rec}'

    return beta_dip_score, beta_max_score, beta_signals
