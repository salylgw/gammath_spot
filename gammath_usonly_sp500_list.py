# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from pathlib import Path
import gammath_get_sp500_list as gspl

sp500_list_url = f'https://en.wikipedia.org/wiki/List_of_S&P_500_companies'

Tickers_dir = Path('tickers')

#List US states and DC
US_States = ('Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'D.C.', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming')

def get_usonly_sp500_list():

    path = Tickers_dir
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    try:
        #Save the history for reference and processing
        sp500 = pd.read_csv(path / f'SP500_list.csv')
    except:
        #Get S&P500 list.
        sp500 = gspl.get_sp500_list()

    return

if __name__ == "__main__":
    get_sp500_list()
