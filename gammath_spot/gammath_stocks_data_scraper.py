# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works
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
__copyright__ = 'Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works'

import time
import multiprocessing as mp
import threading, queue
try:
    from gammath_spot import gammath_get_stocks_data as ggsd
    from gammath_spot import gammath_utils as gut
except:
    import gammath_get_stocks_data as ggsd
    import gammath_utils as gut
import sys
import pandas as pd

def run_scraper(sf_name, info_queue):
    #Read the watchlist
    try:
        watch_list = pd.read_csv(sf_name)
    except:
        print('ERROR: Failed to read watchlist. See sample_watchlist.csv for example')
        #Update progress bar (if any)
        gut.send_msg_to_gui_if_thread(info_queue, 'Scraper', 0)
        return

    print('\nStart Time: ', time.strftime('%x %X'), '\n')

    try:
        #Instantiate GUTILS class
        gutils = gut.GUTILS()

        #Fetch and save S&P500 list.
        gutils.get_sp500_list()

        #Fetch S&P500 closing data.
        gutils.get_sp500_closing_data()

        #Set the start method for launching parallel processes
        #Python 3.8 onwards 'spawn' is the default method for MacOS and is supported on Linux and Windows
        #so using it for portability. Spawn method is much slower compared to 'fork' method. If there are no unsafe changes made to this project then on MacOS and Linux this can be changed to use 'fork'
        gut.set_child_process_start_method()

        #Get the number of usable CPUs
        cores_to_use = gut.get_usable_cpu_count()

        print(f'\n{cores_to_use} usable CPUs\n')

        proc_handles = []

        max_tickers = len(watch_list)

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
                proc_handles.append(mp.Process(target=gsd_instances[i].get_stocks_data, args=(f'{sym}',)))
                proc_handles[i].start()

                max_tickers -= 1

            for i in range(start_index, end_index):
                proc_handles[i].join()

                #Delete the GSD instance
                gsd_instance = gsd_instances[i]
                gsd_instances[i] = 0
                del gsd_instance

                #Running out of resources so need to close handles and release resources
                proc_handles[i].close()

            #Update progress bar (if any)
            gut.send_msg_to_gui_if_thread(info_queue, 'Scraper', end_index)

            if (max_tickers):
                start_index = end_index
                if (max_tickers > cores_to_use):
                    end_index += cores_to_use
                else:
                    end_index += max_tickers

        #Aggregate and save PE data
        gutils.aggregate_pe_data()
    except:
        print('ERROR: Data scraping failed')

        #Update progress bar (if any)
        gut.send_msg_to_gui_if_thread(info_queue, 'Scraper', 0)

    print('\nEnd Time: ', time.strftime('%x %X'), '\n')

def main():
    """
    Main function to scrape the web and collect data necessary for analyzing and computing gScores for each stock in the provided watchlist. It saves the collected data in tickers/<ticker_symbol> directory.
    """

    #Avoiding to check number of args as if watchlist is not there then there will be an exception anyway
    try:
        #Get the watchlist file from pgm argument
        sf_name = sys.argv[1]
        run_scraper(sf_name, None)
    except:
        print('ERROR: Need watch list file name as one argument to this Program. See sample_watchlist.csv')

class GSCRAPER:
    def __init__(self):
        self.scraper_thread = None

    def launch_scraper_thread(self, watchlist, info_queue):
        self.scraper_thread = threading.Thread(name='Scraper_main_thread', target=run_scraper, args=(watchlist,info_queue,))
        self.scraper_thread.start()

    def scraper_thread_is_alive(self):
        #Check if thread is alive
        if (self.scraper_thread != None):
            alive = self.scraper_thread.is_alive()
        else:
            alive = False

        return alive

if __name__ == '__main__':
    main()
