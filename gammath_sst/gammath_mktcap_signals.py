# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd


def get_mktcap_signals(tsymbol, df_summ):

    TRILLION_DOLLAR_MCAP = 1000000000000

    mktcap_buy_score = 0
    mktcap_sell_score = 0
    mktcap_max_score = 0

    mktcap = df_summ['marketCap'][0]

    #Just give an extra point to trillion dollar companies
    #When we add more weight for marketcap, we can add buy/sell scores this in levels from market cap in millions to trillions
    if (mktcap >= TRILLION_DOLLAR_MCAP):
        mktcap_buy_score += 1

    mktcap_max_score += 1

    mktcap_buy_rec = f'mktcap_buy_score:{mktcap_buy_score}/{mktcap_max_score}'
    mktcap_sell_rec = f'mktcap_sell_score:{mktcap_sell_score}/{mktcap_max_score}'

    mktcap_signals = f'mktcap:{mktcap},{mktcap_buy_rec},{mktcap_sell_rec}'

    return mktcap_buy_score, mktcap_sell_score, mktcap_max_score, mktcap_signals
