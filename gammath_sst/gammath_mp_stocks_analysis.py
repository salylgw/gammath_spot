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
from pathlib import Path
import re
import pandas as pd
import random

MIN_DELAY_BETWEEN_BATCHES = 1
MAX_DELAY_BETWEEN_BATCHES = 3

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

    watch_list = pd.read_csv(sf_name)

    max_tickers = len(watch_list)

    start_index = 0
    if (max_tickers > cores_to_use):
        end_index = cores_to_use
    else:
        end_index = max_tickers

    while (max_tickers):
        for i in range(start_index, end_index):
            sym = watch_list['Symbol'][i].strip()
            proc_handles.append(Process(target=gsa.get_ticker_hist_n_analysis, args=(f'{sym}',)))
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

            #Following delay is no longer needed as we are not fetching data over the internet
            #Play nice
#            time.sleep(random.randrange(MIN_DELAY_BETWEEN_BATCHES, MAX_DELAY_BETWEEN_BATCHES))

    Tickers_dir = Path('tickers')

    #Get all the subdirs. Need to check for is_dir
    p = Path('tickers')
    
    #Somehow looks like os.is_dir isn't supported
    #Using pathlib/Path instead since is_dir is supported there
    subdirs = [x for x in p.iterdir() if x.is_dir()]

    print('\nNum of subdirs: ', len(subdirs))

    pattern_for_final_buy_score = re.compile(r'(final_buy_score):([-]*[0-9]*[.]*[0-9]+)')
    pattern_for_final_sell_score = re.compile(r'(final_sell_score):([-]*[0-9]*[.]*[0-9]+)')

    #Collect 1Y OLS regression fit scores for debugging
    pattern_for_1y_ols_fit_score = re.compile(r'(ols_1y_fit_score):([-]*[0-9]*[.]*[0-9]+)')

    #Collect 3Y OLS regression fit scores for debugging
    pattern_for_3y_ols_fit_score = re.compile(r'(ols_3y_fit_score):([-]*[0-9]*[.]*[0-9]+)')

    #Collect OLS regression fit scores for debugging
    pattern_for_ols_fit_score = re.compile(r'(ols_fit_score):([-]*[0-9]*[.]*[0-9]+)')

    #Collect SGD regression fit scores for debugging
    pattern_for_sgd_fit_score = re.compile(r'(sgd_fit_score):([-]*[0-9]*[.]*[0-9]+)')

    #Collect Ridge regression fit scores for debugging
    pattern_for_ridge_fit_score = re.compile(r'(ridge_fit_score):([-]*[0-9]*[.]*[0-9]+)')

    #Collect Bayesian Ridge regression fit scores for debugging
    pattern_for_bayesian_ridge_fit_score = re.compile(r'(bayesian_ridge_fit_score):([-]*[0-9]*[.]*[0-9]+)')

    #Collect Lasso regression fit scores for debugging
    pattern_for_lasso_fit_score = re.compile(r'(lasso_fit_score):([-]*[0-9]*[.]*[0-9]+)')

    #Collect Logistic regression scores for debugging
    pattern_for_lgstic_fit_score = re.compile(r'(lgstic_fit_score):([-]*[0-9]*[.]*[0-9]+)')

    df_b = pd.DataFrame(columns=['Ticker', 'final_buy_score'], index=range(len(subdirs)))

    df_s = pd.DataFrame(columns=['Ticker', 'final_sell_score'], index=range(len(subdirs)))

    df_fs = pd.DataFrame(columns=['Ticker', 'ols_1y_fit_score', 'ols_3y_fit_score', 'ols_fit_score' ,'sgd_fit_score', 'ridge_fit_score', 'bayesian_fit_score', 'lasso_fit_score', 'lgstic_fit_score'], index=range(len(subdirs)))

    i = 0
    j = 0
    k = 0

    for subdir in subdirs:
        if not subdir.exists():
            print('\nError. ', subdir, ' not found')
        else:
            try:
                f = open(subdir / 'signal.txt', 'r')
                content = f.read()
                matched_string = pattern_for_final_buy_score.search(content)
                if (matched_string):
                    kw, val = matched_string.groups()
                    print(f'\n{kw} for {subdir.name}: {val}')
                    df_b['Ticker'][i] = f'{subdir.name}'
                    df_b['final_buy_score'][i] = float(val)
                    i += 1
                else:
                    print(f'\n{kw} NOT found for {subdir}')

                matched_string = pattern_for_final_sell_score.search(content)
                if (matched_string):
                    kw, val = matched_string.groups()
                    print(f'\n{kw} for {subdir.name}: {val}')
                    df_s['Ticker'][j] = f'{subdir.name}'
                    df_s['final_sell_score'][j] = float(val)
                    j += 1
                else:
                    print(f'\n{kw} NOT found for {subdir}')


                matched_string = pattern_for_1y_ols_fit_score.search(content)
                if (matched_string):
                    kw, val = matched_string.groups()
                    print(f'\n{kw} for {subdir.name}: {val}')
                    df_fs['Ticker'][k] = f'{subdir.name}'
                    df_fs['ols_1y_fit_score'][k] = float(val)
                else:
                    print(f'\n{kw} NOT found for {subdir}')

                matched_string = pattern_for_3y_ols_fit_score.search(content)
                if (matched_string):
                    kw, val = matched_string.groups()
                    print(f'\n{kw} for {subdir.name}: {val}')
                    df_fs['Ticker'][k] = f'{subdir.name}'
                    df_fs['ols_3y_fit_score'][k] = float(val)
                else:
                    print(f'\n{kw} NOT found for {subdir}')

                matched_string = pattern_for_ols_fit_score.search(content)
                if (matched_string):
                    kw, val = matched_string.groups()
                    print(f'\n{kw} for {subdir.name}: {val}')
                    df_fs['Ticker'][k] = f'{subdir.name}'
                    df_fs['ols_fit_score'][k] = float(val)
                else:
                    print(f'\n{kw} NOT found for {subdir}')

                matched_string = pattern_for_sgd_fit_score.search(content)
                if (matched_string):
                    kw, val = matched_string.groups()
                    print(f'\n{kw} for {subdir.name}: {val}')
                    df_fs['Ticker'][k] = f'{subdir.name}'
                    df_fs['sgd_fit_score'][k] = float(val)
                else:
                    print(f'\n{kw} NOT found for {subdir}')

                matched_string = pattern_for_ridge_fit_score.search(content)
                if (matched_string):
                    kw, val = matched_string.groups()
                    print(f'\n{kw} for {subdir.name}: {val}')
                    df_fs['Ticker'][k] = f'{subdir.name}'
                    df_fs['ridge_fit_score'][k] = float(val)
                else:
                    print(f'\n{kw} NOT found for {subdir}')

                matched_string = pattern_for_bayesian_ridge_fit_score.search(content)
                if (matched_string):
                    kw, val = matched_string.groups()
                    print(f'\n{kw} for {subdir.name}: {val}')
                    df_fs['Ticker'][k] = f'{subdir.name}'
                    df_fs['bayesian_fit_score'][k] = float(val)
                else:
                    print(f'\n{kw} NOT found for {subdir}')

                matched_string = pattern_for_lasso_fit_score.search(content)
                if (matched_string):
                    kw, val = matched_string.groups()
                    print(f'\n{kw} for {subdir.name}: {val}')
                    df_fs['Ticker'][k] = f'{subdir.name}'
                    df_fs['lasso_fit_score'][k] = float(val)
                else:
                    print(f'\n{kw} NOT found for {subdir}')

                matched_string = pattern_for_lgstic_fit_score.search(content)
                if (matched_string):
                    kw, val = matched_string.groups()
                    print(f'\n{kw} for {subdir.name}: {val}')
                    df_fs['Ticker'][k] = f'{subdir.name}'
                    df_fs['lgstic_fit_score'][k] = float(val)
                else:
                    print(f'\n{kw} NOT found for {subdir}')

                k += 1
                f.close()
            except:
                print('\nError while getting stock signals for ', subdir.name, ': ', sys.exc_info()[0])

    df_b.sort_values('final_buy_score').dropna(how='all').to_csv(Tickers_dir / 'overall_buy_scores.csv', index=False)
    df_s.sort_values('final_sell_score').dropna(how='all').to_csv(Tickers_dir / 'overall_sell_scores.csv', index=False)

    #Regression fit scores Debug data
    df_fs.sort_values('Ticker').dropna(how='all').to_csv(Tickers_dir / 'overall_regression_fit_scores.csv', index=False)

    print('\nEnd Time: ', time.strftime('%x %X'), '\n')
