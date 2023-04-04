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
    from gammath_spot import gammath_backtesting as gbt
    from gammath_spot import gammath_utils as gut
except:
    import gammath_backtesting as gbt
    import gammath_utils as gut
import pandas as pd
import sys

def run_backtester(sf_name, info_queue):
    #Read the watchlist
    try:
        watch_list = pd.read_csv(sf_name)
    except:
        print('ERROR: Failed to read watchlist. See sample_watchlist.csv for example')

        #Update progress bar (if any)
        gut.send_msg_to_gui_if_thread(info_queue, 'Backtester', 0)
        return

    print('\nStart Time: ', time.strftime('%x %X'), '\n')

    try:
        #Set the start method for launching parallel processes
        #Python 3.8 onwards 'spawn' is the default method for MacOS and is supported on Linux and Windows
        #so using it for portability. Spawn method is much slower compared to 'fork' method. If there are no unsafe changes made to this project then on MacOS and Linux this can be changed to use 'fork'
        gut.set_child_process_start_method()

        #Get the number of usable CPUs
        cores_to_use = gut.get_usable_cpu_count()

        print(f'\n{cores_to_use} usable CPUs\n')

        proc_handles = []

        max_tickers = len(watch_list)

        #Use one process per core so we can run core_to_use number of processes in parallel
        start_index = 0
        if (max_tickers > cores_to_use):
            end_index = cores_to_use
        else:
            end_index = max_tickers

        #Instances of GBT class
        gbt_instances = []
        symbols_list = []

        while (max_tickers):
            for i in range(start_index, end_index):
                sym = watch_list['Symbol'][i].strip()
                tsymbol = f'{sym}'
                symbols_list.append(tsymbol)

                gbt_instances.append(gbt.GBT())
                proc_handles.append(mp.Process(target=gbt_instances[i].run_backtest, args=(f'{sym}',)))
                proc_handles[i].start()

                max_tickers -= 1

            for i in range(start_index, end_index):
                proc_handles[i].join()

                #Delete the GBT instance
                gbt_instance = gbt_instances[i]
                gbt_instances[i] = 0
                del gbt_instance

                #Running out of resources so need to close handles and release resources
                proc_handles[i].close()

            #Update progress bar (if any)
            gut.send_msg_to_gui_if_thread(info_queue, 'Backtester', end_index)

            if (max_tickers):
                start_index = end_index
                if (max_tickers > cores_to_use):
                    end_index += cores_to_use
                else:
                    end_index += max_tickers

        #Instantiate GUTILS class
        gutils = gut.GUTILS()

        #Summarize today's actions
        gutils.summarize_todays_actions(symbols_list)
    except:
        print('ERROR: Backtesting failed')
        #Update progress bar (if any)
        gut.send_msg_to_gui_if_thread(info_queue, 'Backtester', 0)

    print('\nEnd Time: ', time.strftime('%x %X'), '\n')


def main():
    """
    Main function to do backtesting on provided watchlist. For each stock, it processes (based on a strategy you implement/use) the data collected by scraper app and processes the stock history based gScore/micro-gScores for approximately last 5 years that from the gscore historian and saves the backtesting stats in respective in tickers/<ticker_symbol>/<ticker_symbol>_bt_stats.csv
    """

    #Avoiding to check number of args as if watchlist is not there then there will be an exception anyway
    try:
        #Get the watchlist file from pgm argument
        sf_name = sys.argv[1]
        run_backtester(sf_name, None)
    except:
        print('ERROR: Need watch list file name as one argument to this Program. See sample_watchlist.csv')


class GBACKTESTER:
    def __init__(self):
        self.backtester_thread = None

    def launch_backtester_thread(self, watchlist, info_queue):
        self.backtester_thread = threading.Thread(name='Backtester_main_thread', target=run_backtester, args=(watchlist,info_queue,))
        self.backtester_thread.start()

    def backtester_thread_is_alive(self):
        #Check if thread is alive
        if (self.backtester_thread != None):
            alive = self.backtester_thread.is_alive()
        else:
            alive = False

        return alive


if __name__ == '__main__':
    main()
