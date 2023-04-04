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
    from gammath_spot import gammath_stocks_analysis as gsa
    from gammath_spot import gammath_utils as gut
except:
    import gammath_stocks_analysis as gsa
    import gammath_utils as gut
import pandas as pd
import sys

def run_analyzer_and_scorer(sf_name, info_queue):

    #Read the watchlist
    try:
        watch_list = pd.read_csv(sf_name)
    except:
        print('ERROR: Failed to read watchlist. See sample_watchlist.csv for example')

        #Update progress bar (if any)
        gut.send_msg_to_gui_if_thread(info_queue, 'Scorer', 0)
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

        #Instances of GSA class
        gsa_instances = []

        #Create symbols list
        symbols_list = []

        while (max_tickers):
            for i in range(start_index, end_index):
                sym = watch_list['Symbol'][i].strip()
                tsymbol = f'{sym}'
                symbols_list.append(tsymbol)
                df_history = pd.DataFrame()

                gsa_instances.append(gsa.GSA())
                proc_handles.append(mp.Process(target=gsa_instances[i].do_stock_analysis_and_compute_score, args=(f'{sym}',df_history,)))
                proc_handles[i].start()

                max_tickers -= 1

            for i in range(start_index, end_index):
                proc_handles[i].join()
                #Delete the GSA instance
                gsa_instance = gsa_instances[i]
                gsa_instances[i] = 0
                del gsa_instance

                #Running out of resources so need to close handles and release resources
                proc_handles[i].close()

            #Update progress bar (if any)
            gut.send_msg_to_gui_if_thread(info_queue, 'Scorer', end_index)

            if (max_tickers):
                start_index = end_index
                if (max_tickers > cores_to_use):
                    end_index += cores_to_use
                else:
                    end_index += max_tickers


        #Instantiate GUTILS class
        gutils = gut.GUTILS()

        #Aggregate scores and generate a gscores summary
        gutils.aggregate_scores(symbols_list, sf_name.split('.')[0])
    except:
        print('ERROR: Analysis and Scoring failed')

        #Update progress bar (if any)
        gut.send_msg_to_gui_if_thread(info_queue, 'Scorer', 0)

    print('\nEnd Time: ', time.strftime('%x %X'), '\n')

def main():
    """
    Main function to analyze and compute score for each stock in the provided watchlist. For each stock, it processes the data collected by scraper app, computes the score and saves score and useful signals in tickers/<ticker_symbol>. List of all gScores is in tickers/<watchlist_name>_overall_gscores.csv
    """

    #Avoiding to check number of args as if watchlist is not there then there will be an exception anyway
    try:
        #Get the watchlist file from pgm argument
        sf_name = sys.argv[1]

        run_analyzer_and_scorer(sf_name, None)
    except:
        print('ERROR: Need watch list file name as one argument to this Program. See sample_watchlist.csv')

class GSCORER:
    def __init__(self):
        self.analyzer_and_scorer_thread = None

    def launch_analyzer_and_scorer_thread(self, watchlist, info_queue):
        self.analyzer_and_scorer_thread = threading.Thread(name='AnSc_main_thread', target=run_analyzer_and_scorer, args=(watchlist,info_queue,))
        self.analyzer_and_scorer_thread.start()

    def analyzer_and_scorer_thread_is_alive(self):
        #Check if thread is alive
        if (self.analyzer_and_scorer_thread != None):
            alive = self.analyzer_and_scorer_thread.is_alive()
        else:
            alive = False

        return alive

if __name__ == '__main__':
    main()
