# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import time
import multiprocessing as mp
from multiprocessing import Process
import gammath_stocks_analysis as gsa
import gammath_utils as gut
import pandas as pd
import sys

if __name__ == '__main__':

    mp.set_start_method('fork')

    #Check number of cores we have to be able to run in parallel
    core_count = mp.cpu_count()

    #Use half the cores from count; Need to check portability on this
    cores_to_use = (core_count >> 1)

    print('\nNumber of logical cores: ', core_count, 'Using logical cores: ', cores_to_use)
    print('\nStart Time: ', time.strftime('%x %X'), '\n')

    proc_handles = []
    sf_name = sys.argv[1]
    print(sf_name)

    watch_list = pd.read_csv(sf_name)

    max_tickers = len(watch_list)

    #Use one process per core so we can run core_to_use number of processes in parallel
    start_index = 0
    if (max_tickers > cores_to_use):
        end_index = cores_to_use
    else:
        end_index = max_tickers

    #Instances of GSA class
    gsa_instances = []

    while (max_tickers):
        for i in range(start_index, end_index):
            sym = watch_list['Symbol'][i].strip()
            tsymbol = f'{sym}'
            gsa_instances.append(gsa.GSA())
            proc_handles.append(Process(target=gsa_instances[i].do_stock_analysis_and_compute_score, args=(f'{sym}',)))
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

    #Aggregate all buy and sell scores
    gutils.aggregate_scores()

    print('\nEnd Time: ', time.strftime('%x %X'), '\n')
