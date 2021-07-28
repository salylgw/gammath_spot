# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd

def get_pbr_signals(tsymbol, df_summ):

    print('\nGetting PBR signals')
    pbr_buy_score = 0
    pbr_sell_score = 0
    pbr_max_score = 0

    try:
        if (len(df_summ) > 0):
            pbr = df_summ['priceToBook'][0]
            if (pbr > 0):
                pbr = round(pbr, 3)

                print('PBR ratio for ', tsymbol, ': ', pbr)

                if (pbr < 40):
                    pbr_buy_score += 1
                    if (pbr < 15):
                        pbr_buy_score += 1
                else:
                    #Reduce/Increase buy/sell score significantly to impact overall score
                    pbr_buy_score -= 10
                    pbr_sell_score += 10

                pbr_max_score += 2
    except:
        pbr = 0
        print(f'\nPBR value not found for {tsymbol}')

    pbr_buy_rec = f'pbr_buy_score:{pbr_buy_score}/{pbr_max_score}'
    pbr_sell_rec = f'pbr_sell_score:{pbr_sell_score}/{pbr_max_score}'

    pbr_signals = f'PBR:{pbr},{pbr_buy_rec},{pbr_sell_rec}'

    print(f'\nPBR signals extracted for {tsymbol}')
    return pbr_buy_score, pbr_sell_score, pbr_max_score, pbr_signals
