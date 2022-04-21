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
# Experimenting with backtesting framework and getting APIs to work; A lot will change later

import sys
from pathlib import Path
import pandas as pd
import numpy
from backtesting import Backtest, Strategy

def getgScoresData(data):
    return numpy.array(data)

class gScoresDataAction(Strategy):

    def init(self):
        #Just placeholder for now
        prices = self.I(getgScoresData, self.data.Close)

    def next(self):
        #Just placeholder for now
        a = None

class GBT:

    def __init__(self):

        self.Tickers_dir = Path('tickers')
        self.SH_GSCORE_MIN_DISCOUNT_LEVEL = 0.375
        self.SH_GSCORE_MIN_PREMIUM_LEVEL = -0.375

    def run_backtest(self, tsymbol):

        try:
            path = self.Tickers_dir / f'{tsymbol}'

            #Read Stock summary info into DataFrame in format necessary for Backtest
            df = pd.read_csv(path / f'{tsymbol}_history.csv', index_col='Date', parse_dates=True)
        except:
            print('\nERROR: Stock history file not found for symbol ', tsymbol)
            return

        #Check API params and compatibility
        backtest = Backtest(df, gScoresDataAction, cash=3000)

        #Check API
        bt_stats = backtest.run()
#        print(bt_stats)

#Quick experiment on gscore APIs for usability in backtesting
#Quick experiment on backtesting module APIs for usability
def main():
    try:
        tsymbol = sys.argv[1]
    except:
        print('ERROR: Need ticker symbol as one argument to this Program.')
        raise ValueError('Missing ticker symbol')

    gbt = GBT()
#    gbt.run_backtest(tsymbol)

if __name__ == '__main__':
    main()
