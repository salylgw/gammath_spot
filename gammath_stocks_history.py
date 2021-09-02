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
        return None

    try:
        stock_history = ticker.history(interval='1d', start=start_date, end=end_date, actions=True,auto_adjust=True)

        print('Stock history dataframe info for ', tsymbol, ':\n')
        stock_history.info()

        stock_history_len = len(stock_history)
        print(f'\nLength of stock history for {tsymbol} is {stock_history_len}')
        if (stock_history_len > 0):
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)

            #Save the history for reference and processing
            stock_history.dropna(how='all').to_csv(path / f'{tsymbol}_history_orig.csv')

            try:
                #Read CSV into DataFrame. Stock_history dataframe seems to filter out dates
                df = pd.read_csv(path / f'{tsymbol}_history_orig.csv')
                print('DataFrame info read from CSV for symbol: ', tsymbol, ':\n')
                df.info()
                df_len = len(df)
                print('Getting last date for stock history')
                last_date = df['Date'][df_len-1]
                last_date_string = f'{last_date}'
                last_date_array = last_date_string.split('-')
                if (end_date.day != int(last_date_array[2])):
                    print('Stock history is stale for ', tsymbol)
                    try:
                        #Read Stock summary info into DataFrame.
                        df_summ = pd.read_csv(path / f'{tsymbol}_summary.csv')
                        print('DataFrame info read from CSV for symbol: ', tsymbol, ':\n')
                        df_summ.info()
                    except:
                        print('\nStock summary file not found for symbol ', tsymbol)
                        df_summ = pd.DataFrame()

                    #Stale prices. Fetch market price from info and save it in history
                    curr_price = df_summ['currentPrice'][0]
                    if (curr_price > 0):
                        #REVISIT: Temp workaround for stale data issue
                        df.loc[(df_len-1), 'Close'] = curr_price
                        val = round(curr_price, 3)
                        print(f'\nStale prices for {tsymbol}. Using price from today of {val}')
                else:
                    print('\nStock history is latest for ', tsymbol)
                df.to_csv(path / f'{tsymbol}_history.csv')
            except:
                print('\nStock history file not found for ', tsymbol)
                df = pd.DataFrame()
        else:
            print(f'\nZero length stock history for {tsymbol}. Aborting for this ticker')
            return None
    except:
        print('\nError getting stock history ', tsymbol, ': ', sys.exc_info()[0])
        return None

    return path, ticker
