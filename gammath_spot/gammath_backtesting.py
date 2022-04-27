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

# THIS IS PROVIDED TO MAKE IT EASY FOR BACKTESTING
# Users will need to implement their own strategy in the gScoresDataAction class

import sys
from pathlib import Path
import pandas as pd
import numpy
from backtesting import Backtest, Strategy

#Implement your own strategy in this class
class gScoresDataAction(Strategy):

    def init(self):
        self.min_sh_premium_level = -0.375
        self.min_sh_discount_level = 0.375
        self.previous_close = 0
        self.total_shares = 0
        self.total_cost = 0

    def next(self):
        #Following is provided to make it easier for you to implement your strategy
        curr_sh_gscore = self.data.Total[-1]
        curr_closing_price = self.data.Close[-1]
        #You can use multiple micro-gScores from self.data.<micro-gScore>

        # Following is provided as an example of using this framework
        # Typical way is to check the charts from gscores historian to correlate different params
        # Then use those correlated fields in your strategy
        # Then check the backtesting stats on how well your strategy did

        #Following shows how to use the APIs. Actual strategy will need to be implemented
#        if (self.previous_close):
#            if (curr_sh_gscore >= self.min_sh_discount_level):
#                if (curr_closing_price > self.previous_close):
#                    self.position.close()
#                    self.buy()

#            if (curr_sh_gscore <= self.min_sh_premium_level):
#                if (curr_closing_price < self.previous_close):
#                    self.position.close()
#                    self.sell()

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

        #Instantiate Backtest
        backtest = Backtest(df, gScoresDataAction, cash=20000)

        #Back test the strategy using our dataframe
        bt_stats = backtest.run()

        #Save it for later reference
        bt_stats.to_csv(path / f'{tsymbol}_bt_stats.csv')
