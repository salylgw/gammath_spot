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
import yfinance as yf
from matplotlib import pyplot as plt
try:
    from gammath_spot import gammath_stocks_analysis as gsa
except:
    import gammath_stocks_analysis as gsa

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

    def get_gscores_history(self, tsymbol):

        path = self.Tickers_dir / f'{tsymbol}'

        #Placeholder for all micro-gScore data frames
        df_gscores = pd.DataFrame()

        try:
            MIN_TRADING_DAYS_FOR_5YEARS = 249*5
            #Read Stock summary info into DataFrame
            df = pd.read_csv(path / f'{tsymbol}_history.csv')
            initial_end_index = len(df) - MIN_TRADING_DAYS_FOR_5YEARS
            initial_start_index = initial_end_index - MIN_TRADING_DAYS_FOR_5YEARS

            if (initial_start_index < 0):
                print('\nERROR: gscores history failed for symbol ', tsymbol)
                ValueError('Insufficient stock history')

            #Use a different df for starting with 0-index
            df1 = df.copy()

            #Brute force (initial experiment; optimize later) for now to run through entire history
            for i in range(MIN_TRADING_DAYS_FOR_5YEARS):
                gsa_instance = gsa.GSA()
                df1.iloc[0:MIN_TRADING_DAYS_FOR_5YEARS] = df.iloc[initial_start_index+i:initial_end_index+i]
                df_micro_gscores = gsa_instance.do_stock_history_analysis(tsymbol, path, df1[0:MIN_TRADING_DAYS_FOR_5YEARS])

                #Get the columns from micro gscores df
                if not len(df_gscores):
                    df_gscores = pd.DataFrame(columns=df_micro_gscores.columns, index=range(MIN_TRADING_DAYS_FOR_5YEARS))

                df_gscores.iloc[i] = df_micro_gscores

            #Save gscores history
            df_gscores.to_csv(path / f'{tsymbol}_micro_gscores.csv')

            #Draw the charts to view a rough sketch; Lot will change
            figure, axes = plt.subplots(nrows=2, figsize=(21, 19))
            closing_prices_df = pd.DataFrame({tsymbol: df1.Close[0:MIN_TRADING_DAYS_FOR_5YEARS]})
            closing_prices_df.plot(ax=axes[0],lw=1,title='Stock history')
            sh_gscores_df = pd.DataFrame({'SH_gscores': df_gscores.Total[0:MIN_TRADING_DAYS_FOR_5YEARS]})
            sh_gscores_df.plot(ax=axes[1],lw=1,title='Stock History based gScores')
            axes[1].axhline(self.SH_GSCORE_MIN_DISCOUNT_LEVEL,lw=1,ls='-',c='r')
            axes[1].axhline(self.SH_GSCORE_MIN_PREMIUM_LEVEL,lw=1,ls='-',c='r')
            plt.savefig(path / f'{tsymbol}_gscores_charts.png')
            return df_gscores
        except:
            print('\nERROR: gscores history failed for symbol ', tsymbol)
            return df_gscores

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
    df_gscores_history = gbt.get_gscores_history(tsymbol)

if __name__ == '__main__':
    main()
