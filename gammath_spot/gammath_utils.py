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

import sys
import os
import time
from pathlib import Path
import pandas as pd
import re

def check_if_same_day(fstat):

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

        self.Tickers_dir = Path('tickers')

    def get_sp500_list(self):

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
            dont_need_fetch = False

        if (not dont_need_fetch):
            #Get S&P500 list from the internet.
            #Specify header (row to use to make column headers)
            #No need to get entire list of dataframes. We only need first dataframe
            sp500 = pd.read_html(sp500_list_url, header=0)[0]

            #Save the history for reference and processing
            sp500.to_csv(path / f'SP500_list.csv')

        return

    def aggregate_scores(self):

        #Get all the subdirs. Need to check for is_dir
        p = self.Tickers_dir

        #Somehow looks like os.is_dir isn't supported
        #Using pathlib/Path instead since is_dir is supported there
        subdirs = [x for x in p.iterdir() if x.is_dir()]

        #Pattern for note
        pattern_for_note = re.compile(r'(Note):([\s]*[A-Z]*[_]*[A-Z]*[_]*[A-Z]*[_]*[A-Z]*[_]*[A-Z]*[_]*[A-Z]*)')

        df_b = pd.DataFrame(columns=['Ticker', 'sh_gscore', 'sci_gscore', 'final_gscore', 'Note'], index=range(len(subdirs)))

        i = 0

        for subdir in subdirs:
            if subdir.exists():
                try:
                    df_gscores = pd.read_csv(subdir / f'{subdir.name}_gscores.csv', index_col='Unnamed: 0')
                    df_b['Ticker'][i] = f'{subdir.name}'
                    df_b['sh_gscore'][i] = df_gscores.SH_Total[0]
                    df_b['sci_gscore'][i] = df_gscores.SCI_Total[0]
                    df_b['final_gscore'][i] = df_gscores.Total[0]

                    f = open(subdir / f'{subdir.name}_signal.txt', 'r')
                    content = f.read()

                    matched_string = pattern_for_note.search(content)
                    if (matched_string):
                        kw, note = matched_string.groups()
                        df_b['Note'][i] = note
                    else:
                        df_b['Note'][i] = ''

                    i += 1
                    f.close()
                except:
                    print('\nERROR: Getting stock signals for ', subdir.name, ': ', sys.exc_info()[0])

        df_b.sort_values('final_gscore').dropna(how='all').to_csv(p / 'overall_gscores.csv', index=False)


    def aggregate_pe_data(self):

        path = self.Tickers_dir
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
                df_pe['TPE'][i] = 0
                df_pe['FPE'][i] = 0

            i += 1

        #Extract unique sectors
        sectors = df_sp['GICS Sector'].drop_duplicates()
        sector_list = []

        #Calculate average and save for each sector; also save sectors
        i = 0
        new_tpe = 0
        new_fpe = 0

        sector_fields = list(df_sp['GICS Sector'])
        len_sector_fields = len(sector_fields)
        tpes = list(df_pe['TPE'])
        fpes = list(df_pe['FPE'])

        for sector in sectors:
            sector_list.append(sector)
            curr_sector_tpe = 0
            curr_sector_tpe_count = 0
            curr_sector_fpe = 0
            curr_sector_fpe_count = 0
            start_index = i
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

            if (curr_sector_fpe_count):
                curr_sector_fpe_avg = curr_sector_fpe / curr_sector_fpe_count


            #Save average values at all indices for this sector
            df_pe['LS_AVG_TPE'][start_index:end_index] = curr_sector_tpe_avg
            df_pe['LS_AVG_FPE'][start_index:end_index] = curr_sector_fpe_avg


        #New data frame with columns from PE dataframe joined
        df_sp = df_sp.join(df_pe)

        #Drop unwanted fields
        df_sp = df_sp.dropna(axis=0, how='all').drop('Unnamed: 0', axis=1)

        #Rearrange based on ticker symbol
        df_sp = df_sp.sort_values('Symbol')

        #Save for later reference and processing
        df_sp.to_csv(path / 'SP500_SEC_PES.csv', index=False)
