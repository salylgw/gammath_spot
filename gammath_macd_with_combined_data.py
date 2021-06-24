# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from datetime import datetime
from pathlib import Path
from talib import RSI, BBANDS, MACD, MFI, STOCH
import gammath_stocks_history as gsh


RSI_TIME_PERIOD = 14
RSI_OVERSOLD_LEVEL = 30
RSI_OVERBOUGHT_LEVEL = 70

BBANDS_TIME_PERIOD = 14

MFI_TIME_PERIOD = 14
MFI_OVERSOLD_LEVEL = 20
MFI_OVERBOUGHT_LEVEL = 80

STOCH_FAST_PERIOD = 14
STOCH_SLOW_PERIOD = 3
STOCH_OVERSOLD_LEVEL = 20
STOCH_OVERBOUGHT_LEVEL = 80

MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9

#Get summary of past 5 years history
end_date = datetime.today()
start_date = datetime(end_date.year-5, end_date.month, end_date.day)

def get_macd_combined_data(tsymbol):

    result = gsh.get_ticker_history(tsymbol)

    if (result is None):
        return
    else:
        path = result

    #Read CSV into DataFrame. Stock_history dataframe seems to filter out dates
    df = pd.read_csv(path / f'{tsymbol}_history.csv')
    print('DataFrame info read from CSV for symbol: ', tsymbol, ':\n')
    df.info()

    #MACD data
    macd, macd_signal, macd_histogram = MACD(df.Close, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD)

    macd_len = len(macd)
    if (macd_len<=0):
        return

    #Prices data
    prices = df.Close
    prices_len = len(prices)
    if (prices_len <= 0):
        return

    #RSI data
    rsi = RSI(df.Close, timeperiod=RSI_TIME_PERIOD)
    rsi_len = len(rsi)
    if (rsi_len <= 0):
        return

    #Bollinger bands data
    ub, mb, lb = BBANDS(df.Close, timeperiod=BBANDS_TIME_PERIOD, nbdevup=2, nbdevdn=2, matype=0)
    bb_len = len(ub)
    if (bb_len<=0):
        return

    #MFI data
    mfi = MFI(df.High, df.Low, df.Close, df.Volume, timeperiod=MFI_TIME_PERIOD)
    mfi_len = len(mfi)

    #Stochs data
    slowk, slowd = STOCH(df.High, df.Low, df.Close, fastk_period=STOCH_FAST_PERIOD, slowk_period=STOCH_SLOW_PERIOD, slowk_matype=0, slowd_period=STOCH_SLOW_PERIOD, slowd_matype=0)

    stoch_len = len(slowd)

    buy_sig = 0
    sell_sig = 0

    last_buy_signal_index = 0
    last_sell_signal_index = 0

    df_buy_sell_signals_data = pd.DataFrame(columns=['bsig', 'ssig', 'price', 'diff', 'pct_change', 'rsi_avg',  'bb_avg', 'bb_vicinity', 'mfi_avg', 'stoch_lvl', 'exception'],index=range(macd_len))
    df_buy_sell_sig_data_index = 0

    df_exeptions_data = df_buy_sell_signals_data
    rule_exception_index = 0

    for i in range(macd_len-1):
        if ((macd_histogram[i] <= 0) and (macd_histogram[i+1] > 0)):
            #Buy signal
            buy_sig = 1
            sell_sig = 0
            last_buy_signal_index = i+1
            df_buy_sell_signals_data['bsig'][df_buy_sell_sig_data_index] = df['Date'][last_buy_signal_index]
            df_buy_sell_signals_data['ssig'][df_buy_sell_sig_data_index] = '-'
            df_buy_sell_signals_data['price'][df_buy_sell_sig_data_index] = round(df['Close'][last_buy_signal_index], 3)
        elif ((macd_histogram[i] >= 0) and (macd_histogram[i+1] < 0)):
            #Sell signal
            buy_sig = 0
            sell_sig = 1
            last_sell_signal_index = i+1
            df_buy_sell_signals_data['ssig'][df_buy_sell_sig_data_index] = df['Date'][last_sell_signal_index]
            df_buy_sell_signals_data['bsig'][df_buy_sell_sig_data_index] = '-'
            df_buy_sell_signals_data['price'][df_buy_sell_sig_data_index] = round(df['Close'][last_sell_signal_index], 3)

            if (df_buy_sell_sig_data_index > 0):
               df_buy_sell_signals_data['diff'][df_buy_sell_sig_data_index] = round((df_buy_sell_signals_data['price'][df_buy_sell_sig_data_index] - df_buy_sell_signals_data['price'][df_buy_sell_sig_data_index-1]), 3)
               df_buy_sell_signals_data['pct_change'][df_buy_sell_sig_data_index] = round(100*(df_buy_sell_signals_data['diff'][df_buy_sell_sig_data_index]/df_buy_sell_signals_data['price'][df_buy_sell_sig_data_index-1]), 3)
        else:
            buy_sig = 0
            sell_sig = 0

        #Combine historic data at macd signal to analyze signal accuracy
        if ((buy_sig == 1) or (sell_sig == 1)):
            rsi_inst_mean = rsi[0:i+1].mean()
            if (rsi[i+1] < rsi_inst_mean):
                ins_rsi_avg = 'b_aver'
            elif (rsi[i+1] > rsi_inst_mean):
                ins_rsi_avg = 'a_aver'
            else:
                ins_rsi_avg = 'aver'

            if (prices[i+1] < mb[i+1]):
                ins_bb_avg = 'b_aver'
                if ((mb[i+1] - prices[i+1]) < (abs(prices[i+1] - lb[i+1]))):
                    ins_bb_vicinity = 'n_mb'
                else:
                    ins_bb_vicinity = 'n_lb'

            elif (prices[i+1] > mb[i+1]):
                ins_bb_avg = 'a_aver'
                if ((prices[i+1] - mb[i+1]) < (abs(ub[i+1] - prices[i+1]))):
                    ins_bb_vicinity = 'n_mb'
                else:
                    ins_bb_vicinity = 'n_ub'
            else:
                ins_bb_avg = 'aver'
                ins_bb_vicinity = 'at_mb'


            mfi_inst_mean = mfi[0:i+1].mean()
            if (mfi[i+1] < mfi_inst_mean):
                ins_mfi_avg = 'b_aver'
            elif (mfi[i+1] > mfi_inst_mean):
                ins_mfi_avg = 'a_aver'
            else:
                ins_mfi_avg = 'aver'

            ins_stoch_lvl = ''
            slowd_inst_mean = slowd[0:i+1].mean()

            if (slowd[i+1] < slowd_inst_mean):
                ins_stoch_lvl = 'below average'
            elif (slowd[i+1] > slowd_inst_mean):
                ins_stoch_lvl = 'above average'
            else:
                ins_stoch_lvl = 'average'

            if (slowd[i+1] <= STOCH_OVERSOLD_LEVEL):
                ins_stoch_lvl = 'oversold'
            elif (slowd[i+1] >= STOCH_OVERBOUGHT_LEVEL):
                ins_stoch_lvl = 'overbought'

            df_buy_sell_signals_data['rsi_avg'][df_buy_sell_sig_data_index] = ins_rsi_avg
            df_buy_sell_signals_data['bb_avg'][df_buy_sell_sig_data_index] = ins_bb_avg
            df_buy_sell_signals_data['bb_vicinity'][df_buy_sell_sig_data_index] = ins_bb_vicinity
            df_buy_sell_signals_data['mfi_avg'][df_buy_sell_sig_data_index] = ins_mfi_avg
            df_buy_sell_signals_data['stoch_lvl'][df_buy_sell_sig_data_index] = ins_stoch_lvl

            if ((sell_sig == 1) and (df_buy_sell_sig_data_index > 0)):
                if (df_buy_sell_signals_data['diff'][df_buy_sell_sig_data_index] < 0):
                    if ((df_buy_sell_signals_data['rsi_avg'][df_buy_sell_sig_data_index-1] == 'b_aver') and (df_buy_sell_signals_data['bb_avg'][df_buy_sell_sig_data_index-1] == 'b_aver') and (df_buy_sell_signals_data['bb_vicinity'][df_buy_sell_sig_data_index-1] == 'n_lb') and (df_buy_sell_signals_data['mfi_avg'][df_buy_sell_sig_data_index-1] == 'b_aver') and (( df_buy_sell_signals_data['stoch_lvl'][df_buy_sell_sig_data_index-1]  == 'below average') or (df_buy_sell_signals_data['stoch_lvl'][df_buy_sell_sig_data_index-1] == 'oversold'))):
                        df_buy_sell_signals_data['exception'][df_buy_sell_sig_data_index-1] = '*'
                        df_buy_sell_signals_data['exception'][df_buy_sell_sig_data_index] = '*'

                        df_exeptions_data.iloc[rule_exception_index] = df_buy_sell_signals_data.iloc[df_buy_sell_sig_data_index-1]

                        rule_exception_index += 1

                        df_exeptions_data.iloc[rule_exception_index] = df_buy_sell_signals_data.iloc[df_buy_sell_sig_data_index]

                        rule_exception_index += 1


            df_buy_sell_sig_data_index += 1

    #Save the buy/sell signals data
    df_buy_sell_signals_data.to_csv(path / f'{tsymbol}_combined_buy_sell_sig_data.csv', index=False)

    #Save the exceptions data separately
    df_exeptions_data.to_csv(path / f'{tsymbol}_exception_sig_data.csv', index=False)
    return

