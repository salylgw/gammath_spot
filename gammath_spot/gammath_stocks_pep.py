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
    from gammath_spot import gammath_lpep as glpep
    from gammath_spot import gammath_utils as gut
except:
    import gammath_lpep as glpep
    import gammath_utils as gut
import pandas as pd
import sys
import os

def run_projector(sf_name, info_queue):

    #Read the watchlist
    try:
        watch_list = pd.read_csv(sf_name)
    except:
        print('ERROR: Failed to read watchlist. See sample_watchlist.csv for example')
        #Update progress bar (if any)
        gut.send_msg_to_gui_if_thread(info_queue, 'Projector', 0)
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

        #Instances of GPEP class
        gpep_instances = []
        symbols_list = []

        while (max_tickers):
            for i in range(start_index, end_index):

                sym = watch_list['Symbol'][i].strip()
                tsymbol = f'{sym}'
                symbols_list.append(tsymbol)
                gpep_instances.append(glpep.GPEP())
                proc_handles.append(mp.Process(target=gpep_instances[i].get_moving_price_estimated_projection, args=(f'{sym}',)))
                proc_handles[i].start()

                max_tickers -= 1

            for i in range(start_index, end_index):
                proc_handles[i].join()

                #Delete the GPEP instance
                gpep_instance = gpep_instances[i]
                gpep_instances[i] = 0
                del gpep_instance

                #Running out of resources so need to close handles and release resources
                proc_handles[i].close()

            #Update progress bar (if any)
            gut.send_msg_to_gui_if_thread(info_queue, 'Projector', end_index)

            if (max_tickers):
                start_index = end_index
                if (max_tickers > cores_to_use):
                    end_index += cores_to_use
                else:
                    end_index += max_tickers

        #Instantiate GUTILS class
        gutils = gut.GUTILS()

        #Generate 5Y estimated projection for S&P500
        gpep = glpep.GPEP()

        #Run S&P500 projection in its own process (for matplotlib main thread issue)
        sp500_pep_handle = mp.Process(target=gpep.sp500_pep)
        sp500_pep_handle.start()
        sp500_pep_handle.join()
        sp500_pep_handle.close()

        #Aggregate a sorted list of moving 5Y estimated projected returns
        gutils.aggregate_peps(symbols_list)

        #Update progress bar (if any)
        gut.send_msg_to_gui_if_thread(info_queue, 'Projector', (end_index+1))
    except:
        print('ERROR: Price estimation and projection failed')
        #Update progress bar (if any)
        gut.send_msg_to_gui_if_thread(info_queue, 'Projector', 0)

    print('\nEnd Time: ', time.strftime('%x %X'), '\n')

def main():
    """
    Main function to compute stock's price estimate and price projection. The estimate and projection charts are saved in tickers/<ticker_symbol>/<ticker_symbol>_pep.png. The price projection values are saved in tickers/<ticker_symbol>/<ticker_symbol>_pp.csv.
    """

    #Avoiding to check number of args as if watchlist is not there then there will be an exception anyway
    try:
        #Get the watchlist file from pgm argument
        sf_name = sys.argv[1]
        run_projector(sf_name, None)
    except:
        print('ERROR: Need watch list file name as one argument to this Program. See sample_watchlist.csv')


class GPROJECTOR:
    def __init__(self):
        self.projector_thread = None

    def launch_projector_thread(self, watchlist, info_queue):
        self.projector_thread = threading.Thread(name='Projector_main_thread', target=run_projector, args=(watchlist,info_queue,))
        self.projector_thread.start()

    def projector_thread_is_alive(self):
        #Check if thread is alive
        if (self.projector_thread != None):
            alive = self.projector_thread.is_alive()
        else:
            alive = False

        return alive

if __name__ == '__main__':
    main()
