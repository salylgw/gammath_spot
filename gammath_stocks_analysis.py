# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path
from talib import RSI, BBANDS, MACD, MFI, STOCH
from matplotlib import pyplot as plt
import gammath_stocks_history as gsh
import gammath_price_signals as gps
import gammath_rsi_signals as grs
import gammath_bb_signals as gbbs
import gammath_mfi_signals as gms
import gammath_stoch_signals as gss
import gammath_macd_signals as gmacd
import gammath_stcktwts as gstw
import gammath_kf_signals as gkf
import gammath_options_signals as gos

RSI_OVERSOLD_LEVEL = 30
RSI_OVERBOUGHT_LEVEL = 70

MFI_OVERSOLD_LEVEL = 20
MFI_OVERBOUGHT_LEVEL = 80

STOCH_OVERSOLD_LEVEL = 20
STOCH_OVERBOUGHT_LEVEL = 80

#Get summary of past 5 years history
end_date = datetime.today()
start_date = datetime(end_date.year-5, end_date.month, end_date.day)

Tickers_dir = Path('tickers')

def get_ticker_hist_n_analysis(tsymbol):

    result = gsh.get_ticker_info(tsymbol)

    if (result is None):
        return
    else:
        path, ticker = result

    try:
        #Read CSV into DataFrame. Stock_history dataframe seems to filter out dates
        df = pd.read_csv(path / f'{tsymbol}_history.csv')
        print('DataFrame info read from CSV for symbol: ', tsymbol, ':\n')
        df.info()
    except:
        print('\nStock history file not found for ', tsymbol)
        df = pd.DataFrame()

    try:
        #Read Stock summary info into DataFrame.
        df_summ = pd.read_csv(path / f'{tsymbol}_summary.csv')
        print('DataFrame info read from CSV for symbol: ', tsymbol, ':\n')
        df_summ.info()
    except:
        print('\nStock summary file not found for symbol ', tsymbol)
        df_summ = pd.DataFrame()

    #Price signals
    price_buy_score, price_sell_score, price_max_score, price_signals = gps.get_price_signals(df, df_summ)

    #Relative Strenght Index signals
    rsi, rsi_buy_score, rsi_sell_score, rsi_max_score, rsi_signals = grs.get_rsi_signals(tsymbol, df, path)

    #Bollinger bands signals
    mb, ub, lb, bb_buy_score, bb_sell_score, bb_max_score, bb_signals = gbbs.get_bollinger_bands_signals(df, path)

    #MFI signals
    mfi, mfi_buy_score, mfi_sell_score, mfi_max_score, mfi_signals = gms.get_mfi_signals(df)

    #Stochastic slow signals
    slowk, slowd, stoch_buy_score, stoch_sell_score, stoch_max_score, stoch_slow_signals = gss.get_stochastics_slow_signals(df)

    #MACD signals
    macd, macd_signal, macd_buy_score, macd_sell_score, macd_max_score, macd_signals = gmacd.get_macd_signals(df)

    #Kalman Filter. For now just plot the state means against price
    state_means, state_covariance = gkf.get_kf_means_covariance(df)

    #StockTwits signals
    st_buy_score, st_sell_score, st_max_score, st_signals = gstw.get_stocktwits_ticker_info(tsymbol, path)
    
    #Options signals
    options_buy_score, options_sell_score, options_max_score, options_signals = gos.get_options_signals(ticker, path, df.Close[len(df)-1], df_summ)

#    0, 0, 0, ''

    overall_buy_score = price_buy_score + rsi_buy_score + bb_buy_score + mfi_buy_score + stoch_buy_score + macd_buy_score + st_buy_score + options_buy_score
    overall_sell_score = price_sell_score + rsi_sell_score + bb_sell_score + mfi_sell_score + stoch_sell_score + macd_sell_score + st_sell_score + options_sell_score
    overall_max_score = price_max_score + rsi_max_score + bb_max_score + mfi_max_score + stoch_max_score + macd_max_score + st_max_score + options_max_score

    overall_buy_rec = f'overall_buy_score:{overall_buy_score}/{overall_max_score}'
    overall_sell_rec = f'overall_sell_score:{overall_sell_score}/{overall_max_score}'

    f = open(path / 'signal.txt', 'w')
    f.write(f'{price_signals}\n{rsi_signals}\n{bb_signals}\n{macd_signals}\n{mfi_signals}\n{stoch_slow_signals}\n{st_signals}\n{options_signals}\n{overall_buy_rec}\n{overall_sell_rec}')
    f.close()

    #Draw the charts to view all at once as subplots
    figure, axes = plt.subplots(nrows=6, figsize=(21, 19))

    sym_str = f'{tsymbol}'

    plot_data1 = pd.DataFrame({sym_str: df.Close, 'Upper Band': ub, 'Middle Band': mb, 'Lower Band': lb})
    plot_data2 = pd.DataFrame({'RSI': rsi})
    #Don't need to draw the MACD histogram
    plot_data3 = pd.DataFrame({'MACD': macd, 'MACD_SIGNAL': macd_signal})
    plot_data4 = pd.DataFrame({'MFI': mfi})
    plot_data5 = pd.DataFrame({'SLOWK': slowk, 'SLOWD': slowd})
    plot_data6 = pd.DataFrame({sym_str: df.Close, 'Kalman Filter': state_means.flatten()})

    plot_data1.plot(ax=axes[0],lw=1,title='Bollinger Bands')
    plot_data2.plot(ax=axes[1],lw=1,title='Relative Strength Index')
    axes[1].axhline(RSI_OVERBOUGHT_LEVEL,lw=1,ls='-',c='r')
    axes[1].axhline(RSI_OVERSOLD_LEVEL,lw=1,ls='-',c='r')
    plot_data3.plot(ax=axes[2],lw=1,title='Moving Average Convergence Divergence')
    plot_data4.plot(ax=axes[3],lw=1,title='Money Flow Index')
    axes[3].axhline(MFI_OVERBOUGHT_LEVEL,lw=1,ls='-',c='r')
    axes[3].axhline(MFI_OVERSOLD_LEVEL,lw=1,ls='-',c='r')
    plot_data5.plot(ax=axes[4],lw=1,title='Stochastic Slow')
    axes[4].axhline(STOCH_OVERBOUGHT_LEVEL,lw=1,ls='-',c='r')
    axes[4].axhline(STOCH_OVERSOLD_LEVEL,lw=1,ls='-',c='r')
    plot_data6.plot(ax=axes[5], lw=1,title='Kalman Filter')

    plt.savefig(path / f'{tsymbol}_charts.png')
