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
# Users will need to implement their own strategy in the gScoresDataAction class or in run_basic_backtest function

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

#Default values
MIN_SH_PREMIUM_LEVEL = -0.375
NEUTRAL_SH_PREMIUM_LEVEL = -0.375
MIN_SH_DISCOUNT_LEVEL = 0.375

MIN_TRADING_DAYS_FOR_5_YEARS = 249*5

#Following is a basic example of writing your own strategy for backtesting
#This is just provided as an example to show one of the ways to do it
#Remember, sell criteria is subjective. The methods shown here could be a way out of a position if one decides to get out; It is not meant to be mandatory sell decision. If one is confident of long-term prospects and if the stock does actually do well then perhaps buy and hold might turn out to be the best strategy
#It is generally expected that in reality, execution of gScore-based dollar cost averaging would be better than what is used in backtesting since this does not account of news analysis and current information that is used in decision-making. As described in the guidelines, one would check the news before making buy/sell decisions
def run_basic_backtest(df, path, tsymbol, term):

    #Create a data frame to save the stats
    df_transactions = pd.DataFrame(columns=['Date', 'Action', 'Buy_Q', 'Sell_Q', 'sh_gScore', 'Price', 'Avg_Price', 'Profit', 'PCT', 'Days_held', 'Last_Price', 'Stage', 'Notes'], index=range(MIN_TRADING_DAYS_FOR_5_YEARS))

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
    buy_now = False
    sell_now = False
    cycle = ''
    note = ''
    sp500_comp_string = ''
    sci_note = ''
    pp_note = ''

    #Instantiate GUTILS class
    gutils = gut.GUTILS()

    #Use percentile levels to determine discount, neutral and premium levels
    #This should cover a broad range of stocks and then can be customized and fine tuned for variety of criteria
    MIN_SH_PREMIUM_LEVEL, NEUTRAL_SH_PREMIUM_LEVEL, MIN_SH_DISCOUNT_LEVEL = df.SH_Total.quantile([0.20, 0.5, 0.80])

    #Get the low and high percentiles for next day up/down probability
    nup_bp, nup_tp = df.NUP.quantile([0.1, 0.9])
    ndp_tp = round((1 - nup_bp), 3)
    last_buy_5y_price_ratio = 0

    for i in range(2, history_len):
        curr_sh_gscore = df.SH_Total[i]
        curr_kf_gscore = df.KF[i]
        curr_ols_gscore = df.OLS[i]
        curr_macd_gscore = df.MACD[i]
        curr_mfi_gscore = df.MFI[i]
        prev_closing_price = df.Close[i-1]
        curr_closing_price = df.Close[i]
        prev_nup = df.NUP[i-1]
        curr_nup = df.NUP[i]
        curr_ndp = round(1 - curr_nup, 3)
        prev_ndp = round(1- prev_nup, 3)
        curr_tpc5y = df.TPC5Y[i]

        #Use this ratio to compare
        curr_5y_price_ratio = (curr_tpc5y/curr_closing_price)
        last_buy_5y_price_ratio = 0

        #Look for discount zone entry or if it is still in the "buy zone"
        if (((curr_sh_gscore >= MIN_SH_DISCOUNT_LEVEL) or (total_shares and (curr_sh_gscore >= NEUTRAL_SH_PREMIUM_LEVEL)))):

            marked_for_sell = False
            marked_for_buy = True
            buy_now = False

            #Check if rising for at least a day
            single_day_rising = (curr_closing_price > prev_closing_price)

            # We only want to buy when price is is below our current average price
            if (total_shares and (curr_closing_price > avg_price)):
                buy_now = False
            else:
                if (term == 'short_term'):
                    #Check if rising for two concecutive days
                    consec_two_days_rising = (single_day_rising and (prev_closing_price > df.Close[i-2]))
                    if (consec_two_days_rising):
                        # For short-term, we want to buy when we see two consecutive up days
                        buy_now = True
                elif (term == 'long_term'):
                    #For long-term, we want to buy on up day that follows multiple down days (we look at previous day's next day up probability to gauge that)
                    # If we are buying for long-term, check for reasonable 5Y return conjecture
                    if ((prev_nup >= nup_tp) and (single_day_rising) and (curr_5y_price_ratio >= 1.5)):
                        buy_now = True
                        #Save this for comparison for sell-side check
                        last_buy_5y_price_ratio = curr_5y_price_ratio

            if (buy_now):
                buy_q += 1

                if ((curr_ols_gscore >= 0.5) and (curr_kf_gscore >= 0.5) and (curr_macd_gscore >= 0.5) and (curr_mfi_gscore >= 0.3)):
                    buy_q += 1

                if ((curr_ols_gscore == 1.0) and (curr_kf_gscore >= 0.9) and (curr_macd_gscore == 1.0) and (curr_mfi_gscore >= 0.7)):
                    buy_q += 1

            if (buy_q):
                total_shares += buy_q
                total_cost += (curr_closing_price*buy_q)
                df_transactions['Date'][transactions_count] = df.Date[i]
                df_transactions['Action'][transactions_count] = 'BUY'
                df_transactions['Buy_Q'][transactions_count] = buy_q
                df_transactions['sh_gScore'][transactions_count] = curr_sh_gscore
                df_transactions['Price'][transactions_count] = round(curr_closing_price, 3)
                avg_price = total_cost/total_shares
                df_transactions['Avg_Price'][transactions_count] = round(avg_price, 3)
                transactions_count += 1
                buy_q = 0
        else:
            marked_for_buy = False
            buy_now = False


        #Check for premium level
        if (((curr_sh_gscore <= MIN_SH_PREMIUM_LEVEL) and total_shares) or marked_for_sell):
            marked_for_buy = False
            marked_for_sell = True
            sell_now = False

            total_cash = (total_shares * curr_closing_price)
            profit = total_cash - total_cost
            profit_pct = round(((profit*100)/total_cost), 3)

            #Check if in profit
            if (total_cost < total_cash):
                #Check if price has fallen for two consecutive days
                consec_two_days_falling = ((curr_closing_price < prev_closing_price) and (prev_closing_price < df.Close[i-2]))

                #Check if falling for two consecutive days
                if (consec_two_days_falling):
                    if (term == 'short_term'):
                        #For short-term: just sell
                        sell_now = True
                    elif (term == 'long_term'):
                        #For long-term, we need more checks
                        sell_now = False

                        #If we already doubled then just sell irrespective of holding period
                        if (profit_pct > 100):
                            sell_now = True
                        elif ((curr_5y_price_ratio < 2) and (curr_5y_price_ratio < last_buy_5y_price_ratio)):
                            #If it doesn't seem to be doubling in 5 years and if our buy-time 5y price ratio is higher than current 5y price ratio then sell
                            sell_now = True
                        else:
                            #If it is < 5% then it is perhaps not going very far
                            if (profit_pct < 5):
                                sell_now = True
                            else:
                                #Check number of years we've been holding
                                num_years = days_held/249
                                # we tend to give it at least 3 years to perform
                                if (num_years >= 3):
                                    # If it is not showing at least 20% return per year then sell
                                    if (profit_pct < (num_years*20)):
                                        sell_now = True

                if (sell_now):
                    #Mimic sale
                    df_transactions['Date'][transactions_count] = df.Date[i]
                    df_transactions['Action'][transactions_count] = 'SELL'
                    df_transactions['Sell_Q'][transactions_count] = total_shares
                    df_transactions['sh_gScore'][transactions_count] = curr_sh_gscore
                    df_transactions['Price'][transactions_count] = round(curr_closing_price, 3)
                    df_transactions['Avg_Price'][transactions_count] = round(avg_price, 3)
                    df_transactions['Profit'][transactions_count] = round(profit, 3)
                    df_transactions['PCT'][transactions_count] = profit_pct
                    df_transactions['Days_held'][transactions_count] = days_held
                    if (term == 'long_term'):

                        #Get actual return for S&P500 for the same period
                        actual_sp500_return = gutils.get_sp500_actual_return(df.Date[i-days_held], df.Date[i])

                        if (not np.isnan(actual_sp500_return)):
                            sp500_comp_string = f'vs SP500 return (same interval): {actual_sp500_return}'
                            df_transactions.Notes[transactions_count] = sp500_comp_string

                    transactions_count += 1
                    total_shares = 0
                    total_cost = 0
                    days_held = 0
                    avg_price = 0
                    profit = 0
                    total_cash = 0
                    marked_for_sell = 0
                    sell_now = False
                    sp500_comp_string = ''
        else:
            marked_for_sell = False

        if (total_shares):
            days_held += 1

    df_sci = pd.read_csv(path / f'{tsymbol}_gscores.csv', index_col='Unnamed: 0')
    if (df_sci.SCI_Total[0] <= 0):
        sci_note = f'Current_info_data_overall_negative'
    else:
        sci_note = f'Current_info_data_overall_positive'

    #Show last closing price for convenience
    df_transactions.Last_Price[transactions_count] = round(curr_closing_price, 3)

    #Check current stage (buy/sell/hold cycle) of our strategy execution
    if (marked_for_buy):
        cycle = 'Buy_cycle'
    elif (marked_for_sell):
        cycle = 'Sell_cycle'
    else:
        cycle = 'Hold_cycle'

    if (total_shares):
        df_transactions.Days_held[transactions_count] = days_held
        df_transactions.PCT[transactions_count] = profit_pct

    try:
        pp_ds = pd.read_csv(path / f'{tsymbol}_pp.csv')
        #Extract 3m, 1y, 5y to log in backtesting results
        pp_3m = round(pp_ds.PP[60], 3)
        pp_1y = round(pp_ds.PP[249], 3)
        pp_5yr = round(pp_ds.PP[len(pp_ds)-1], 3)
        pp_note = f'price projection[3m, 1y, 5yr]: {pp_3m}, {pp_1y}, {pp_5yr}'
    except:
        pp_note = f'Price projection tool has not been run for {tsymbol}'

    note = f'{sci_note},{pp_note}'
    df_transactions.Stage[transactions_count] = cycle
    df_transactions.Notes[transactions_count] = note
    df_transactions = df_transactions.truncate(after=transactions_count)
    df_transactions.to_csv(path / f'{tsymbol}_gtrades_stats_{term}.csv')

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

            #Verify that prepared data corresponds to correct timeline and values before backtesting

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

            #Read the prepared data (gscores history and closing price) into dataframe
            df_gscores_history = pd.read_csv(path / f'{tsymbol}_micro_gscores.csv', index_col='Unnamed: 0')

            #Just double check data is consistent before backtesting
            for i in range(len(df)):
                if ((round(df_gscores_history.Close[i], 3) != round(df.Close[i], 3)) or (df_gscores_history.Date[i] != df.Date[i])):
                    raise ValueError('gScores and price history mismatched')

        except:
            print('\nERROR: Backtesting data initialization failed for symbol ', tsymbol)
            return

        #You can call your own backtesting function here. Following is a basic example
        run_basic_backtest(df_gscores_history, path, tsymbol, 'short_term')
        run_basic_backtest(df_gscores_history, path, tsymbol, 'long_term')

        #Following is done to make it easier to use this with backtesting python framework
#        df_gscores_history.Date = pd.to_datetime(df_gscores_history['Date'])
#        df_gscores_history = df_gscores_history.set_index('Date')

        #Instantiate Backtest
#        backtest = Backtest(df_gscores_history, gScoresDataAction, cash=20000)

        #Back test the strategy using our dataframe
#        bt_stats = backtest.run()

        #Save it for later reference
#        bt_stats.to_csv(path / f'{tsymbol}_bt_stats.csv')
