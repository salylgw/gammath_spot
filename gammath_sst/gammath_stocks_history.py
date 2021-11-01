# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
import yfinance as yf
from datetime import datetime
from pathlib import Path
import sys

#Get summary of past 5 years history
end_date = datetime.today()
start_date = datetime(end_date.year-5, end_date.month, end_date.day)

def get_ticker_history(tsymbol, ticker, path):

    if (len(tsymbol) == 0):
        raise ValueError('Invalid symbol')

    try:
        stock_history = ticker.history(interval='1d', start=start_date, end=end_date, actions=True,auto_adjust=True)
    except:
        raise RuntimeError('Error obtaining stock history')

    print('Stock history dataframe info for ', tsymbol, ':\n')
    stock_history.info()

    stock_history_len = len(stock_history)

    if (stock_history_len > 0):
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        try:
            update_file = True

            #Read old history for comparison (if it exists)
            history_file_exists = (path / f'{tsymbol}_history.csv').exists()

            if (history_file_exists):
                df_old = pd.read_csv(path / f'{tsymbol}_history.csv')
                df_old_len = len(df_old)
                if (stock_history_len < df_old_len):
                    print(f'New stock history is shorter than older stock history for {tsymbol}. old_len: {df_old_len}, new_len: {df_len}. Using older stock history')
                    update_file = False

            if (update_file):
                #Save the history for processing
                stock_history.dropna(how='all').to_csv(path / f'{tsymbol}_history.csv')
            else:
                #Save the new/original history for reference
                stock_history.dropna(how='all').to_csv(path / f'{tsymbol}_history_orig.csv')
        except:
            raise RuntimeError('Stock history file RW error')
    else:
        print(f'\nZero length stock history for {tsymbol}. Aborting for this ticker')
        raise ValueError('Invalid length stock history')

    return
