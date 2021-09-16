# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import yfinance as yf
from pathlib import Path
import bisect
from datetime import datetime
import pandas as pd
import time
import os

def get_options_signals(tsymbol, path, curr_price, df_summ):

    options_buy_score = 0
    options_sell_score = 0
    options_max_score = 0
    shortRatio = 0

    print(f'\nGetting options signals for {tsymbol}')
    #Get the options data from existing file
    if ((path / f'{tsymbol}_options_dates.csv').exists()):
        print(f'\nGet options dates for {tsymbol}')
        #Get the latest options expiry date
        dates_df = pd.read_csv(path / f'{tsymbol}_options_dates.csv', index_col='Unnamed: 0')

        option_date = dates_df.loc[0][0]

        print(f'\nTop option date for {tsymbol} is {option_date}')
        df_calls = pd.read_csv(path / f'{tsymbol}_call_{option_date}.csv')
        df_puts = pd.read_csv(path / f'{tsymbol}_put_{option_date}.csv')
        print('\nRead call and put data')

        #Get current date and time
        current_dt = datetime.now()

        try:
            call_opts_size = len(df_calls)
            put_opts_size = len(df_puts)

            print('\nCalls size: ', call_opts_size)
            print('\nPuts size: ', put_opts_size)

            if ((call_opts_size != 0) and (put_opts_size != 0)):
                print('\nFind index of call strike price closest to current price')

                #Get index for current price call options
                i = bisect.bisect_right(df_calls['strike'], curr_price)

                if (i < (call_opts_size-1)):
                    print('\nFound the strike for current price of ', curr_price, 'in call option chain')
                    bullish_start_index = i
                else:
                    bullish_start_index = 0

                print('\nbullish start index: ', bullish_start_index)

                print('\nFind index of put strike price closest to current price')

                #Get index for current price put options
                i = bisect.bisect_right(df_puts['strike'], curr_price)

                if (i < (put_opts_size-1)):
                    print('\nFound the strike for current price of ', curr_price, 'in put option chain')
                    bearish_end_index = i
                else:
                    bearish_end_index = 0

                print('\nbearish end index: ', bearish_end_index)

                #Get total call open interest for curr price and higher
                total_bullish_open_interest = df_calls['openInterest'][bullish_start_index:call_opts_size-1].sum()

                #Get total put open interest for curr price and lower
                total_bearish_open_intetest = df_puts['openInterest'][0:bearish_end_index].sum()

                print('\nopen interests: bullish: ', total_bullish_open_interest, 'bearish: ', total_bearish_open_intetest)

                if (total_bearish_open_intetest > 0):
                    bc_ratio = round((total_bullish_open_interest / total_bearish_open_intetest),3)
                else:
                    bc_ratio = 0

                if (bc_ratio > 1):
                    print(f'\nbullish signal for {tsymbol}')
                    options_buy_score += 3
                    options_sell_score -= 3
                else:
                    print(f'\nbearish signal for {tsymbol}')
                    options_buy_score -= 3
                    options_sell_score += 3

                options_max_score += 3

                #Use short ratio to read the bullish/bearish trend
                #Add weightage for buy/sell scores
                shortRatio = df_summ['shortRatio'][0]
                if (shortRatio > 0):
                    if (shortRatio < 3):
                        options_buy_score += 12
                        options_sell_score -= 12
                    elif (shortRatio < 6):
                        options_buy_score += 3
                        options_sell_score -= 3
                    else:
                        if (shortRatio > 15):
                            options_buy_score -= 12
                            options_sell_score += 12
                        elif (shortRatio > 10):
                            options_buy_score -= 3
                            options_sell_score += 3

                    options_max_score += 12
                else:
                    #Put some -ve weight for lack of info
                    options_buy_score -= 2
                    options_sell_score += 2
                    options_max_score += 2

            else:
                print('\nOptions not supported for ', tsymbol)

        except:
            print('\nError while processing options data for ', tsymbol)


    options_buy_rec = f'options_buy_score:{options_buy_score}/{options_max_score}'
    options_sell_rec = f'options_sell_score:{options_sell_score}/{options_max_score}'
    options_signals = f'options: {options_buy_rec},{options_sell_rec},short_ratio:{shortRatio}'
    
    return options_buy_score, options_sell_score, options_max_score, options_signals

