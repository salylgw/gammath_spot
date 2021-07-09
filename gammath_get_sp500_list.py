# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from pathlib import Path

sp500_list_url = f'https://en.wikipedia.org/wiki/List_of_S&P_500_companies'

Tickers_dir = Path('tickers')

def get_sp500_list():

    #Get S&P500 list.
    #Specify header and get first dataframe
    sp500 = pd.read_html(sp500_list_url, header=0)[0]

    print('S&P500 list dataframe info:\n')
    sp500.info()

    path = Tickers_dir
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    #Save the history for reference and processing
    sp500.to_csv(path / f'SP500_list.csv')

    return sp500

if __name__ == "__main__":
    get_sp500_list()
