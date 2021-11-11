# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd

def get_pbr_signals(tsymbol, df_summ):

    pbr_dip_score = 0
    pbr_max_score = 0

    try:
        if (len(df_summ) > 0):
            try:
                pbr = df_summ['priceToBook'][0]
            except:
                raise ValueError('PBR not found')

            if (pbr > 0):
                pbr = round(pbr, 3)

                #Lower PBR is better; Not giving more weight as we have analyst reco and other factors accouting for "selection" criteria
                if (pbr < 20):
                    pbr_dip_score += 1
                else:
                    pbr_dip_score -= 1
        else:
            raise RuntimeError('Dataframe empty')

    except:
        pbr = 0

    pbr_max_score += 1

    pbr_dip_rec = f'pbr_dip_score:{pbr_dip_score}/{pbr_max_score}'

    pbr_signals = f'PBR:{pbr},{pbr_dip_rec}'

    return pbr_dip_score, pbr_max_score, pbr_signals
