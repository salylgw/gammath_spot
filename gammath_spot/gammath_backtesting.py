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

# THIS IS WIP: DO NOT USE
# Experimenting with backtesting framework and getting APIs to work

import sys
from pathlib import Path
import pandas as pd
import numpy
from backtesting import Backtest, Strategy

#This is work-in-progress; DO NOT USE
# Just getting all pieces to work before actually using a strategy
class gScoresDataAction(Strategy):

    def init(self):
        self.min_sh_premium_level = -0.375
        self.min_sh_discount_level = 0.375
        self.previous_close = 0
        self.total_shares = 0
        self.total_cost = 0

    def next(self):
        #Following is just experiment to iterate through all data with backtesting framework
        #Not for use as a strategy
        #You can implement your own strategy here
        curr_sh_gscore = self.data.Total[-1]
        curr_closing_price = self.data.Close[-1]

        if (self.previous_close):
            if (curr_sh_gscore >= self.min_sh_discount_level):
                if (curr_closing_price > self.previous_close):
                    self.position.close()
                    self.buy()

            if (curr_sh_gscore <= self.min_sh_premium_level):
                if (curr_closing_price < self.previous_close):
                    self.position.close()
                    self.sell()

        self.previous_close = curr_closing_price

class GBT:

    def __init__(self):

        self.Tickers_dir = Path('tickers')

    def run_backtest(self, tsymbol):

        MIN_TRADING_DAYS_FOR_5_YEARS = 249*5
        try:
            path = self.Tickers_dir / f'{tsymbol}'

            #We only need last 5y data
            df_orig = pd.read_csv(path / f'{tsymbol}_history.csv')
            df_len = len(df_orig)
            start_index = df_len - MIN_TRADING_DAYS_FOR_5_YEARS
            if (start_index < 0):
                raise ValueError('Not enough stock history')
            end_index = df_len
            df = df_orig.copy()
            df.iloc[0:MIN_TRADING_DAYS_FOR_5_YEARS] = df_orig.iloc[start_index:end_index]
            df = df.truncate(after=MIN_TRADING_DAYS_FOR_5_YEARS-1)
            #Read the gscores history into dataframe
            df_gscores_history = pd.read_csv(path / f'{tsymbol}_micro_gscores.csv', index_col='Unnamed: 0')
            #Generate the dataframe that has stock history and gscores history
            df = df.join(df_gscores_history)
            df.Date = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
        except:
            print('\nERROR: Stock history file not found for symbol ', tsymbol)
            return

        #Check API params and compatibility
        backtest = Backtest(df, gScoresDataAction, cash=20000)

        #Check API
        bt_stats = backtest.run()
        print(bt_stats)

#Quick experiment on gscore APIs for usability in backtesting
#Quick experiment on backtesting module APIs for usability
def main():
    try:
        tsymbol = sys.argv[1]
    except:
        print('ERROR: Need ticker symbol as one argument to this Program.')
        raise ValueError('Missing ticker symbol')

    gbt = GBT()
    gbt.run_backtest(tsymbol)

if __name__ == '__main__':
    main()
