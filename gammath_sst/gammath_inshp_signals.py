# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd

def get_inshp_signals(tsymbol, df_summ):

    print(f'\nGetting Insider holdings percentage signals for {tsymbol}')

    inshp_dip_score = 0
    inshp_max_score = 0

    try:
        inshp = df_summ['heldPercentInsiders'][0]
    except:
        raise ValueError('heldPercentInsiders not found')

    print('inshp for ', tsymbol, ': ', inshp)

    if (inshp > 0):
        inshp_dip_score += 1
    else:
        inshp_dip_score -= 1

    inshp_max_score += 1

    #Round it off to take less space displaying the value
    inshp = round(inshp, 3)

    #At some point, we can add percent change. Right now requires to be checked using local old val with new val; REVISIT

    inshp_dip_rec = f'inshp_dip_score:{inshp_dip_score}/{inshp_max_score}'

    inshp_signals = f'inshp:{inshp},{inshp_dip_rec}'

    return inshp_dip_score, inshp_max_score, inshp_signals
