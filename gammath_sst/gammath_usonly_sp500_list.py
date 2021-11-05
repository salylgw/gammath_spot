# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from pathlib import Path
import gammath_get_sp500_list as gspl
import re


def get_usonly_sp500_list():

    print(f'\nGetting SP500 list of US companies.')

    sp500_list_url = f'https://en.wikipedia.org/wiki/List_of_S&P_500_companies'

    CURR_DIR = Path('.')
    Tickers_dir = Path('./tickers')

    #List US states and DC
    US_States = ('Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'D.C.', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming')

    path = CURR_DIR

    try:
        #Save the history for reference and processing
        sp500 = pd.read_csv(path / f'SP500_list.csv')
    except:
        #Get S&P500 list.
        sp500 = gspl.get_sp500_list()

    path = Tickers_dir

    pattern_for_state = re.compile(r'([A-Z]*[a-z]*[\s]*[A-Z]*[a-z]*),[\s]*([A-Z]*[a-z]*[\s]*[A-Z]*[a-z]*)')

    i = 0
    for symbol in sp500['Symbol']:
        if not (path / f'{symbol}/{symbol}_summary.csv').exists():
            print(f'File {symbol}/{symbol}_summary.csv does not exist')
        else:
            st_info = pd.read_csv(path / f'{symbol}/{symbol}_summary.csv')
            val_does_not_exist = st_info['country'].isna()
            if (val_does_not_exist[0]):
                hq_loc = sp500['Headquarters Location'][i]
                matched_string = pattern_for_state.search(hq_loc)
                if (matched_string):
                    city, state = matched_string.groups()
                    if (state in US_States):
                        print(f'{symbol} is US company')
                        country = 'United States'
                    else:
                        print(f'{symbol} is not US company')
                        country = 'Not US'
            else:
                country = st_info['country'][0]

            if (country != 'United States'):
                print(f'{symbol} is not US company')
                sp500 = sp500.drop([i])

        i += 1

    sp500.to_csv('SP500_US_ONLY.csv', index=False)

    return

if __name__ == "__main__":
    get_usonly_sp500_list()
