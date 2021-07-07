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

def get_options_signals(ticker, path, curr_price, df_summ):

    options_buy_score = 0
    options_sell_score = 0
    options_max_score = 0
    shortRatio = 0

    #Get current date and time
    current_dt = datetime.now()

    try:
        option_dates = ticker.options

        if (len(option_dates)):
            option_date = option_dates[0]

            #We only need to read options data once a day
            if not (path / f'{ticker.ticker}_call_{option_date}.csv').exists():
                print('\nGetting option chain for ', ticker.ticker)
                #ticker.calendar seems to be too slow. Need to REVISIT
#               events_cal = ticker.calendar

#               print('\nEvents call info for ', ticker.ticker)
#               events_cal.info()
#               if (events_cal is not None):
#                   next_earnings_date = ticker.calendar[0]['Earnings Date']
#                    print('\nNext earnings date for ', ticker.ticker, 'is ', next_earnings_date, 'type is ', type(next_earnings_date))
 #               else:
 #                   print('\nEarnings date not found for ', ticker.ticker)

                print('\nNext options expiry ', ticker.ticker, 'is ', option_date, 'type is ', type(option_date))

                options = ticker.option_chain(option_date)
                options.calls.info()
                options.puts.info()
                print('\nGot option chain for ', ticker.ticker, 'Current price: ', curr_price)

                print('\nSorting calls based on strike price')
                df_calls = options.calls.sort_values('strike')

                #Save the calls sorted by strike price
                df_calls.to_csv(path / f'{ticker.ticker}_call_{option_date}.csv')

                print('\nSorting puts based on strike price')
                df_puts = options.puts.sort_values('strike')

                #Save the puts sorted by strike price
                df_puts.to_csv(path / f'{ticker.ticker}_put_{option_date}.csv')

                print('\nSaved call and put data')
            else:
                print('\nOption chain for ', ticker.ticker, ' exists. Reading from files')
                #Get the data from existing file
                df_calls = pd.read_csv(path / f'{ticker.ticker}_call_{option_date}.csv')
                df_puts = pd.read_csv(path / f'{ticker.ticker}_put_{option_date}.csv')
                print('\nRead call and put data')


            call_opts_size = len(df_calls)
            put_opts_size = len(df_puts)

            print('\nCalls size: ', call_opts_size)
            print('\nPuts size: ', put_opts_size)

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
                print('\nbullish')
                options_buy_score += 1
                options_sell_score -= 1
            else:
                print('\nbearish')
                options_buy_score -= 1
                options_sell_score += 1

            options_max_score += 1

            shortRatio = df_summ['shortRatio'][0]
            if (shortRatio > 0):
                if (shortRatio < 3):
                    options_buy_score += 1

                if (shortRatio > 5):
                    options_buy_score -= 1
                    options_sell_score += 1

                if (shortRatio > 10):
                    options_buy_score -= 2
                    options_sell_score += 2

                #Setting it disproportionately high to have a screaming signal
                if (shortRatio > 15):
                    options_buy_score -= 100
                    options_sell_score += 100

                options_max_score += 1

    except:
        print('\nOptions not supported for ticker: ', ticker.ticker)


    options_buy_rec = f'options_buy_score:{options_buy_score}/{options_max_score}'
    options_sell_rec = f'options_sell_score:{options_sell_score}/{options_max_score}'
    options_signals = f'options: {options_buy_rec},{options_sell_rec},short_ratio:{shortRatio}'
    
    return options_buy_score, options_sell_score, options_max_score, options_signals

