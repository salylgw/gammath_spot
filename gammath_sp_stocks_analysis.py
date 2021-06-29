# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import sys
import time
import gammath_stocks_analysis as st_ha

if __name__ == "__main__":
    import sys
    sf_name = sys.argv[1]
    print(sys.argv[1])

    print('\nStart Time: ', time.strftime('%x %X'), '\n')    
    sym_file = open(sf_name, 'r')
    tickers = sym_file.readlines()
    for ticker in tickers:
        sym = ticker.strip()
        print(sym)
        st_ha.get_ticker_hist_n_analysis(sym)

    print('\nEnd Time: ', time.strftime('%x %X'), '\n')

