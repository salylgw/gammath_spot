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

import multiprocessing as mp
from multiprocessing import Process
try:
    from gammath_spot import gammath_get_stocks_data as ggsd
    from gammath_spot import gammath_utils as gut
except:
    import gammath_get_stocks_data as ggsd
    import gammath_utils as gut

import sys
from pathlib import Path
import pandas as pd

def main():
    """
    Main function to scrape the web and collect data necessary for analyzing and computing gScores for each stock in the provided watchlist. It saves the collected data in tickers/<ticker_symbol> directory.
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

    #Check how many cores we have to be able to run parallel
    core_count = mp.cpu_count()

    #Need to check portability on this
    #Might need to reduce the number cores actually used hence core_count and cores_to_use are defined separately
    cores_to_use = core_count

    if (cores_to_use < 1):
        cores_to_use = 1

    proc_handles = []

    max_tickers = len(watch_list)

    #Instantiate GUTILS class
    gutils = gut.GUTILS()

    #Fetch and save S&P500 list.
    gutils.get_sp500_list()

    #Fetch S&P500 closing data.
    gutils.get_sp500_closing_data()

    #Instances of GSD class
    gsd_instances = []

    #One process per ticker symbol
    #Run cores_to_use number of processes in parallel
    start_index = 0
    if (max_tickers > cores_to_use):
        end_index = cores_to_use
    else:
        end_index = max_tickers

    while (max_tickers):
        for i in range(start_index, end_index):
            sym = watch_list['Symbol'][i].strip()
            gsd_instances.append(ggsd.GSD())
            proc_handles.append(Process(target=gsd_instances[i].get_stocks_data, args=(f'{sym}',)))
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

    #Aggregate and save PE data
    gutils.aggregate_pe_data()

if __name__ == '__main__':
    main()
