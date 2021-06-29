# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import yfinance as yf
from pathlib import Path

def get_options_signals(ticker, path):

    options_buy_score = 0
    options_sell_score = 0
    options_max_score = 0

    try:
        option_dates = ticker.options
        if (len(option_dates)):
            option_date = option_dates[0]
            options = ticker.option_chain(option_date)
            options.calls.info()
            options.puts.info()
            options.calls.dropna().sort_values('openInterest').to_csv(path / f'{ticker.ticker}_call_{option_date}.csv')
            options.puts.dropna().sort_values('openInterest').to_csv(path / f'{ticker.ticker}_put_{option_date}.csv')
            total_open_calls = options.calls['openInterest'].sum()
            total_open_puts = options.puts['openInterest'].sum()

            bc_ratio = round((total_open_calls / total_open_puts),3)
            if (bc_ratio > 1):
                options_buy_score += 1
                options_sell_score -= 1
            else:
                options_buy_score -= 1
                options_sell_score += 1

            options_max_score += 1

    except:
        print('\nOptions not supported for ticker: ', ticker.ticker)


    options_buy_rec = f'options_buy_score:{options_buy_score}/{options_max_score}'
    options_sell_rec = f'options_sell_score:{options_sell_score}/{options_max_score}'
    options_signals = f'options: {options_buy_rec},{options_sell_rec}'
    
    return options_buy_score, options_sell_score, options_max_score, options_signals

