# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import sys
import os
import time
from pathlib import Path
import pandas as pd
import re

def check_if_same_day(fstat):

    print(f'\nChecking if same day file')

    fct_time = time.ctime(fstat.st_ctime).split(' ')
    dt = time.strftime('%x').split('/')
    if (fct_time[2] == ''):
        fct_date_index = 3
    else:
        fct_date_index = 2

    fct_date = int(fct_time[fct_date_index])
    dt_date = int(dt[1])

    if (fct_date == dt_date):
        return True
    else:
        return False

class GUTILS:

    def __init__(self):
        print('\nGUTILS instantiated')
        self.Tickers_dir = Path('tickers')


    def get_sp500_list(self):

        print(f'\nGetting list of SP500 companies')

        sp500_list_url = f'https://en.wikipedia.org/wiki/List_of_S&P_500_companies'

        path = self.Tickers_dir
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        #Fetch the file only once a day
        dont_need_fetch = True

        try:
            #Get existing file
            file_exists = (path / f'SP500_list.csv').exists()

            #Check if file exists and is it from another day
            if file_exists:
                fstat = os.stat(path / f'SP500_list.csv')
                dont_need_fetch = check_if_same_day(fstat)
            else:
                #File doesn't exist/
                dont_need_fetch = False
        except:
            print(f'\nError checking SP500 list')

        if (not dont_need_fetch):
            #Get S&P500 list from the internet.
            #Specify header (row to use to make column headers)
            #No need to get entire list of dataframes. We only need first dataframe
            sp500 = pd.read_html(sp500_list_url, header=0)[0]

            print('S&P500 list dataframe info:\n')
            sp500.info()

            #Save the history for reference and processing
            sp500.to_csv(path / f'SP500_list.csv')

        return

    def aggregate_scores(self):
        print('\nGUTILS aggregate_scores')

        #Get all the subdirs. Need to check for is_dir
        p = self.Tickers_dir

        #Somehow looks like os.is_dir isn't supported
        #Using pathlib/Path instead since is_dir is supported there
        subdirs = [x for x in p.iterdir() if x.is_dir()]

        print('\nNum of subdirs: ', len(subdirs))

        pattern_for_final_dip_score = re.compile(r'(final_dip_score):([-]*[0-9]*[.]*[0-9]+)')

        #Collect 1Y OLS regression fit scores for debugging
        pattern_for_1y_ols_fit_score = re.compile(r'(ols_1y_fit_score):([-]*[0-9]*[.]*[0-9]+)')

        #Collect OLS regression fit scores for debugging
        pattern_for_ols_fit_score = re.compile(r'(ols_fit_score):([-]*[0-9]*[.]*[0-9]+)')

        #Pattern for note
        pattern_for_note = re.compile(r'(Note):([\s]*[A-Z]*[_]*[A-Z]*[_]*[A-Z]*)')



        df_b = pd.DataFrame(columns=['Ticker', 'final_dip_score', 'Note'], index=range(len(subdirs)))


        df_fs = pd.DataFrame(columns=['Ticker', 'ols_1y_fit_score', 'ols_fit_score'], index=range(len(subdirs)))


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
                    note = ''
                    matched_string = pattern_for_note.search(content)
                    if (matched_string):
                        kw, note = matched_string.groups()
                        print(f'\n{kw} for {subdir.name}: {note}')
                    else:
                        print(f'\nNote-Pattern NOT found for {subdir}')

                    matched_string = pattern_for_final_dip_score.search(content)
                    if (matched_string):
                        kw, val = matched_string.groups()
                        print(f'\n{kw} for {subdir.name}: {val}')
                        df_b['Ticker'][i] = f'{subdir.name}'
                        df_b['final_dip_score'][i] = float(val)
                        df_b['Note'][i] = note
                        i += 1
                    else:
                        print(f'\nFinal dip score pattern NOT found for {subdir}')


                    matched_string = pattern_for_1y_ols_fit_score.search(content)
                    if (matched_string):
                        kw, val = matched_string.groups()
                        print(f'\n{kw} for {subdir.name}: {val}')
                        df_fs['Ticker'][k] = f'{subdir.name}'
                        df_fs['ols_1y_fit_score'][k] = float(val)
                    else:
                        print(f'\n1Y OLS fit score pattern NOT found for {subdir}')

                    matched_string = pattern_for_ols_fit_score.search(content)
                    if (matched_string):
                        kw, val = matched_string.groups()
                        print(f'\n{kw} for {subdir.name}: {val}')
                        df_fs['Ticker'][k] = f'{subdir.name}'
                        df_fs['ols_fit_score'][k] = float(val)
                    else:
                        print(f'\nOLS fit pattern NOT found for {subdir}')

                    k += 1
                    f.close()
                except:
                    print('\nError while getting stock signals for ', subdir.name, ': ', sys.exc_info()[0])

        df_b.sort_values('final_dip_score').dropna(how='all').to_csv(self.Tickers_dir / 'overall_dip_scores.csv', index=False)

        #Regression fit scores Debug data
        df_fs.sort_values('Ticker').dropna(how='all').to_csv(self.Tickers_dir / 'overall_regression_fit_scores.csv', index=False)

    def aggregate_pe_data(self):

        print(f'\nAggregating PE data')

        path = self.Tickers_dir
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        df = pd.read_csv(path / 'SP500_list.csv')

        #Need to calculate sector-average so rearrange
        df_sp = df.sort_values('GICS Sector')

        df_sp_len = len(df_sp)

        #Create new dataframe for holding trailing/forward PE and their respective sector averages
        df_pe = pd.DataFrame(columns=['TPE', 'FPE', 'LS_AVG_TPE', 'LS_AVG_FPE'], index=range(df_sp_len))

        i = 0
        #Get all symbols in list
        symbols = list(df_sp['Symbol'])

        for symbol in symbols:
            try:
                df_summ = pd.read_csv(path / f'{symbol}/{symbol}_summary.csv')
                tpe = df_summ['trailingPE'][0]
                fpe = df_summ['forwardPE'][0]

                #df_sp Symbols are arranged based on sectors so same order will be in df_pe
                df_pe['TPE'][i] = tpe
                df_pe['FPE'][i] = fpe

            except:
                print('\nError while getting stock PE values for ', symbol, ': ', sys.exc_info()[0])
                df_pe['TPE'][i] = 0
                df_pe['FPE'][i] = 0

            i += 1

        print('DataFrame length: ', df_sp_len)

        #Extract unique sectors
        sectors = df_sp['GICS Sector'].drop_duplicates()
        print('\nSectors: ', sectors)
        sector_list = []

        #Calculate average and save for each sector; also save sectors
        i = 0
        new_tpe = 0
        new_fpe = 0

        sector_fields = list(df_sp['GICS Sector'])
        len_sector_fields = len(sector_fields)
        print('\nSector fields list size: ', len_sector_fields)
        tpes = list(df_pe['TPE'])
        fpes = list(df_pe['FPE'])

        for sector in sectors:
            sector_list.append(sector)
            curr_sector_tpe = 0
            curr_sector_tpe_count = 0
            curr_sector_fpe = 0
            curr_sector_fpe_count = 0
            start_index = i
            print('Sector field: ', sector_fields[i], 'Sector: ', sector)
            while (sector_fields[i] == sector):
                new_tpe = tpes[i]
                new_fpe = fpes[i]
                i += 1

                if (new_tpe > 0):
                    curr_sector_tpe_count += 1
                    curr_sector_tpe += new_tpe

                if (new_fpe > 0):
                    curr_sector_fpe_count += 1
                    curr_sector_fpe += new_fpe

                if (i == len_sector_fields):
                    break

            end_index = i
            curr_sector_tpe_avg = 0
            curr_sector_fpe_avg = 0

            if (curr_sector_tpe_count):
                curr_sector_tpe_avg = curr_sector_tpe / curr_sector_tpe_count
                print('TPE AVG: ', curr_sector_tpe_avg, 'start_index: ', start_index, 'end_index: ', end_index)

            if (curr_sector_fpe_count):
                curr_sector_fpe_avg = curr_sector_fpe / curr_sector_fpe_count
                print('FPE AVG: ', curr_sector_fpe_avg, 'start_index: ', start_index, 'end_index: ', end_index)

            print(f'start index: {start_index}, end index: {end_index}')

            #Save average values at all indices for this sector
            df_pe['LS_AVG_TPE'][start_index:end_index] = curr_sector_tpe_avg
            df_pe['LS_AVG_FPE'][start_index:end_index] = curr_sector_fpe_avg

        print(df_pe)
        print(f'\nSector list: {sector_list}')

        #New data frame with columns from PE dataframe joined
        df_sp = df_sp.join(df_pe)

        #Drop unwanted fields
        df_sp = df_sp.dropna(0, how='all').drop('Unnamed: 0', axis=1)

        #Rearrange based on ticker symbol
        df_sp = df_sp.sort_values('Symbol')

        #Save for later reference and processing
        df_sp.to_csv(path / 'SP500_SEC_PES.csv', index=False)


