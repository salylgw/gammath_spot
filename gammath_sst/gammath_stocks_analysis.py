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
import gammath_mktcap_signals as gmktcap
import gammath_qbs_signals as gqbs
import gammath_pbr_signals as gpbrs
import gammath_reco_signals as greco
import gammath_ols_signals as gols
import gammath_lgstic_signals as glgs
import gammath_get_events as gge
import sys
import time
import os
import numpy as np

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

    path = Tickers_dir / f'{tsymbol}'

    price_buy_score = 0
    rsi_buy_score = 0
    bb_buy_score = 0
    mfi_buy_score = 0
    stoch_buy_score = 0
    macd_buy_score = 0
    kf_buy_score = 0
    ols_buy_score = 0
    options_buy_score = 0
    pe_buy_score = 0
    peg_buy_score = 0
    beta_buy_score = 0
    ihp_buy_score = 0
    inshp_buy_score = 0
    mktcap_buy_score = 0
    qbs_buy_score = 0
    pbr_buy_score = 0
    reco_buy_score = 0
    st_buy_score = 0


    price_sell_score = 0
    rsi_sell_score = 0
    bb_sell_score = 0
    mfi_sell_score = 0
    stoch_sell_score = 0
    macd_sell_score = 0
    kf_sell_score = 0
    ols_sell_score = 0
    options_sell_score = 0
    pe_sell_score = 0
    peg_sell_score = 0
    beta_sell_score = 0
    ihp_sell_score = 0
    inshp_sell_score = 0
    mktcap_sell_score = 0
    qbs_sell_score = 0
    pbr_sell_score = 0
    reco_sell_score = 0
    st_sell_score = 0

    price_max_score = 0
    rsi_max_score = 0
    bb_max_score = 0
    mfi_max_score = 0
    stoch_max_score = 0
    macd_max_score = 0
    kf_max_score = 0
    ols_max_score = 0
    options_max_score = 0
    pe_max_score = 0
    peg_max_score = 0
    beta_max_score = 0
    ihp_max_score = 0
    inshp_max_score = 0
    mktcap_max_score = 0
    qbs_max_score = 0
    pbr_max_score = 0
    reco_max_score = 0
    st_max_score = 0

    price_signals = ''
    rsi_signals = ''
    bb_signals = ''
    macd_signals = ''
    kf_signals = ''
    ols_signals = ''
    lgstic_signals = ''
    mfi_signals = ''
    stoch_slow_signals = ''
    options_signals = ''
    pe_signals = ''
    peg_signals = ''
    beta_signals = ''
    ihp_signals = ''
    inshp_signals = ''
    mktcap_signals = ''
    qbs_signals = ''
    pbr_signals = ''
    reco_signals = ''
    st_signals = ''
    events_info = ''

    try:
        #Read Stock summary info into DataFrame.
        df_summ = pd.read_csv(path / f'{tsymbol}_summary.csv')
        print('DataFrame info read from CSV for symbol: ', tsymbol, ':\n')
        df_summ.info()
    except:
        print('\nStock summary file not found for symbol ', tsymbol)
        df_summ = pd.DataFrame()

    try:
        #Read CSV into DataFrame.
        df = pd.read_csv(path / f'{tsymbol}_history.csv')
        print('DataFrame info read from CSV for symbol: ', tsymbol, ':\n')
        df.info()
    except:
        print('\nStock history file not found for ', tsymbol)
        df = pd.DataFrame()

    try:
        #Price signals
        price_buy_score, price_sell_score, price_max_score, price_signals = gps.get_price_signals(tsymbol, df, df_summ)
    except:
        print('\nError while getting price signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Relative Strength Index signals
        rsi, rsi_buy_score, rsi_sell_score, rsi_max_score, rsi_signals = grs.get_rsi_signals(tsymbol, df, path)
    except:
        print('\nError while getting RSI signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Bollinger bands signals
        mb, ub, lb, bb_buy_score, bb_sell_score, bb_max_score, bb_signals = gbbs.get_bollinger_bands_signals(tsymbol, df, path)
    except:
        print('\nError while getting BB signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #MFI signals
        mfi, mfi_buy_score, mfi_sell_score, mfi_max_score, mfi_signals = gms.get_mfi_signals(tsymbol, df, path)
    except:
        print('\nError while getting MFI signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Stochastic slow signals
        slowk, slowd, stoch_buy_score, stoch_sell_score, stoch_max_score, stoch_slow_signals = gss.get_stochastics_slow_signals(tsymbol, df)
    except:
        print('\nError while getting stochastics signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #MACD signals
        macd, macd_signal, macd_buy_score, macd_sell_score, macd_max_score, macd_signals = gmacd.get_macd_signals(tsymbol, df, path)
    except:
        print('\nError while getting MACD signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Kalman Filter signals
        state_means, kf_buy_score, kf_sell_score, kf_max_score, kf_signals = gkf.get_kf_state_means(tsymbol, df)
    except:
        print('\nError while getting KF signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Ordinary Least Squares line signals
        ols_y1_predictions, ols_y3_predictions, ols_y_predictions, ols_buy_score, ols_sell_score, ols_max_score, ols_signals = gols.get_ols_signals(tsymbol, df, path)
    except:
        print('\nError while getting OLS signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Logistic regression signals
        lgstic_signals = glgs.get_lgstic_signals(tsymbol, df, path)
    except:
        print('\nError while getting lgstic regr signals for ', tsymbol, ': ', sys.exc_info()[0])
        lgstic_signals = ''

    try:
        #Options signals
        options_buy_score, options_sell_score, options_max_score, options_signals = gos.get_options_signals(tsymbol, path, df.Close[len(df)-1], df_summ)
    except:
        print('\nError while getting options signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #PE signals
        pe_buy_score, pe_sell_score, pe_max_score, pe_signals = gpes.get_pe_signals(tsymbol, df_summ)
    except:
        print('\nError while getting PE signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #PEG signals
        peg_buy_score, peg_sell_score, peg_max_score, peg_signals = gpeg.get_peg_signals(tsymbol, df_summ)
    except:
        print('\nError while getting PEG signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Beta signals
        beta_buy_score, beta_sell_score, beta_max_score, beta_signals = gbeta.get_beta_signals(tsymbol, df_summ)
    except:
        print('\nError while getting beta signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Institutional Holders Percentage signals
        ihp_buy_score, ihp_sell_score, ihp_max_score, ihp_signals = gihp.get_ihp_signals(tsymbol, df_summ)
    except:
        print('\nError while getting ihp signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Insider Holders Percentage signals
        inshp_buy_score, inshp_sell_score, inshp_max_score, inshp_signals = ginshp.get_inshp_signals(tsymbol, df_summ)
    except:
        print('\nError while getting inshp signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Market cap signals
        mktcap_buy_score, mktcap_sell_score, mktcap_max_score, mktcap_signals = gmktcap.get_mktcap_signals(tsymbol, df_summ)
    except:
        print('\nError while getting mktcap signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Quarterly Balance sheet signals
        qbs_buy_score, qbs_sell_score, qbs_max_score, qbs_signals = gqbs.get_qbs_signals(tsymbol, path)
    except:
        print('\nError while getting QBS signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #PBR signals
        pbr_buy_score, pbr_sell_score, pbr_max_score, pbr_signals = gpbrs.get_pbr_signals(tsymbol, df_summ)
    except:
        print('\nError while getting PBR signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Reco signals
        reco_buy_score, reco_sell_score, reco_max_score, reco_signals = greco.get_reco_signals(tsymbol, path)
    except:
        print('\nError while getting reco signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #StockTwits signals
        st_buy_score, st_sell_score, st_max_score, st_signals = gstw.get_stocktwits_signals(tsymbol, path)
    except:
        print('\nError while getting stocktwits signals for ', tsymbol, ': ', sys.exc_info()[0])

    try:
        #Get events info
        events_info = gge.get_events_info(tsymbol, path)
    except:
        print('\nError while getting events info for ', tsymbol, ': ', sys.exc_info()[0])

    overall_buy_score = price_buy_score + rsi_buy_score + bb_buy_score + mfi_buy_score + stoch_buy_score + macd_buy_score + kf_buy_score + ols_buy_score + options_buy_score + pe_buy_score + peg_buy_score + beta_buy_score + ihp_buy_score + inshp_buy_score + mktcap_buy_score + qbs_buy_score + pbr_buy_score + reco_buy_score + st_buy_score
    overall_sell_score = price_sell_score + rsi_sell_score + bb_sell_score + mfi_sell_score + stoch_sell_score + macd_sell_score + kf_sell_score + ols_sell_score + options_sell_score + pe_sell_score + peg_sell_score + beta_sell_score + ihp_sell_score + inshp_sell_score + mktcap_sell_score + qbs_sell_score + pbr_sell_score + reco_sell_score + st_sell_score
    overall_max_score = price_max_score + rsi_max_score + bb_max_score + mfi_max_score + stoch_max_score + macd_max_score + kf_max_score + ols_max_score + options_max_score + pe_max_score + peg_max_score + beta_max_score + ihp_max_score + inshp_max_score + mktcap_max_score + qbs_max_score + pbr_max_score + reco_max_score + st_max_score

    overall_buy_rec = f'overall_buy_score:{overall_buy_score}/{overall_max_score}'
    overall_sell_rec = f'overall_sell_score:{overall_sell_score}/{overall_max_score}'

    if (overall_max_score != 0):
        final_buy_score = round((int(overall_buy_score)/int(overall_max_score)), 5)
        final_sell_score = round((int(overall_sell_score)/int(overall_max_score)), 5)
    else:
        final_buy_score = 0
        final_sell_score = 0

    final_buy_score_rec = f'final_buy_score:{final_buy_score}'
    final_sell_score_rec = f'final_sell_score:{final_sell_score}'

    try:
        f = open(path / 'signal.txt', 'w')
    except:
        print('\nError while opening signal file for ', tsymbol, ': ', sys.exc_info()[0])
    else:
        f.write(f'{price_signals}\n{rsi_signals}\n{bb_signals}\n{macd_signals}\n{kf_signals}\n{ols_signals}\n{lgstic_signals}\n{mfi_signals}\n{stoch_slow_signals}\n{options_signals}\n{pe_signals}\n{peg_signals}\n{beta_signals}\n{ihp_signals}\n{inshp_signals}\n{mktcap_signals}\n{qbs_signals}\n{pbr_signals}\n{reco_signals}\n{st_signals}\n{overall_buy_rec}\n{overall_sell_rec}\n{final_buy_score_rec}\n{final_sell_score_rec}\n{events_info}')
        f.close()

        file_exists = (path / f'{tsymbol}_charts.png').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_charts.png')
            fct_time = time.ctime(fstat.st_ctime).split(' ')
            dt = time.strftime('%x').split('/')
            if (fct_time[2] == ''):
                fct_date_index = 3
            else:
                fct_date_index = 2

            fct_date = int(fct_time[fct_date_index])
            dt_date = int(dt[1])

            if (fct_date == dt_date):
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
        plot_data6 = pd.DataFrame({sym_str: df.Close, 'Kalman Filter': state_means.flatten()})
    except:
        print(f'\nError generating KF DF for {sym_str}')
        plot_data6 = pd.DataFrame({sym_str: [0]})

    try:
        plot_data7 = pd.DataFrame({sym_str: df.Close, 'OLS': ols_y_predictions, 'OLS_1Y': ols_y1_predictions, 'OLS_3Y': ols_y3_predictions})
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

    
