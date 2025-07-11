# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-Present, Salyl Bhagwat, Gammath Works
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
__copyright__ = 'Copyright (c) 2021-Present, Salyl Bhagwat, Gammath Works'

import sys
import os
import multiprocessing as mp
import time
from datetime import date
from pathlib import Path
import pandas as pd
import re
import pandas_datareader.data as pdd
import numpy as np
from glob import glob
import configparser
import requests
import yfinance as yf

try:
    from gammath_spot import version
    from gammath_spot import gammath_get_stocks_history as gsh
    from gammath_spot import gammath_stocks_analysis as gsa
except:
    import version
    import gammath_get_stocks_history as gsh
    import gammath_stocks_analysis as gsa


#Number of trading days varies across the globe.
#Some stock exchanges are closed more than US stocks exchanges.
#As a result, setting the minimum to 239 to accomodate stock exchanges
#in multiple geographical areas
MIN_TRADING_DAYS_PER_YEAR = 239
MIN_TRADING_DAYS_FOR_5_YEARS = (MIN_TRADING_DAYS_PER_YEAR*5)

def get_gammath_spot_version_string():
    #Show version for GUI
    return f'version {version.__version__}'

def set_child_process_start_method():

    try:
        start_method = mp.get_start_method(allow_none=True)
    except:
        start_method = None

    #set_start_method should be called only once preferrably from main function
    try:
        if (start_method != 'spawn'):
            mp.set_start_method('spawn')
    except:
        print(f'Failed to set child process start method to spawn. Current method is {start_method}')

