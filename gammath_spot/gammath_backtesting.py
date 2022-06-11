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

#Default values
MIN_SH_PREMIUM_LEVEL = -0.375
NEUTRAL_SH_PREMIUM_LEVEL = -0.375
MIN_SH_DISCOUNT_LEVEL = 0.375

MIN_TRADING_DAYS_FOR_5_YEARS = 249*5

#Following is a basic example of writing your own strategy for backtesting
#This is just provided as an example to show one of the ways to do it
#Remeber, sell criteria is subjective. The method used here could be a way out of a position if one decides to get out; Otherwise, it is not mandatory to sell if one is confident of long-term prospects
#It is generally expected that in reality, execution of gScore-based dollar cost averaging would be better than what is used in backtesting since this does not account of news analysis and current information. As described in the guidelines, one would check the news before making buy/sell decisions
def run_basic_backtest(df, path, tsymbol):

    #Create a data frame to save the stats
    df_transactions = pd.DataFrame(columns=['Date', 'Buy_Q', 'Sell_Q', 'sh_gScore', 'Price', 'Avg_Price', 'Profit', 'PCT', 'Days_held', 'Last_Price', 'Stage', 'Notes'], index=range(MIN_TRADING_DAYS_FOR_5_YEARS))

    history_len = len(df)

    total_shares = 0
    total_cost = 0
    avg_price = 0
    transactions_count = 0
    days_held = 0
    profit = 0
    buy_q = 0
    marked_for_buy = False
    marked_for_sell = False
    cycle = ''

    #Use percentile levels to determine discount, neutral and premium levels
    #This should cover a broad range of stocks and then can be customized and fine tuned for variety of criteria
    MIN_SH_PREMIUM_LEVEL, NEUTRAL_SH_PREMIUM_LEVEL, MIN_SH_DISCOUNT_LEVEL = df.Total.quantile([0.20, 0.5, 0.80])

    for i in range(2, history_len):
        curr_sh_gscore = df.Total[i]
        curr_ols_gscore = df.OLS[i]
        curr_closing_price = df.Close[i]
        prev_closing_price = df.Close[i-1]

        if ((curr_sh_gscore >= MIN_SH_DISCOUNT_LEVEL) or (total_shares and (curr_sh_gscore >= NEUTRAL_SH_PREMIUM_LEVEL))):

            marked_for_sell = False
            marked_for_buy = True
            #Basic conservative approach; This should be customized for your own check for bottom
            if (((curr_closing_price < avg_price) or (not avg_price)) and ((curr_closing_price > prev_closing_price) and (prev_closing_price > df.Close[i-2]))): #Check if lower than our avg buying price and rising [for two concecutive days]

                #Mimic a buy; In reality, buy quantity can also be 0.1 if your broker support dollar based investing and fractional shares buy/sell
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
        else:
            marked_for_buy = False


        if (((curr_sh_gscore <= MIN_SH_PREMIUM_LEVEL) and total_shares) or marked_for_sell):
            marked_for_buy = False
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
        else:
            marked_for_sell = False

        if (total_shares):
            days_held += 1

    df_sci = pd.read_csv(path / f'{tsymbol}_gscores.csv', index_col='Unnamed: 0')
    if (df_sci.SCI_Total[0] <= 0):
        note = f'Current_info_data_overall_negative'
    else:
        note = f'Current_info_data_overall_positive'

    #Show last closing price for convenience
    df_transactions.Last_Price[transactions_count] = round(curr_closing_price, 3)

    #Check current stage (buy/sell/hold cycle) of our strategy execution
    if (marked_for_buy):
        cycle = 'Buy_cycle'
    elif (marked_for_sell):
        cycle = 'Sell_cycle'
    else:
        cycle = 'Hold_cycle'

    df_transactions.Stage[transactions_count] = cycle
    df_transactions.Notes[transactions_count] = note
    df_transactions = df_transactions.truncate(after=transactions_count)
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
            #Debug code
#            for i in range(len(df)):
#                if (df_gscores_history.Date[i] != df.Date[i]):
#                    raise ValueError('gScores and price history dates mismatch')

            #Generate the dataframe that has stock history and gscores history
            df = df_gscores_history.join(df.Close)
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
