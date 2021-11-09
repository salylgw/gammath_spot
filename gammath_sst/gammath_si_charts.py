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
import sys
import os
import time
import gammath_utils as gut
import gammath_kf_signals as gkf
import gammath_ols_signals as gols


def plot_n_save_charts(tsymbol, df, ub, mb, lb, rsi, mfi, macd, macd_signal, slowk, slowd, ds_sm, ols_y_predictions, ols_y1_predictions):

    print(f'\nPlotting and saving charts for {tsymbol}')

    RSI_OVERSOLD_LEVEL = 30
    RSI_OVERBOUGHT_LEVEL = 70

    MFI_OVERSOLD_LEVEL = 20
    MFI_OVERBOUGHT_LEVEL = 80

    STOCH_OVERSOLD_LEVEL = 20
    STOCH_OVERBOUGHT_LEVEL = 80

    Tickers_dir = Path('tickers')

    path = Tickers_dir / f'{tsymbol}'

    file_exists = (path / f'{tsymbol}_charts.png').exists()

    #Check if file exists and is it from another day
    if file_exists:
        fstat = os.stat(path / f'{tsymbol}_charts.png')

        if (True == gut.check_if_same_day(fstat)):
            print('No need to draw charts again for today')
            return

    #Draw the charts to view all at once as subplots
    figure, axes = plt.subplots(nrows=7, figsize=(21, 19))

    sym_str = f'{tsymbol}'

    try:
        plot_data1 = pd.DataFrame({sym_str: df.Close, 'Upper Band': ub, 'Middle Band': mb, 'Lower Band': lb})
    except:
        print(f'\nError generating BB DF for {sym_str}')
        plot_data1 = pd.DataFrame({sym_str: [0]})

    try:
        plot_data2 = pd.DataFrame({'RSI': rsi})
    except:
        print(f'\nError generating RSI DF for {sym_str}')
        plot_data2 = pd.DataFrame({sym_str: [0]})

    try:
        #Don't need to draw the MACD histogram
        plot_data3 = pd.DataFrame({'MACD': macd, 'MACD_SIGNAL': macd_signal})
    except:
        print(f'\nError generating MACD DF for {sym_str}')
        plot_data3 = pd.DataFrame({sym_str: [0]})

    try:
        plot_data4 = pd.DataFrame({'MFI': mfi})
    except:
        print(f'\nError generating MFI DF for {sym_str}')
        plot_data4 = pd.DataFrame({sym_str: [0]})

    try:
        plot_data5 = pd.DataFrame({'SLOWK': slowk, 'SLOWD': slowd})
    except:
        print(f'\nError generating stochastic DF for {sym_str}')
        plot_data5 = pd.DataFrame({sym_str: [0]})

    try:
        plot_data6 = pd.DataFrame({sym_str: df.Close, 'Kalman Filter': ds_sm})
    except:
        print(f'\nError generating KF DF for {sym_str}')
        plot_data6 = pd.DataFrame({sym_str: [0]})

    try:
        plot_data7 = pd.DataFrame({sym_str: df.Close, 'OLS': ols_y_predictions, 'OLS_1Y': ols_y1_predictions})
    except:
        print(f'\nError generating OLS DF for {sym_str}')
        plot_data7 = pd.DataFrame({sym_str: [0]})

    try:
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
        plot_data7.plot(ax=axes[6], lw=1,title='OLS')
        plt.savefig(path / f'{tsymbol}_charts.png')
    except:
        print('\nError while plotting charts for ', tsymbol, ': ', sys.exc_info()[0])

