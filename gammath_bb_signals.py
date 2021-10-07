# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from talib import BBANDS
import numpy as np
#import random

BBANDS_TIME_PERIOD = 14

def get_bollinger_bands_signals(tsymbol, df, path):

    ub, mb, lb = BBANDS(df.Close, timeperiod=BBANDS_TIME_PERIOD, nbdevup=2, nbdevdn=2, matype=0)
    bb_len = len(ub)
    if (bb_len<=0):
        return

    last_val_mb = mb[bb_len-1]
    last_val_ub = ub[bb_len-1]
    last_val_lb = lb[bb_len-1]

    bb_buy_score = 0
    bb_sell_score = 0
    bb_max_score = 0

    #Get the most recent price from dataframe
    lp = df['Close'][bb_len-1]

    if (lp < last_val_mb):

        bb_avg = 'below average'

        if ((last_val_mb - lp) < (abs(lp - last_val_lb))):
            bb_vicinity = 'near middle band'
            bb_buy_score += 2
            bb_sell_score -= 2
        else:
            #Higher buy weights when near lower band
            bb_vicinity = 'near lower band'
            bb_buy_score += 6
            bb_sell_score -= 6

    elif (lp > last_val_mb):

        bb_avg = 'above average'

        if ((lp - last_val_mb) < (abs(last_val_ub - lp))):
            bb_vicinity = 'near middle band'
            bb_sell_score += 2
            bb_buy_score -= 2
        else:
            #Higher sell weights when near upper band
            bb_vicinity = 'near upper band'
            bb_sell_score += 6
            bb_buy_score -= 6
    else:
        bb_avg = 'average'
        bb_vicinity = 'at middle band'
        bb_buy_score += 1
        bb_sell_score -= 1

    bb_max_score += 6

    bb_buy_rec = f'bb_buy_score:{bb_buy_score}/{bb_max_score}'
    bb_sell_rec = f'bb_sell_score:{bb_sell_score}/{bb_max_score}'
    bb_signals = f'bollinger bands:{bb_avg},{bb_vicinity},{bb_buy_rec},{bb_sell_rec}'

    #Experimental: Using bollinger bands to compute price sigmoid based on LB, MB, UB comparisons
    #This method isn't the best but will be used for comparison
    prices = df.Close
    prices_len = len(prices)
    if (prices_len != bb_len):
        print('\nMismatch in prices and bollinger bands data length')
    else:

        bb_prices_sigmoid = pd.DataFrame(columns=['Sigmoid'], index=range(prices_len))
    
        for i in range(prices_len):

            c_price = prices[i]
            c_ub = ub[i]
            c_mb = mb[i]
            c_lb = lb[i]
            if (c_price < c_mb):

                #below average; Set it to 1
                bb_prices_sigmoid['Sigmoid'][i] = 1
#                if ((c_mb - c_price) < (abs(c_price - c_lb))):
                    #near middle band
#                    bb_prices_sigmoid['Sigmoid'][i] = 0 #random.randint(0, 1)
#                else:
                    #near lower band
#                    bb_prices_sigmoid['Sigmoid'][i] = 1

            elif (c_price > c_mb):
                #above average; Set it to 0
                bb_prices_sigmoid['Sigmoid'][i] = 0

#                if ((c_price - c_mb) < (abs(c_ub - c_price))):
                    #near middle band
#                    bb_prices_sigmoid['Sigmoid'][i] = 0 #random.randint(0, 1)
#                else:
                    #near upper band
#                    bb_prices_sigmoid['Sigmoid'][i] = 1
            else:
                #average; Set it to 0
                bb_prices_sigmoid['Sigmoid'][i] = 0
#                bb_prices_sigmoid['Sigmoid'][i] = random.randint(0, 1)


        #Save for later usage
        bb_prices_sigmoid.to_csv(path / f'{tsymbol}_bbp_sigmoid.csv')

    return ub, mb, lb, bb_buy_score, bb_sell_score, bb_max_score, bb_signals
