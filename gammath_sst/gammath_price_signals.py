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

def get_price_signals(df, df_summ):

    prices = df.Close
    prices_len = len(prices)
    if (prices_len <=0):
        return

    #Get current price from summary
    one_off_curr_price = df_summ['currentPrice'][0]
    val_type = type(one_off_curr_price)
    print(f'\nOne off curr price: {one_off_curr_price}, type:{val_type}')

    #Looks like price history is stale so get current price from summary
#    if (one_off_curr_price > 0):
#        lp = one_off_curr_price
#    else:
#        lp = prices[prices_len-1]

    lp = prices[prices_len-1]

    #Limit to 3 digits after decimal point
    curr_price = f'curr_price: %5.3f' % lp

    lpm1 = prices[prices_len-2]
    lpm2 = prices[prices_len-3]

    price_buy_score = 0
    price_sell_score = 0
    price_max_score = 0
    nftwl = ''

    if ((lp < lpm1) and (lpm1 < lpm2)):
        price_dir = 'falling'
        price_sell_score += 2
        price_buy_score -= 2
    elif ((lp > lpm1) and (lpm1 > lpm2)):
        price_dir = 'rising'
        price_buy_score += 2
        price_sell_score -= 2
    else:
        price_dir = 'direction_unclear'
        price_buy_score = 1
        price_sell_score = 1

    price_max_score += 2

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

    if (last_falling_days_count > fp_bp):
        price_buy_score += 1
        price_sell_score -= 1
    else:
        price_buy_score -= 1
        price_sell_score += 1

    if (last_rising_days_count > rp_bp):
        price_sell_score += 1
        price_buy_score -= 1
    else:
        price_buy_score += 1
        price_sell_score -= 1

    price_max_score += 1

    if (last_falling_days_count > fp_mp):
        price_buy_score += 2

    if (last_rising_days_count > rp_mp):
        price_sell_score += 2

    price_max_score += 2

    if (last_falling_days_count > fp_tp):
        price_buy_score += 3

    if (last_rising_days_count > rp_tp):
        price_sell_score += 3

    price_max_score += 3

    yearly_lowest_val = df_summ['fiftyTwoWeekLow'][0]

    if (yearly_lowest_val > 0):
        if (lp <= yearly_lowest_val):
            #Isolated case to bring it to the front for checkout
            price_buy_score += 30
            price_sell_score -= 30
            nftwl = 'new fiftyTwoWeekLow'
            price_max_score += 30
        else:
            pct_val = yearly_lowest_val*100/lp

            if (pct_val >= PRICE_PERCENT_CUTOFF):
                price_buy_score += 1
                price_sell_score -= 1
            else:
                price_buy_score -= 1
                price_sell_score += 1

            price_max_score += 1

    else:
        print('\n52-week low value not found')

    yearly_highest_val = df_summ['fiftyTwoWeekHigh'][0]

    if (yearly_highest_val > 0):
        if (lp >= yearly_highest_val):
            #Isolated case to bring it to the front for checkout
            price_sell_score += 30
            price_buy_score -= 30
            price_max_score += 30
        else:
            pct_val = lp*100/yearly_highest_val

            if (pct_val >= PRICE_PERCENT_CUTOFF):
                price_sell_score += 1
                price_buy_score -= 1
            else:
                price_buy_score += 1
                price_sell_score -= 1

            price_max_score += 1
    else:
        print('\n52-week high value not found')

    fiftyDayAverage = df_summ['fiftyDayAverage'][0]

    if (fiftyDayAverage > 0):
        if (lp <= fiftyDayAverage):
            price_buy_score += 2
            price_sell_score -= 2
        else:
            price_buy_score -= 2
            price_sell_score += 2

    price_max_score += 2

    twoHundredDayAverage = df_summ['twoHundredDayAverage'][0]

    if (twoHundredDayAverage > 0):
        if (lp <= twoHundredDayAverage):
            price_buy_score += 3
            price_sell_score -= 3

    price_max_score += 3

    one_year_prices = df['Close'][(prices_len-AVG_TRADING_DAYS_PER_YEAR):]
    bp, mp, tp = one_year_prices.quantile([0.25, 0.5, 0.75])

    bp = round(bp, 3)
    mp = round(mp, 3)
    tp = round(tp, 3)

    if ((lp <= bp) or (lp >= tp)):
        if (lp <= bp):
            price_buy_score += 3
            price_sell_score -= 3
        elif (lp >= tp):
            price_buy_score -= 3
            price_sell_score += 3
    else:
        if ((lp > bp) and (lp < mp)):
            price_buy_score += 2
            price_sell_score -= 2

        if ((lp > mp) and (lp < tp)):
            price_buy_score += 1
            price_sell_score -= 1

    price_max_score += 3

    price_buy_rec = f'price_buy_score:{price_buy_score}/{price_max_score}'
    price_sell_rec = f'price_sell_score:{price_sell_score}/{price_max_score}'

    if (yearly_lowest_val > 0):
        price_signals = f'price: {price_dir}, cfdc: {last_falling_days_count}, fp_bp:{fp_bp},fp_mp:{fp_mp},fp_tp:{fp_tp},mfdc:{max_falling_days_count},{curr_price},lowest_price:{yearly_lowest_val},bp:{bp},mp:{mp},tp:{tp},{price_buy_rec},{price_sell_rec},{nftwl}'
    else:
        price_signals = f'price: {price_dir}, cfdc: {last_falling_days_count}, rp_bp:{rp_bp},rp_mp:{rp_mp},rp_tp:{rp_tp},mrdc:{max_rising_days_count},{curr_price},bp:{bp},mp:{mp},tp:{tp},{price_buy_rec},{price_sell_rec},{nftwl}'
    
    return price_buy_score, price_sell_score, price_max_score, price_signals
