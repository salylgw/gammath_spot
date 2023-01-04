# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works
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
__copyright__ = 'Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works'

import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path
from talib import RSI, BBANDS, MACD, MFI, STOCH
from matplotlib import pyplot as plt
import sys
import os
import time
try:
    from gammath_spot import gammath_kf_signals as gkf
    from gammath_spot import gammath_ols_signals as gols
except:
    import gammath_kf_signals as gkf
    import gammath_ols_signals as gols

def plot_and_save_charts(tsymbol, path, bb_df, rsi_df, mfi_df, macd_df, stoch_df, kf_df, ols_df):

    RSI_OVERSOLD_LEVEL = 30
    RSI_OVERBOUGHT_LEVEL = 70

    MFI_OVERSOLD_LEVEL = 20
    MFI_OVERBOUGHT_LEVEL = 80

    STOCH_OVERSOLD_LEVEL = 20
    STOCH_OVERBOUGHT_LEVEL = 80

    #Draw the charts to view all at once as subplots
    figure, axes = plt.subplots(nrows=7, figsize=(28, 35))

    #Get DPI for the figure
    charts_dpi = figure.get_dpi()

    #Get the width and height in pixels for the figure
    charts_pw = figure.get_figwidth() * charts_dpi
    charts_ph = figure.get_figheight() * charts_dpi

    logo_file_found = True

    try:
        #Get the path of program/package
        pgm_dir_path, fn = os.path.split(__file__)

        #Append the data dir
        pgm_data_path = os.path.join(pgm_dir_path, 'data')

        #Read the logo
        logo_data = plt.imread(f'{pgm_data_path}/logo.png')
    except:
        logo_file_found = False

    try:
        bb_df.plot(ax=axes[0],lw=1,title='Bollinger Bands')
        rsi_df.plot(ax=axes[1],lw=1,title='Relative Strength Index')
        axes[1].axhline(RSI_OVERBOUGHT_LEVEL,lw=1,ls='-',c='r')
        axes[1].axhline(RSI_OVERSOLD_LEVEL,lw=1,ls='-',c='r')
        macd_df.plot(ax=axes[2],lw=1,title='Moving Average Convergence Divergence')
        mfi_df.plot(ax=axes[3],lw=1,title='Money Flow Index')
        axes[3].axhline(MFI_OVERBOUGHT_LEVEL,lw=1,ls='-',c='r')
        axes[3].axhline(MFI_OVERSOLD_LEVEL,lw=1,ls='-',c='r')
        stoch_df.plot(ax=axes[4],lw=1,title='Stochastic Slow')
        axes[4].axhline(STOCH_OVERBOUGHT_LEVEL,lw=1,ls='-',c='r')
        axes[4].axhline(STOCH_OVERSOLD_LEVEL,lw=1,ls='-',c='r')
        kf_df.plot(ax=axes[5], lw=1,title='Kalman Filter')
        ols_df.plot(ax=axes[6], lw=1,title='OLS')

        if (logo_file_found):
            #Attach the logo to figure
            plt.figimage(logo_data, xo=charts_pw/2, yo=(charts_ph-100))

        #Save for later reference. Use PDF instead of png to save space
        plt.savefig(path / f'{tsymbol}_charts.pdf', format='pdf')
    except:
        print('\nERROR: Plotting charts for ', tsymbol, ': ', sys.exc_info()[0])

