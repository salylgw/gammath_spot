# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd

TRILLION_DOLLAR_MCAP = 1000000000000
BILLION_DOLLAR_MCAP = 1000000000
FIFTY_MILLION_DOLLAR_MCAP = 50000000

def get_mktcap_signals(tsymbol, df_summ):

    print(f'\nGetting Market Cap signals for {tsymbol}')

    mktcap_buy_score = 0
    mktcap_sell_score = 0
    mktcap_max_score = 0

    mktcap = df_summ['marketCap'][0]

    print('\nmktcap for ', tsymbol, ': ', mktcap)

    if (mktcap < FIFTY_MILLION_DOLLAR_MCAP):
        mktcap_sell_score += 4
        mktcap_buy_score -= 4
    else:

        mktcap_buy_score += 1

        if (mktcap >= BILLION_DOLLAR_MCAP):
            mktcap_buy_score += 1

        if (mktcap >= TRILLION_DOLLAR_MCAP):
            mktcap_buy_score += 2

    mktcap_max_score += 4

    mktcap_buy_rec = f'mktcap_buy_score:{mktcap_buy_score}/{mktcap_max_score}'
    mktcap_sell_rec = f'mktcap_sell_score:{mktcap_sell_score}/{mktcap_max_score}'

    mktcap_signals = f'mktcap:{mktcap},{mktcap_buy_rec},{mktcap_sell_rec}'

    return mktcap_buy_score, mktcap_sell_score, mktcap_max_score, mktcap_signals
