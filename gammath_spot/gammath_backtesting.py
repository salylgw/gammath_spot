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

#Set this based on gScores history for specific stocks. This default setting is generic and may have to be tailored for specific stocks
MIN_SH_PREMIUM_LEVEL = -0.375
MIN_SH_DISCOUNT_LEVEL = 0.375

MIN_TRADING_DAYS_FOR_5_YEARS = 249*5

#Following is a basic example of writing your own strategy for backtesting
#This is just provided as an example to show one of the ways to do it
#Remeber, sell criteria is subjective. The method used here could be a way out of a position if one decides to get out; Otherwise, it is not mandatory to sell if one is confident of long-term prospects
def run_basic_backtest(df, path, tsymbol):

    #Create a data frame to save the stats
    df_transactions = pd.DataFrame(columns=['Date', 'Buy_Q', 'Sell_Q', 'sh_gScore', 'Price', 'Avg_Price', 'Profit', 'PCT', 'Days_held'], index=range(MIN_TRADING_DAYS_FOR_5_YEARS))

    history_len = len(df)

    total_shares = 0
    total_cost = 0
    avg_price = 0
    transactions_count = 0
    days_held = 0
    profit = 0
    buy_q = 0
    marked_for_sell = False

    for i in range(1, history_len):
        curr_sh_gscore = df.Total[i]
        curr_ols_gscore = df.OLS[i]
        curr_closing_price = df.Close[i]
        previous_closing_price = df.Close[i-1]

        if ((curr_sh_gscore >= MIN_SH_DISCOUNT_LEVEL) or (total_shares and (curr_sh_gscore >= 0))):

            marked_for_sell = False
            if (((curr_closing_price < avg_price) or (not avg_price)) and (curr_closing_price > previous_closing_price)): #Check if lower than our avg buying price and rising

                #Mimic a buy
                buy_q = 1

                #If it is below "expected" average then buy more
                if (curr_ols_gscore > 0):
                    buy_q += 1

                #If it fits better and well below "expected" average then buy more
                if (curr_ols_gscore > 0.5):
                    buy_q += 1

                #If it fits better and significantly below "expected" average then buy more
                if (curr_ols_gscore == 1.0):
                    buy_q += 1

                total_shares += buy_q
                total_cost += (curr_closing_price*buy_q)
                df_transactions['Date'][transactions_count] = df.Date[i]
                df_transactions['Buy_Q'][transactions_count] = buy_q
                df_transactions['sh_gScore'][transactions_count] = curr_sh_gscore
                df_transactions['Price'][transactions_count] = round(curr_closing_price, 3)
                avg_price = total_cost/total_shares
                df_transactions['Avg_Price'][transactions_count] = round(avg_price, 3)
                transactions_count += 1


        if (((curr_sh_gscore <= MIN_SH_PREMIUM_LEVEL) and total_shares) or marked_for_sell):

            marked_for_sell = True
            if (curr_closing_price < df.Close[i-1]): #Check if falling
                total_cash = (total_shares * curr_closing_price)
                if (total_cost < total_cash):
                    #Mimic sale
                    profit = total_cash - total_cost
                    df_transactions['Date'][transactions_count] = df.Date[i]
                    df_transactions['Sell_Q'][transactions_count] = total_shares
                    df_transactions['sh_gScore'][transactions_count] = curr_sh_gscore
                    df_transactions['Price'][transactions_count] = round(curr_closing_price, 3)
                    df_transactions['Avg_Price'][transactions_count] = round(avg_price, 3)
                    df_transactions['Profit'][transactions_count] = round(profit, 3)
                    df_transactions['PCT'][transactions_count] = round(((profit*100)/total_cost), 3)
                    df_transactions['Days_held'][transactions_count] = days_held
                    transactions_count += 1
                    total_shares = 0
                    total_cost = 0
                    days_held = 0
                    avg_price = 0
                    profit = 0
                    total_cash = 0
                    marked_for_sell = 0

        if (total_shares):
            days_held += 1

    df_transactions = df_transactions.truncate(after=transactions_count-1)
    df_transactions.to_csv(path / f'{tsymbol}_gtrades_stats.csv')

#Get the main stock history based gScores
def extractGscores(data):
    return data.Total

#Implement your own strategy in this class
class gScoresDataAction(Strategy):

    def init(self):
        self.min_sh_premium_level = -0.375
        self.min_sh_discount_level = 0.375
        self.previous_close = 0
        self.total_shares = 0
        self.total_cost = 0
        self.sh_gScore = self.I(extractGscores, self.data)

    def next(self):
        #Following is provided to make it easier for you to implement your own strategy using the gScore and micro-gScores
        curr_sh_gscore = self.sh_gScore[-1]
        curr_closing_price = self.data.Close[-1]

        #You can use multiple micro-gScores from self.data.<micro-gScore>

        # Following is provided as an example of using this backtesting framework
        # Typical way is to check the charts from gscores historian to correlate gScore and micro-gScores with price
        # Then use those correlated fields in your own strategy
        # Then check the backtesting stats on how well your strategy did
        # If it shows your desired success rate then one can choose to execute on that strategy

        # Following shows how to use the APIs. Following is not a strategy.
        # Actual strategy will need to be implemented
#        if (self.previous_close):
#            if (curr_sh_gscore >= self.min_sh_discount_level):
#                if (curr_closing_price > self.previous_close):
#                    self.buy()

#            if (curr_sh_gscore <= self.min_sh_premium_level):
#                if (curr_closing_price < self.previous_close):
#                    self.sell()

        self.previous_close = curr_closing_price

class GBT:

    def __init__(self):

        self.Tickers_dir = Path('tickers')

    def run_backtest(self, tsymbol):

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
        except:
            print('\nERROR: Backtesting data initialization failed for symbol ', tsymbol)
            return


        #You can call your own backtesting function here. Following is a basic example
        run_basic_backtest(df, path, tsymbol)

        #Following is done to make it easier to use this with backtesting python framework
#        df.Date = pd.to_datetime(df['Date'])
#        df = df.set_index('Date')

        #Instantiate Backtest
#        backtest = Backtest(df, gScoresDataAction, cash=20000)

        #Back test the strategy using our dataframe
#        bt_stats = backtest.run()

        #Save it for later reference
#        bt_stats.to_csv(path / f'{tsymbol}_bt_stats.csv')
