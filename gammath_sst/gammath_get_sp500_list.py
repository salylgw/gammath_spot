# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from pathlib import Path
import os
import time

sp500_list_url = f'https://en.wikipedia.org/wiki/List_of_S&P_500_companies'

Tickers_dir = Path('./tickers')

def get_sp500_list():

    path = Tickers_dir
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    #Fetch the file only once a day
    dont_need_fetch = True

    try:
        #Get existing file
        file_exists = (path / f'SP500_list.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'SP500_list.csv')
            fct_time = time.ctime(fstat.st_ctime).split(' ')
            dt = time.strftime('%x').split('/')
            if (fct_time[2] == ''):
                fct_date_index = 3
            else:
                fct_date_index = 2

            fct_date = int(fct_time[fct_date_index])
            dt_date = int(dt[1])

            if (fct_date == dt_date):
                print('No need to get new file')
                dont_need_fetch = True
            else:
                print('Date mismatch. Need to fetch new file')
                dont_need_fetch = False
        else:
            #File doesn't exist/
            dont_need_fetch = False
    except:
        print(f'\nError checking SP500 list')

    if (not dont_need_fetch):
        #Get S&P500 list from the internet.
        #Specify header (row to use to make column headers)
        #No need to get entire list of dataframes. We only need first dataframe
        sp500 = pd.read_html(sp500_list_url, header=0)[0]

        print('S&P500 list dataframe info:\n')
        sp500.info()

        #Save the history for reference and processing
        sp500.to_csv(path / f'SP500_list.csv')

    return
