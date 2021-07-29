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
import gammath_pe_signals as gpes
import gammath_peg_signals as gpeg
import gammath_beta_signals as gbeta
import gammath_ihp_signals as gihp
import gammath_inshp_signals as ginshp
import gammath_qbs_signals as gqbs
import gammath_pbr_signals as gpbrs
import gammath_reco_signals as greco
import sys
import time
import os

RSI_OVERSOLD_LEVEL = 30
RSI_OVERBOUGHT_LEVEL = 70

MFI_OVERSOLD_LEVEL = 20
MFI_OVERBOUGHT_LEVEL = 80

STOCH_OVERSOLD_LEVEL = 20
STOCH_OVERBOUGHT_LEVEL = 80

#Get summary of past 5 years history
end_date = datetime.today()
start_date = datetime(end_date.year-5, end_date.month, end_date.day)

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

    try:
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

        #Options signals
        options_buy_score, options_sell_score, options_max_score, options_signals = gos.get_options_signals(ticker, path, df.Close[len(df)-1], df_summ)

        #PE signals
        pe_buy_score, pe_sell_score, pe_max_score, pe_signals = gpes.get_pe_signals(tsymbol, df_summ)

        #PEG signals
        peg_buy_score, peg_sell_score, peg_max_score, peg_signals = gpeg.get_peg_signals(tsymbol, df_summ)

        #Beta signals
        beta_buy_score, beta_sell_score, beta_max_score, beta_signals = gbeta.get_beta_signals(tsymbol, df_summ)

        #Institutional Holders Percentage signals
        ihp_buy_score, ihp_sell_score, ihp_max_score, ihp_signals = gihp.get_ihp_signals(tsymbol, df_summ)

        #Insider Holders Percentage signals
        inshp_buy_score, inshp_sell_score, inshp_max_score, inshp_signals = ginshp.get_inshp_signals(tsymbol, df_summ)

        #Quarterly Balance sheet signals
        qbs_buy_score, qbs_sell_score, qbs_max_score, qbs_signals = gqbs.get_qbs_signals(tsymbol, path)

        #PBR signals
        pbr_buy_score, pbr_sell_score, pbr_max_score, pbr_signals = gpbrs.get_pbr_signals(tsymbol, df_summ)

        #Reco signals
        reco_buy_score, reco_sell_score, reco_max_score, reco_signals = greco.get_reco_signals(tsymbol, path)

        #StockTwits signals
        st_buy_score, st_sell_score, st_max_score, st_signals = gstw.get_stocktwits_ticker_info(tsymbol, path)

        overall_buy_score = price_buy_score + rsi_buy_score + bb_buy_score + mfi_buy_score + stoch_buy_score + macd_buy_score + options_buy_score + pe_buy_score + peg_buy_score + beta_buy_score + ihp_buy_score + inshp_buy_score + qbs_buy_score + pbr_buy_score + reco_buy_score + st_buy_score
        overall_sell_score = price_sell_score + rsi_sell_score + bb_sell_score + mfi_sell_score + stoch_sell_score + macd_sell_score + options_sell_score + pe_sell_score + peg_sell_score + beta_sell_score + ihp_sell_score + inshp_sell_score + qbs_sell_score + pbr_sell_score + reco_sell_score + st_sell_score
        overall_max_score = price_max_score + rsi_max_score + bb_max_score + mfi_max_score + stoch_max_score + macd_max_score + options_max_score + pe_max_score + peg_max_score + beta_max_score + ihp_max_score + inshp_max_score +  qbs_max_score + pbr_max_score + reco_max_score + st_max_score

        overall_buy_rec = f'overall_buy_score:{overall_buy_score}/{overall_max_score}'
        overall_sell_rec = f'overall_sell_score:{overall_sell_score}/{overall_max_score}'

        f = open(path / 'signal.txt', 'w')
        f.write(f'{price_signals}\n{rsi_signals}\n{bb_signals}\n{macd_signals}\n{mfi_signals}\n{stoch_slow_signals}\n{options_signals}\n{pe_signals}\n{peg_signals}\n{beta_signals}\n{ihp_signals}\n{inshp_signals}\n{qbs_signals}\n{pbr_signals}\n{reco_signals}\n{st_signals}\n{overall_buy_rec}\n{overall_sell_rec}')
        f.close()

        file_exists = (path / f'{tsymbol}_charts.png').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_charts.png')
            fct_time = time.ctime(fstat.st_ctime).split(' ')
            dt = time.strftime('%x').split('/')
            if (fct_time[2] == dt[1]):
                print('No need to draw charts again for today')
                return

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
    except:
        print('\nError while getting stock info for ', tsymbol, ': ', sys.exc_info()[0])

    
