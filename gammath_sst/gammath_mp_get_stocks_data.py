# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import time
import multiprocessing as mp
from multiprocessing import Process
import gammath_get_sp500_list as gspl
import gammath_get_stocks_data as ggsd
import gammath_stocks_pe_aggregation as gspa
import sys
from pathlib import Path
import re
import pandas as pd
import random

if __name__ == '__main__':

    mp.set_start_method('fork')

    #Check how many cores we have to be able to run parallel
    core_count = mp.cpu_count()

    #Use half the cores from count; Need to check portability on this
    cores_to_use = ((mp.cpu_count() >> 1))

    print('\nNumber of logical cores: ', core_count, 'Using logical cores: ', cores_to_use)

    print('\nStart Time: ', time.strftime('%x %X'), '\n')
    proc_handles = []
    sf_name = sys.argv[1]
    print(sf_name)

    watch_list = pd.read_csv(sf_name)

    max_tickers = len(watch_list)

    #Fetch and save S&P500 list.
    gspl.get_sp500_list()

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
            proc_handles.append(Process(target=ggsd.get_stocks_data, args=(f'{sym}',)))
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
    gspa.aggregate_pe_data()
