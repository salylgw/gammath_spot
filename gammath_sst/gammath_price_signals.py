# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
import numpy as np

AVG_TRADING_DAYS_PER_YEAR = 252
PRICE_PERCENT_CUTOFF = 85

def get_price_signals(tsymbol, df, df_summ):

    print(f'\nGetting Price signals for {tsymbol}')

    price_buy_score = 0
    price_sell_score = 0
    price_max_score = 0
    price_signals = ''

    prices = df.Close
    prices_len = len(prices)
    if (prices_len <= 0):
        print(f'\nError: Incorrect length of Price dataframe for {tsymbol}')
        raise ValueError('Invalid Price data for generating signals')

    lp = prices[prices_len-1]

    #Limit to 3 digits after decimal point
    curr_price = f'curr_price: %5.3f' % lp

    lpm1 = prices[prices_len-2]
    lpm2 = prices[prices_len-3]

    nftwlh = ''

    #No score on this; Just log it to make a decision on buy/sell by seeing falling/rising in signals data
    if ((lp < lpm1) and (lpm1 < lpm2)):
        price_dir = 'falling'
    elif ((lp > lpm1) and (lpm1 > lpm2)):
        price_dir = 'rising'
    else:
        price_dir = 'direction_unclear'

    #Get consecutive falling and rising days count
    last_falling_days_count = 0
    max_falling_days_count = 0
    last_rising_days_count = 0
    max_rising_days_count = 0

    price_consec_falling_days_count_series = pd.Series(np.nan, pd.RangeIndex(prices_len))
    price_consec_falling_days_count_index = 0

    price_consec_rising_days_count_series = pd.Series(np.nan, pd.RangeIndex(prices_len))
    price_consec_rising_days_count_index = 0

    for i in range(prices_len-1):
        if (prices[i] > prices[i+1]):
            last_falling_days_count += 1

            if (last_rising_days_count > 0):
                price_consec_rising_days_count_index += 1

            last_rising_days_count = 0

            price_consec_falling_days_count_series[price_consec_falling_days_count_index] = last_falling_days_count

            if (last_falling_days_count > max_falling_days_count):
                max_falling_days_count = last_falling_days_count
        elif (prices[i] < prices[i+1]):
            last_rising_days_count += 1

            if (last_falling_days_count > 0):
                price_consec_falling_days_count_index += 1

            last_falling_days_count = 0

            price_consec_rising_days_count_series[price_consec_rising_days_count_index] = last_rising_days_count

            if (last_rising_days_count > max_rising_days_count):
                max_rising_days_count = last_rising_days_count
        else:
            last_falling_days_count = 0
            last_rising_days_count = 0

    price_consec_falling_days_count_series = price_consec_falling_days_count_series.dropna()

    #Lower counts will be too many so drop them to get approx percentile past lower numbers
    price_consec_falling_days_count_series = price_consec_falling_days_count_series.drop_duplicates()
    price_consec_falling_days_count_series = price_consec_falling_days_count_series.sort_values()

    price_consec_rising_days_count_series = price_consec_rising_days_count_series.dropna()

    #Lower counts will be too many so drop them to get approx percentile past lower numbers
    price_consec_rising_days_count_series = price_consec_rising_days_count_series.drop_duplicates()
    price_consec_rising_days_count_series = price_consec_rising_days_count_series.sort_values()

    #Get percentile values
    fp_bp, fp_mp, fp_tp = price_consec_falling_days_count_series.quantile([0.25, 0.5, 0.75])

    fp_bp = round(fp_bp, 3)
    fp_mp = round(fp_mp, 3)
    fp_tp = round(fp_tp, 3)

    rp_bp, rp_mp, rp_tp = price_consec_rising_days_count_series.quantile([0.25, 0.5, 0.75])

    rp_bp = round(rp_bp, 3)
    rp_mp = round(rp_mp, 3)
    rp_tp = round(rp_tp, 3)

    try:
        #50-day average
        fiftyDayAverage = df_summ['fiftyDayAverage'][0]
    except:
        print(f'\n50-day average value not found for {tsymbol}')
        fiftyDayAverage = 0

    try:
        #200-day average
        twoHundredDayAverage = df_summ['twoHundredDayAverage'][0]
    except:
        print(f'\n200-day average value not found for {tsymbol}')
        twoHundredDayAverage = 0

    try:
        #52-week low
        yearly_lowest_val = df_summ['fiftyTwoWeekLow'][0]
    except:
        print(f'\52-week low value not found for {tsymbol}')
        yearly_lowest_val = 0

    try:
        #52-week high
        yearly_highest_val = df_summ['fiftyTwoWeekHigh'][0]
    except:
        print(f'\52-week high value not found for {tsymbol}')
        yearly_highest_val = 0

    if (yearly_lowest_val > 0):
        if (lp <= yearly_lowest_val):
            #New 52-week low; Log it for information
            nftwlh = 'new fiftyTwoWeekLow'
    else:
        print('\n52-week low value not found')

    if (yearly_highest_val <= 0):
        #New 52-week high; Log it for information
        print('\n52-week high value not found')
        nftwlh = 'new fiftyTwoWeekHigh'

    if (last_falling_days_count > 0):
        price_buy_score -= 1
        price_sell_score += 1

        if (last_falling_days_count >= fp_bp):
            price_buy_score -= 2
            price_sell_score += 2

        #Checkout price wrt 50-day average, 200-day average and 52-week low
        if (fiftyDayAverage > 0):
            if (lp > fiftyDayAverage):
                price_sell_score += 1

        if (twoHundredDayAverage > 0):
            if (lp > twoHundredDayAverage):
                price_sell_score += 1

        if (yearly_highest_val > 0):
            pct_val = lp*100/yearly_highest_val

            #If we are closer to 52-week high then increase the sell score; else increase the buy score
            if (pct_val >= PRICE_PERCENT_CUTOFF):
                price_sell_score += 3
    elif (last_rising_days_count > 0):
        price_buy_score += 1
        price_sell_score -= 1
        if (last_rising_days_count <= rp_bp):
            price_buy_score += 2
            price_sell_score -= 2

        #Checkout price wrt 50-day average, 200-day average and 52-week low
        if (fiftyDayAverage > 0):
            if (lp <= fiftyDayAverage):
                price_buy_score += 1

        if (twoHundredDayAverage > 0):
            if (lp <= twoHundredDayAverage):
                price_buy_score += 1

        if (yearly_lowest_val > 0):
            pct_val = yearly_lowest_val*100/lp

            #If current price is not too far from 52-week low then increase buy score
            if (pct_val >= PRICE_PERCENT_CUTOFF):
                price_buy_score += 3


    price_max_score += 8

    #Get percentiles for 52-week prices
    one_year_prices = df['Close'][(prices_len-AVG_TRADING_DAYS_PER_YEAR):]
    bp, mp, tp = one_year_prices.quantile([0.25, 0.5, 0.75])

    bp = round(bp, 3)
    mp = round(mp, 3)
    tp = round(tp, 3)

    #If price is in lower percentile then higher buy score
    #If price is in higher percentile the higher sell score
    if ((lp <= bp) or (lp >= tp)):
        if (lp <= bp):
            price_buy_score += 2
        elif (lp >= tp):
            price_sell_score += 2
    else:
        if ((lp > bp) and (lp < mp)):
            price_buy_score += 1
        elif ((lp > mp) and (lp < tp)):
            #Either buy/sell depending on overall score
            price_buy_score += 1
            price_sell_score += 1

    price_max_score += 2

    price_buy_rec = f'price_buy_score:{price_buy_score}/{price_max_score}'
    price_sell_rec = f'price_sell_score:{price_sell_score}/{price_max_score}'

    if (yearly_lowest_val > 0):
        price_signals = f'price: {price_dir}, cfdc: {last_falling_days_count}, fp_bp:{fp_bp},fp_mp:{fp_mp},fp_tp:{fp_tp},mfdc:{max_falling_days_count},{curr_price},lowest_price:{yearly_lowest_val},bp:{bp},mp:{mp},tp:{tp},{price_buy_rec},{price_sell_rec},{nftwlh}'
    else:
        price_signals = f'price: {price_dir}, cfdc: {last_falling_days_count}, rp_bp:{rp_bp},rp_mp:{rp_mp},rp_tp:{rp_tp},mrdc:{max_rising_days_count},{curr_price},bp:{bp},mp:{mp},tp:{tp},{price_buy_rec},{price_sell_rec},{nftwlh}'
    
    return price_buy_score, price_sell_score, price_max_score, price_signals
