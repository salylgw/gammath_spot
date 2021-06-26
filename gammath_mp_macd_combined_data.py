# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import time
import multiprocessing as mp
from multiprocessing import Process
import gammath_macd_with_combined_data as gmwcd
import sys
from pathlib import Path
import pandas as pd
        
cores_to_use = ((mp.cpu_count() >> 1) + 1)

if __name__ == '__main__':
    mp.set_start_method('fork')
    core_count = mp.cpu_count()
#    cores_to_use = ((core_count // 2) - 1)
    print('\nNumber of logical cores: ', core_count, 'Usable logical cores: ', cores_to_use)
    print('\nStart Time: ', time.strftime('%x %X'), '\n')
    proc_handles = []
    sf_name = sys.argv[1]
    print(sf_name)

    sym_file = open(sf_name, 'r')
    tickers = sym_file.readlines()

    max_tickers = len(tickers)
    start_index = 0
    if (max_tickers > cores_to_use):
        end_index = cores_to_use
    else:
        end_index = max_tickers

    while (max_tickers):
        for i in range(start_index, end_index):
            sym = tickers[i].strip()
            proc_handles.append(Process(target=gmwcd.get_macd_combined_data, args=(f'{sym}',)))
            proc_handles[i].start()

            max_tickers -= 1

        for i in range(start_index, end_index):
            proc_handles[i].join()

        if (max_tickers):
            start_index = end_index
            if (max_tickers > cores_to_use):
                end_index += cores_to_use
            else:
                end_index += max_tickers


    #Collect exception data for all tickers in one file for easy reference
    Tickers_dir = Path('tickers')

    #Get all the subdirs. Need to check for is_dir
    p = Path('tickers')

    #Somehow looks like os.is_dir isn't supported
    #Using pathlib/Path instead since is_dir is supported there
    subdirs = [x for x in p.iterdir() if x.is_dir()]

    print('\nNum of subdirs: ', len(subdirs))

    #Collector dataframe
    collected_df = pd.DataFrame()

    for subdir in subdirs:
        if not subdir.exists():
            print('\nError. ', subdir, ' not found')
        else:
            new_df = pd.read_csv(subdir / f'{subdir.name}_exception_sig_data.csv')
            if (len(new_df)):
                collected_df = collected_df.append(new_df)
                print(f'Collected exception data for {subdir.name}')

    #Save the collected data in CSV file
    collected_df.to_csv(Tickers_dir / 'all_exception_sig_data.csv', index=False)

    print('\nEnd Time: ', time.strftime('%x %X'), '\n')
