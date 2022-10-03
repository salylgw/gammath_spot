# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2022, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021-2022, Salyl Bhagwat, Gammath Works'

import time
import multiprocessing as mp
from multiprocessing import Process

try:
    from gammath_spot import gammath_lpep as glpep
    from gammath_spot import gammath_utils as gut
except:
    import gammath_lpep as glpep
    import gammath_utils as gut

import pandas as pd
import sys

def main():
    """
    Main function to compute stock's price estimate and price projection. The estimate and projection charts are saved in tickers/<ticker_symbol>/<ticker_symbol>_pep.png. The price projection values are saved in tickers/<ticker_symbol>/<ticker_symbol>_pp.csv.
    """

    #Avoiding to check number of args as if watchlist is not there then there will be an exception anyway
    try:
        #Get the watchlist file from pgm argument
        sf_name = sys.argv[1]
    except:
        print('ERROR: Need watch list file name as one argument to this Program. See watchlist.csv')
        raise ValueError('Missing watch list')

    #Read the watchlist
    try:
        watch_list = pd.read_csv(sf_name)
    except:
        print('ERROR: Failed to read watchlist. See watchlist.csv for example')
        raise ValueError('Watchlist file read failed')

    #Set the start method for launching parallel processes
    #Python 3.8 onwards 'spawn' is the default method for MacOS and is supported on Linux and Windows
    #so using it for portability. Spawn method is much slower compared to 'fork' method. If there are no unsafe changes made to this project then on MacOS and Linux this can be changed to use 'fork'
    mp.set_start_method('spawn')

    #Check number of cores we have to be able to run in parallel
    core_count = mp.cpu_count()

    #Need to check portability on this

    #Might need to reduce the number cores actually used hence core_count and cores_to_use are defined separately
    cores_to_use = core_count

    if (cores_to_use < 1):
        cores_to_use = 1

    print('\nStart Time: ', time.strftime('%x %X'), '\n')

    proc_handles = []

    max_tickers = len(watch_list)

    #Use one process per core so we can run core_to_use number of processes in parallel
    start_index = 0
    if (max_tickers > cores_to_use):
        end_index = cores_to_use
    else:
        end_index = max_tickers

    #Instances of GPEP class
    gpep_instances = []
    symbols_list = []

    while (max_tickers):
        for i in range(start_index, end_index):

            sym = watch_list['Symbol'][i].strip()
            tsymbol = f'{sym}'
            symbols_list.append(tsymbol)
            gpep_instances.append(glpep.GPEP())
            proc_handles.append(Process(target=gpep_instances[i].get_moving_price_estimated_projection, args=(f'{sym}',)))
            proc_handles[i].start()

            max_tickers -= 1

        for i in range(start_index, end_index):
            proc_handles[i].join()

        #Running out of resources so need to close handles and release resources
        for i in range(start_index, end_index):
            proc_handles[i].close()

        if (max_tickers):
            start_index = end_index
            if (max_tickers > cores_to_use):
                end_index += cores_to_use
            else:
                end_index += max_tickers

    #Instantiate GUTILS class
    gutils = gut.GUTILS()

    #Generate 5Y estimated projection for S&P500
    gpep = glpep.GPEP()
    gpep.sp500_pep()

    #Aggregate a sorted list of moving 5Y estimated projected returns
    gutils.aggregate_peps(symbols_list)

    print('\nEnd Time: ', time.strftime('%x %X'), '\n')

if __name__ == '__main__':
    main()
