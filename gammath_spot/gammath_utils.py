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
from datetime import date
from pathlib import Path
import pandas as pd
import re
import pandas_datareader.data as pdd
import numpy as np
from matplotlib import pyplot as plt

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

#Common function to generate price sigmoid
#Specify 'n' days interval for checking the diff
def get_price_sigmoid(prices, n_days_interval):

    prices_len = len(prices)
    start_index = (prices_len % n_days_interval)
    end_index = (prices_len - n_days_interval)

    #Zero-initialize the sigmoid
    prices_sigmoid = pd.Series(0, pd.RangeIndex((prices_len-start_index)/n_days_interval))
    j = 1

    #First element of sigmoid is set to 0; next ascending val then 1 else 0
    for i in range(start_index, end_index, n_days_interval):
        if (prices[i] <= prices[i+n_days_interval]):
            prices_sigmoid[j] = 1
        else:
            prices_sigmoid[j] = 0
        j += 1


    return (prices_sigmoid)

class GUTILS:

    def __init__(self):

        self.Tickers_dir = Path('tickers')
        self.MIN_TRADING_DAYS_FOR_5_YEARS = 249*5

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
                    df_b['sh_gscore'][i] = df_gscores.SH_gScore[0]
                    df_b['sci_gscore'][i] = df_gscores.SCI_gScore[0]
                    df_b['final_gscore'][i] = df_gscores.gScore[0]

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

    def get_sp500_closing_data(self):

        path = self.Tickers_dir

        try:
            #SP500 closing data (apparently, start and end defaults aren't working)
            #Specify a start to get more data
            sp500_closing_data = pdd.DataReader('SP500', 'fred', start='1/1/2010')
            sp500_closing_data.columns = ['Close']
            sp500_closing_data.to_csv(path / 'SP500_history.csv')
        except:
            print('Get SP500 closing data failed')

    def get_sp500_5y_return_conjecture(self):

        path = self.Tickers_dir

        try:
            #SP500 closing data (entire range)
            sp500_closing_data = pd.read_csv(path / 'SP500_history.csv')

            #Get a 5Y return conjecture
            pct_5y_return_conecture = sp500_closing_data.Close.dropna().pct_change().mean()*self.MIN_TRADING_DAYS_FOR_5_YEARS*100

            return round(pct_5y_return_conecture, 3)
        except:
            print('Get SP500 5Y return conjecture failed')
            return 0

    def get_sp500_actual_return(self, start_date, end_date):

        path = self.Tickers_dir

        try:
            #SP500 closing data
            sp500_closing_data = pd.read_csv(path / 'SP500_history.csv')
            sp500_closing_data = sp500_closing_data.set_index('DATE')
            try:
                start_val = sp500_closing_data.Close[start_date]
            except:
                print(f'Failed to get SP500 closing price data for date {start_date}')
                return np.nan

            try:
                end_val = sp500_closing_data.Close[end_date]
            except:
                print(f'Failed to get SP500 closing price data for date {end_date}')
                return np.nan

            #Get actual return percentage
            actual_pct_return = ((end_val - start_val)*100/start_val)

            return round(actual_pct_return, 3)
        except:
            print(f'Get SP500 actual return failed for dates {start_date} and {end_date}')
            return np.nan

    def get_5y_ppct(self, path, tsymbol):
        try:
            df_pp = pd.read_csv(path / f'{tsymbol}_pp.csv')
        except:
            print(f'Error opening price projection data for {tsymbol}')
            raise ValueError('Price projection error')

        try:
            df = pd.read_csv(path / f'{tsymbol}_history.csv')
        except:
            print(f'Error opening gscores files for {tsymbol}')
            raise ValueError('History error')

        #Get last price
        lp = df.Close[len(df)-1]
        pp_len = len(df_pp)

        if (pp_len < self.MIN_TRADING_DAYS_FOR_5_YEARS):
            print(f'Not enough projection data for {tsymbol}')
            raise ValueError('Not enough projection data')

        #Get last projection
        m5ypep = round(df_pp.PP[pp_len-1], 3)

        #Calculate the percentage return for easy comparison
        m5ypep_pct = round((((m5ypep - lp)*100)/lp), 3)

        return m5ypep, m5ypep_pct

    def aggregate_peps(self, symbols_list):

        #Create a dataframe to save tickers and their associated moving estimated projected 5Y returns
        df_pep = pd.DataFrame(columns=['Ticker', 'M5YPEP', 'M5YPEP_PCT'], index=range(len(symbols_list)+1))

        i = 0

        for tsymbol in symbols_list:
            try:
                path = self.Tickers_dir / f'{tsymbol}'
                try:
                    m5ypep, m5ypep_pct = self.get_5y_ppct(path, tsymbol)
                except:
                    continue

                df_pep['Ticker'][i] = f'{tsymbol}'
                df_pep['M5YPEP'][i] = m5ypep
                df_pep['M5YPEP_PCT'][i] = m5ypep_pct

                i += 1
            except:
                print('\nERROR: extracting estimated projections for ', tsymbol, ': ', sys.exc_info()[0])

        #Back to base dir
        p = self.Tickers_dir

        tsymbol = 'SP500'
        try:
            m5ypep, m5ypep_pct = self.get_5y_ppct(p, tsymbol)
        except:
            print(f'S&P500 Price projection error')
        else:
            df_pep['Ticker'][i] = tsymbol
            df_pep['M5YPEP'][i] = m5ypep
            df_pep['M5YPEP_PCT'][i] = m5ypep_pct

        #Save a sorted (by return percentage) list for convenient reference
        df_pep.sort_values('M5YPEP_PCT').dropna(how='all').to_csv(p / 'MPEP.csv', index=False)


    def summarize_todays_actions(self, symbols_list):

        #Get today's date
        today = date.today()
        today_year = today.year
        today_month = today.month
        today_day = today.day

        #Create a dataframe to save tickers and their associated actions
        df_actions = pd.DataFrame(columns=['Ticker', 'Price', 'Action', 'Quantity', 'Term'], index=range(len(symbols_list)<<1))

        i = 0

        for tsymbol in symbols_list:
            path = self.Tickers_dir / f'{tsymbol}'
            try:
                bactesting_st_data = pd.read_csv(path / f'{tsymbol}_gtrades_stats_short_term.csv', index_col='Unnamed: 0')
                bt_st_data_len = len(bactesting_st_data)
                last_action_index = bt_st_data_len-2
                last_action_date = bactesting_st_data.Date.iloc[last_action_index].split(' ')[0].split('-')
                if ((today_year == int(last_action_date[0])) and (today_month == int(last_action_date[1])) and (today_day == int(last_action_date[2]))):
                    #Today's action
                    df_actions['Ticker'][i] = f'{tsymbol}'
                    df_actions['Price'][i] = bactesting_st_data.Price.iloc[last_action_index]
                    df_actions['Action'][i] = bactesting_st_data.Action.iloc[last_action_index]
                    df_actions['Quantity'][i] = bactesting_st_data.Quantity.iloc[last_action_index]
                    df_actions['Term'][i] = 'short_term'
                    i += 1
            except:
                print(f'Failed to open short-term backtesting data for {tsymbol}')
            try:
                bactesting_lt_data = pd.read_csv(path / f'{tsymbol}_gtrades_stats_long_term.csv', index_col='Unnamed: 0')
                bt_lt_data_len = len(bactesting_lt_data)
                last_action_index = bt_lt_data_len-2
                last_action_date = bactesting_lt_data.Date.iloc[last_action_index].split(' ')[0].split('-')
                if ((today_year == int(last_action_date[0])) and (today_month == int(last_action_date[1])) and (today_day == int(last_action_date[2]))):
                    #Today's action
                    df_actions['Ticker'][i] = f'{tsymbol}'
                    df_actions['Price'][i] = bactesting_lt_data.Price.iloc[last_action_index]
                    df_actions['Action'][i] = bactesting_lt_data.Action.iloc[last_action_index]
                    df_actions['Quantity'][i] = bactesting_lt_data.Quantity.iloc[last_action_index]
                    df_actions['Term'][i] = 'long_term'
                    i += 1
            except:
                print(f'Failed to open long-term backtesting data for {tsymbol}')


        #Back to base dir
        p = self.Tickers_dir

        #Save a sorted (by ticker symbol) list for convenient reference
        df_actions.sort_values('Ticker').dropna(how='all').to_csv(p / 'Todays_Actions.csv', index=False)