def get_usable_cpu_count():

    #Check how many cores we have to be able to run in parallel
    #Need to check portability on this.
    #os.name can be used to check posix
    #os.name 'nt' could be used for windows as os.uname won't be supported on Windows
    #If os.name is 'posix' then os.uname().sysname could be used to check which OS
    try:
        cores_to_use = len(os.sched_getaffinity(0))
    except:
        #Workaround. Need to find a better way at some point
        cores_to_use = ((mp.cpu_count())//2)

    #Might need to change the way number of usable cores is obtained in certain environments

    if (cores_to_use < 1):
        cores_to_use = 1

    return cores_to_use

def get_min_trading_days():
    return MIN_TRADING_DAYS_PER_YEAR, MIN_TRADING_DAYS_FOR_5_YEARS


def get_sh_gscores_df_columns():
    sh_gscores_columns = ('Date', 'Close', 'Price', 'RSI', 'BBANDS', 'MACD', 'KF', 'OLS', 'MFI', 'Stoch', 'SH_gScore', 'NUP', 'A5DUP', 'A20DUP', 'TPC5Y', 'CSL', 'SLS', 'PDSL', 'CRL', 'RLS', 'PDRL', 'DDBTP', 'DPSTP')

    return sh_gscores_columns

def get_sci_gscores_df_columns():
    sci_gscores_columns = ('Options', 'PE', 'PEG', 'Beta', 'PBR', 'QBS', 'IHP', 'Reco', 'Senti', 'SNS', 'SCI_gScore')

    return sci_gscores_columns

def get_trading_bt_columns():
    trading_bt_columns = ('Date', 'Price', 'Action', 'Quantity', 'Avg_Price', 'Profit', 'Return_Pct', 'SP500_Pct', 'Days_Held', 'Last_Price', 'Stage', 'Notes')
    return trading_bt_columns

def get_tool_msg_struct():
    tool_msg_struct = {'Tool': 'None', 'PD': 0}

    return tool_msg_struct

def get_tickers_dir():
    tickers_dir = Path('tickers')
    return tickers_dir

def get_gscores_screening_df_columns():
    gscores_screening_columns = ('Price', 'RSI', 'BBANDS', 'MACD', 'KF', 'OLS', 'MFI', 'Stoch', 'Options', 'Reco', 'Senti')

    return gscores_screening_columns

def get_gscores_results_df_columns():
    gscores_results_columns = ('Ticker', 'sh_gscore', 'sci_gscore', 'final_gscore', 'newshl_sams', 'Note')

    return gscores_results_columns

def get_news_scraper_df_columns():
    news_scraper_df_columns = ('title', 'date', 'link', 'nhss')

    return news_scraper_df_columns

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


def send_msg_to_gui_if_thread(info_queue, tool, data):
    if (info_queue != None):
        tool_msg = get_tool_msg_struct()
        tool_msg['Tool'] = tool
        tool_msg['PD'] = data
        info_queue.put(tool_msg)
        info_queue.join()

#Get list for watchlists (name and path) in current working dir
def get_watchlist_list():

    wl_fp_list = []

    #Get all csv file names with path in current working dir
    fp_list = glob(os.getcwd() + '/*.csv')

    #Extract watchlists (name and paths)
    for file in fp_list:
        #Read the file
        df = pd.read_csv(file)
        #Check if it has only Symbol column
        if ((len(df.columns) == 1) and (df.columns[0] == 'Symbol')):
            #Name with full path
            wl_fp_list.append(file)

    return wl_fp_list


class GUTILS:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('gw_config.ini')

    def get_fg(self):
        fg_data = yf.download('^VIX', period='1d', auto_adjust=True)
        if not fg_data.empty:
            path = get_tickers_dir()
            fg_data.to_csv(path / f'fear_gauge.csv')

    def get_sp500_list(self):

        sp500_list_url = f'https://en.wikipedia.org/wiki/List_of_S&P_500_companies'
        path = get_tickers_dir() / 'SP500'

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

            #Save S&P500 as a watchlist
            sp500.Symbol.to_csv(path / f'SP500_watchlist.csv', index=False)

        return

    def aggregate_scores(self, symbols_list, wl_name):

        #Get the watchlist length
        watchlist_len = len(symbols_list)

        #Get the tickers dir path
        p = get_tickers_dir()

        #Pattern for note
        pattern_for_note = re.compile(r'(Note):([\s]*[A-Z]*[_]*[A-Z]*[_]*[A-Z]*[_]*[A-Z]*[_]*[A-Z]*[_]*[A-Z]*)')

        df_b = pd.DataFrame(columns=get_gscores_results_df_columns(), index=range(watchlist_len))

        i = 0
        for symbol in symbols_list:
            try:
                path = p / f'{symbol}'
                df_gscores = pd.read_csv(path / f'{symbol}_gscores.csv', index_col='Unnamed: 0')
                df_b.loc[i, "Ticker"] = symbol
                df_b.loc[i, "sh_gscore"] = df_gscores.SH_gScore[0]
                df_b.loc[i, "sci_gscore"] = df_gscores.SCI_gScore[0]
                df_b.loc[i, "final_gscore"] = df_gscores.gScore[0]
                df_b.loc[i, "newshl_sams"] = df_gscores.SNS[0]

                f = open(path / f'{symbol}_signal.txt', 'r')
                content = f.read()

                matched_string = pattern_for_note.search(content)
                if (matched_string):
                    kw, note = matched_string.groups()
                    df_b.loc[i, "Note"] = note
                else:
                    df_b.loc[i, "Note"] = ''

                f.close()
                i += 1
            except:
                print('\nERROR: Getting stock signals for ', symbol, ': ', sys.exc_info()[0])

        df_b.sort_values('final_gscore').dropna(how='all').to_csv(p / f'{wl_name}_overall_gscores.csv', index=False)


    def aggregate_pe_data(self):

        path = get_tickers_dir()
        df = pd.read_csv(path / 'SP500/SP500_list.csv')

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
                df_pe.loc[i, "TPE"] = tpe
                df_pe.loc[i, "FPE"] = fpe

            except:
                df_pe.loc[i, "TPE"] = 0
                df_pe.loc[i, "FPE"] = 0

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
            df_pe.loc[start_index:end_index, "LS_AVG_TPE"] = curr_sector_tpe_avg
            df_pe.loc[start_index:end_index, "LS_AVG_FPE"] = curr_sector_fpe_avg


        #New data frame with columns from PE dataframe joined
        df_sp = df_sp.join(df_pe)

        #Drop unwanted fields
        df_sp = df_sp.dropna(axis=0, how='all').drop('Unnamed: 0', axis=1)

        #Rearrange based on ticker symbol
        df_sp = df_sp.sort_values('Symbol')

        #Save for later reference and processing
        df_sp.to_csv(path / 'SP500/SP500_SEC_PES.csv', index=False)

    def get_sp500_closing_data(self):

        path = get_tickers_dir()

        try:
            #SP500 closing data (apparently, start and end defaults aren't working)
            #Specify a start to get more data
            sp500_closing_data = pdd.DataReader('SP500', 'fred', start='1/1/2010')
            sp500_closing_data.rename({'SP500': 'Close'}, axis='columns').dropna().to_csv(path / 'SP500/SP500_history_fred.csv')

            #Get full data for analysis from Yahoo Finance
            gsh.get_sp500_history(path / 'SP500');
        except:
            print('Get SP500 closing data failed')

    def do_sp500_analysis(self):
        #Create a GSA instance
        gsa_instance = gsa.GSA()
        gsa_instance.do_stock_analysis_and_compute_score('SP500', True)

    def get_sp500_actual_return(self, start_date, end_date):

        path = get_tickers_dir()

        try:
            #SP500 closing data from FRED
            sp500_closing_data = pd.read_csv(path / 'SP500/SP500_history_fred.csv')
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
        mtdpy, mtd5y = get_min_trading_days()
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

        if (pp_len < mtd5y):
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

        tickers_dir = get_tickers_dir()

        for tsymbol in symbols_list:
            try:
                path = tickers_dir / f'{tsymbol}'
                try:
                    m5ypep, m5ypep_pct = self.get_5y_ppct(path, tsymbol)
                except:
                    continue

                df_pep.loc[i, "Ticker"] = f'{tsymbol}'
                df_pep.loc[i, "M5YPEP"] = m5ypep
                df_pep.loc[i, "M5YPEP_PCT"] = m5ypep_pct

                i += 1
            except:
                print('\nERROR: extracting estimated projections for ', tsymbol, ': ', sys.exc_info()[0])


        #Back to base dir
        p = tickers_dir

        tsymbol = 'SP500'
        try:
            m5ypep, m5ypep_pct = self.get_5y_ppct(p / f'{tsymbol}', tsymbol)
        except:
            print(f'S&P500 Price projection error')
        else:
            df_pep.loc[i, "Ticker"] = tsymbol
            df_pep.loc[i, "M5YPEP"] = m5ypep
            df_pep.loc[i, "M5YPEP_PCT"] = m5ypep_pct

        #Save a sorted (by return percentage) list for convenient reference
        df_pep.sort_values('M5YPEP_PCT').dropna(how='all').to_csv(p / 'MPEP.csv', index=False)

    def summarize_todays_actions(self, symbols_list):

        #Get today's date
        today = date.today()
        today_year = today.year
        today_month = today.month
        today_day = today.day

        #Create a dataframe to save tickers and their associated actions
        df_actions = pd.DataFrame(columns=['Ticker', 'Price', 'Action', 'Quantity', 'Risk_Appetite', 'Term'], index=range(len(symbols_list)<<1))

        #Init loop params
        term = ('short', 'long')
        risk = ('medium', 'high')

        i = 0

        tickers_dir = get_tickers_dir()
        for tsymbol in symbols_list:
            path = tickers_dir / f'{tsymbol}'
            for iterm in term:
                for risk_level in risk:
                    try:
                        bactesting_st_data = pd.read_csv(path / f'{tsymbol}_gtrades_stats_{iterm}_term_{risk_level}_risk_appetite.csv', index_col='Unnamed: 0')
                        bt_st_data_len = len(bactesting_st_data)
                        last_action_index = bt_st_data_len-2
                        last_action_date = bactesting_st_data.Date.iloc[last_action_index].split(' ')[0].split('-')
                        if ((today_year == int(last_action_date[0])) and (today_month == int(last_action_date[1])) and (today_day == int(last_action_date[2]))):
                            #Today's action
                            df_actions.loc[i, 'Ticker'] = f'{tsymbol}'
                            df_actions.loc[i, 'Price'] = bactesting_st_data.Price.iloc[last_action_index]
                            df_actions.loc[i, 'Action'] = bactesting_st_data.Action.iloc[last_action_index]
                            df_actions.loc[i, 'Quantity'] = bactesting_st_data.Quantity.iloc[last_action_index]
                            df_actions.loc[i, 'Term'] = f'{iterm}_term'
                            df_actions.loc[i, 'Risk_Appetite'] = f'{risk_level}_risk_appetite'
                            i += 1
                    except:
                        print(f'Failed to open {tsymbol}_gtrades_stats_{iterm}_term_{risk_level}_risk_appetite.csv')

        #Back to base dir
        p = tickers_dir

        #Save a sorted (by ticker symbol) list for convenient reference
        df_actions.sort_values('Ticker').dropna(how='all').to_csv(p / 'Todays_Actions.csv', index=False)

        json_data = ''

        if (i):
            json_data = df_actions.drop_duplicates(['Ticker']).truncate(after=(i-1)).to_json(orient='records')

            try:
                ep_url = self.config['webhook']['url']
                ep_api_key = self.config['webhook']['api_key']
                if self.config['webhook']['url']:
                    headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {ep_api_key}'}
                    response = requests.post(ep_url, data=json_data, headers=headers)
                    response.raise_for_status()
                    print('Actions sent to endpoint')
            except requests.exceptions.RequestException as e:
                print(f'Error sending data to endpoint: {e}')
            except:
                print('Webhook not configured. done.')

        return json_data
