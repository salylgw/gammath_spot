# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd

PRICE_PERCENT_CUTOFF = 85

def get_price_signals(df, df_summ):

    prices = df.Close
    prices_len = len(prices)
    if (prices_len <=0):
        return

    lp = prices[prices_len-1]
    lpm1 = prices[prices_len-2]
    lpm2 = prices[prices_len-3]

    price_buy_score = 0
    price_sell_score = 0
    price_max_score = 0

    if ((lp < lpm1) and (lpm1 < lpm2)):
        price_dir = 'falling'
        price_sell_score += 1
        price_buy_score -= 1
    elif ((lp > lpm1) and (lpm1 > lpm2)):
        price_dir = 'rising'
        price_buy_score += 1
        price_sell_score -= 1
    else:
        price_dir = 'direction_unclear'
        price_buy_score = 0
        price_sell_score = 0

    price_max_score += 1

    #Get consecutive falling and rising days count
    last_falling_days_count = 0
    max_falling_days_count = 0
    last_rising_days_count = 0
    max_rising_days_count = 0

    for i in range(prices_len-1):
        if (prices[i] > prices[i+1]):
            last_falling_days_count += 1
            max_rising_days_count = 0
            if (last_falling_days_count > max_falling_days_count):
                max_falling_days_count = last_falling_days_count
        elif (prices[i] < prices[i+1]):
            last_rising_days_count += 1
            last_falling_days_count = 0
            if (last_rising_days_count > max_rising_days_count):
                max_rising_days_count = last_rising_days_count
        else:
            last_falling_days_count = 0
            last_rising_days_count = 0

    #Limit to 3 digits after decimal point
    curr_price = f'curr_price: %5.3f' % lp

    if (last_falling_days_count >= (max_falling_days_count/2)):
        price_buy_score += 1

    if (last_rising_days_count >= (max_rising_days_count/2)):
        price_sell_score += 1

    price_max_score += 1

    yearly_lowest_val = df_summ['fiftyTwoWeekLow'][0]

    if (yearly_lowest_val > 0):
        if (lp <= yearly_lowest_val):
            price_buy_score += 1
            price_sell_score -= 1
        else:
            pct_val = yearly_lowest_val*100/lp

            if (pct_val >= PRICE_PERCENT_CUTOFF):
                price_buy_score += 1
                price_sell_score -= 1

        price_max_score += 1
    else:
        print('\n52-week low value not found')

    yearly_highest_val = df_summ['fiftyTwoWeekHigh'][0]

    if (yearly_highest_val > 0):
        if (lp >= yearly_highest_val):
            price_sell_score += 1
            price_buy_score -= 1
        else:
            pct_val = lp*100/yearly_highest_val

            if (pct_val >= PRICE_PERCENT_CUTOFF):
                price_sell_score += 1
                price_buy_score -= 1

        price_max_score += 1
    else:
        print('\n52-week high value not found')

    fiftyDayAverage = df_summ['fiftyDayAverage'][0]

    if (fiftyDayAverage > 0):
        if (lp <= fiftyDayAverage):
            price_buy_score += 1
        else:
            price_buy_score -= 1

        price_max_score += 1

    twoHundredDayAverage = df_summ['twoHundredDayAverage'][0]

    if (twoHundredDayAverage > 0):
        if (lp <= twoHundredDayAverage):
            price_buy_score += 3

        price_max_score += 3

    price_buy_rec = f'price_buy_score:{price_buy_score}/{price_max_score}'
    price_sell_rec = f'price_sell_score:{price_sell_score}/{price_max_score}'

    if (yearly_lowest_val > 0):
        price_signals = f'price: {price_dir}, cfdc: {last_falling_days_count}, mfdc:{max_falling_days_count},{curr_price},lowest_price:{yearly_lowest_val},{price_buy_rec},{price_sell_rec}'
    else:
        price_signals = f'price: {price_dir}, cfdc: {last_falling_days_count}, mfdc:{max_falling_days_count},{curr_price},{price_buy_rec},{price_sell_rec}'
    
    return price_buy_score, price_sell_score, price_max_score, price_signals
