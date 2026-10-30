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

#Stock screener based on micro-gScores
import argparse
import sys
from pathlib import Path
import pandas as pd
import threading, queue

try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut


def run_screener(sf_name, info_queue):

    complete_pct = 0
    try:
        df_gscores_screening = pd.read_csv(sf_name)

        #extract values for screening
        #-1 means no filtering
        min_options_micro_gscore = df_gscores_screening.Options[0]
        min_fast_micro_gscore = df_gscores_screening.FAST[0]

    except:
        print('INFO: No screening info provided. Using default values')

        #Get all; no filtering
        min_options_micro_gscore = -1
        min_fast_micro_gscore = -1

    #Get ticker dir path
    p = gut.get_tickers_dir()

    #Get all sub-dirs for traversing
    subdirs = [x for x in p.iterdir() if x.is_dir()]

    #Create a data frame for screened watch list
    df_list = pd.DataFrame(columns=['Symbol'], index=range(len(subdirs)))
    count = 0
    for subdir in subdirs:
        if subdir.exists():
            try:
                #Get the saved gscores
                df_gscores = pd.read_csv(subdir / f'{subdir.name}_gscores.csv', index_col='Unnamed: 0')

                #Extract symbols that match screening criteria
                if ((df_gscores.Options[0] >= min_options_micro_gscore) and
                    (df_gscores.FAST[0] >= min_fast_micro_gscore)):

                    #Extract ticker, sh_gscore, sci_gscore and final_gscore for convenient reference
                    df_list.iloc[count] = {"Symbol": f'{subdir.name}'}
                    count += 1
            except:
                #No action necessary
                continue

    if (count):
        #Remove unused rows and sort by final_gscore
        df_list = df_list.truncate(after=(count-1)).sort_values('Symbol')

    #Save screened watchlist without the index field
    df_list.to_csv(p / 'screened_watchlist.csv', index=False)

    complete_pct = 100

    #Update progress bar (if any)
    gut.send_msg_to_gui_if_thread(info_queue, 'Screener', complete_pct)

def main():

    """
    Main function to screen stocks for buy criteria based on micro-gScores.
    The screened list is saved in tickers/screened_watchlist.csv.
    """

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("screener", help="A CSV file as screening criteria. e.g. screener.csv")
        args = parser.parse_args()

        #Get the watchlist file from pgm argument
        sf_name = args.screener
        run_screener(sf_name, None)
    except:
        print('ERROR: Need screener file name as one argument to this Program. See screener.csv')

class GSCREENER:

    def __init__(self):
        self.screener_thread = None

    def launch_screener_thread(self, screener, info_queue):
        self.screener_thread = threading.Thread(name='Screener_main_thread', target=run_screener, args=(screener,info_queue,))
        self.screener_thread.start()

    def screener_thread_is_alive(self):
        #Check if thread is alive
        if (self.screener_thread != None):
            alive = self.screener_thread.is_alive()
        else:
            alive = False

        return alive

if __name__ == '__main__':
    main()
