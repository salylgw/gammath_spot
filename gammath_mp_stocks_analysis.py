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
import sys
import os
from pathlib import Path
import re
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
            proc_handles.append(Process(target=gsa.get_ticker_hist_n_analysis, args=(f'{sym}',)))
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

    Tickers_dir = Path('tickers')

#    pattern_for_overall_buy_score = re.compile(r'(overall_buy_score):([-]*[0-9]+[/][0-9]+)')
#    pattern_for_overall_sell_score = re.compile(r'(overall_sell_score):([-]*[0-9]+[/][0-9]+)')

    pattern_for_overall_buy_score = re.compile(r'(overall_buy_score):([-]*[0-9]+)')
    pattern_for_overall_sell_score = re.compile(r'(overall_sell_score):([-]*[0-9]+)')

    subdirs = os.listdir(Tickers_dir)

    print('\nNum of subdirs: ', len(subdirs))

    df_b = pd.DataFrame(columns=['Ticker', 'overall_buy_score'], index=range(len(subdirs)))

    df_s = pd.DataFrame(columns=['Ticker', 'overall_sell_score'], index=range(len(subdirs)))

    i = 0
    j = 0

    for subdir in subdirs:
        path = Tickers_dir / f'{subdir}'
        if not path.exists():
            print('\nError. ', path, ' not found')
        else:
            f = open(path / 'signal.txt', 'r')
            content = f.read()
            matched_string = pattern_for_overall_buy_score.search(content)
            if (matched_string):
                kw, val = matched_string.groups()
                print(f'\n{kw} for {subdir}: {val}')
                df_b['Ticker'][i] = f'{subdir}'
                df_b['overall_buy_score'][i] = int(val)
                i += 1
            else:
                print(f'\n{kw} NOT found for {subdir}')

            matched_string = pattern_for_overall_sell_score.search(content)
            if (matched_string):
                kw, val = matched_string.groups()
                print(f'\n{kw} for {subdir}: {val}')
                df_s['Ticker'][j] = f'{subdir}'
                df_s['overall_sell_score'][j] = int(val)
                j += 1
            else:
                print(f'\n{kw} NOT found for {subdir}')

            f.close()

    df_b.sort_values('overall_buy_score').to_csv(Tickers_dir / 'overall_buy_scores.csv', index=False)
    df_s.sort_values('overall_sell_score').to_csv(Tickers_dir / 'overall_sell_scores.csv', index=False)

    print('\nEnd Time: ', time.strftime('%x %X'), '\n')
