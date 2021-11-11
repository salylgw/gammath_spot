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

    ihp_dip_score = 0
    ihp_max_score = 0

    try:
        #Get data about percentage held from summary dataframe
        ihp = df_summ['heldPercentInstitutions'][0]
    except:
        raise ValueError('heldPercentInstitutions value not found')

    #We can do checks for different levels but for now this will suffice
    if (ihp > 0):
        if (ihp > 0.7):
            ihp_dip_score += 1
        else:
            ihp_dip_score -= 1

    ihp_max_score += 1

    #Round it off to take less space when displaying
    ihp = round(ihp, 3)

    #At some point, we can add percent change. Right now requires to be checked using local old val with new val; REVISIT

    ihp_dip_rec = f'ihp_dip_score:{ihp_dip_score}/{ihp_max_score}'

    ihp_signals = f'IHP:{ihp},{ihp_dip_rec}'

    return ihp_dip_score, ihp_max_score, ihp_signals
