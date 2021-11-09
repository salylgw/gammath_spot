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
import gammath_stcktwts_signals as gstw
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
import gammath_ols_signals as gols
import gammath_get_events as gge
import gammath_score_signals as gscsi
import gammath_si_charts as gsc
import sys
import time
import os
import numpy as np
import re

class GSA:

    def __init__(self):
        print('\nGSA instantiated')
        self.Tickers_dir = Path('tickers')
        self.overall_dip_score = 0
        self.overall_max_score = 0
        self.reco_signals_exist = False
        self.note = ''

    def do_stock_analysis_and_compute_score(self, tsymbol):
        print('\nGSA do_stock_analysis_and_compute_score')

        path = self.Tickers_dir / f'{tsymbol}'

        try:
            #Read Stock summary info into DataFrame.
            df_summ = pd.read_csv(path / f'{tsymbol}_summary.csv')
            print('DataFrame info read from CSV for symbol: ', tsymbol, ':\n')
            df_summ.info()
        except:
            print('\nERROR: Stock summary file not found for symbol ', tsymbol)
            return

        try:
            #Read CSV into DataFrame.
            df = pd.read_csv(path / f'{tsymbol}_history.csv')
            print('DataFrame info read from CSV for symbol: ', tsymbol, ':\n')
            df.info()
            dt = time.strftime('%x').split('/')
            df_ld = df.Date[len(df)-1]
            df_ld = df_ld.split('-')
            if ((int(dt[0]) != int(df_ld[1])) and (int(dt[1]) != int(df_ld[2]))):
                raise ValueError('Stale price data')
        except ValueError:
            print('\nERROR: Stale price data for ', tsymbol)
            self.note = 'Note: INVALID_STOCK_HISTORY'
        except:
            print('\nERROR: Stock history file not found for ', tsymbol)
            return

        try:
            reco_dip_score = 0
            reco_max_score = 0 #In case there is an exception, we should do fundamental analysis
            reco_signals = ''
            #Reco signals
            reco_dip_score, reco_max_score, reco_signals = greco.get_reco_signals(tsymbol, path)

            self.overall_dip_score += reco_dip_score
            self.overall_max_score += reco_max_score
            self.reco_signals_exist = ((reco_dip_score != 0) and (reco_max_score != 0))
        except RuntimeError:
            print('\nError while getting reco signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            pe_dip_score = 0
            pe_max_score = 2
            pe_signals = ''

            #PE signals
            pe_dip_score, pe_max_score, pe_signals = gpes.get_pe_signals(tsymbol, df_summ)
            if not self.reco_signals_exist:
                self.overall_dip_score += pe_dip_score
                self.overall_max_score += pe_max_score

        except ValueError:
            print('\nError while getting PE signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            peg_dip_score = 0
            peg_max_score = 1
            peg_signals = ''

            #PEG signals
            peg_dip_score, peg_max_score, peg_signals = gpeg.get_peg_signals(tsymbol, df_summ)

            if not self.reco_signals_exist:
                self.overall_dip_score += peg_dip_score
                self.overall_max_score += peg_max_score

        except ValueError:
            print('\nError while getting PEG signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            beta_dip_score = 0
            beta_max_score = 1
            beta_signals = ''

            #Beta signals
            beta_dip_score, beta_max_score, beta_signals = gbeta.get_beta_signals(tsymbol, df_summ)

            if not self.reco_signals_exist:
                self.overall_dip_score += beta_dip_score
                self.overall_max_score += beta_max_score

        except ValueError:
            print('\nError while getting beta signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            pbr_dip_score = 0
            pbr_max_score = 1
            pbr_signals = ''

            #PBR signals
            pbr_dip_score, pbr_max_score, pbr_signals = gpbrs.get_pbr_signals(tsymbol, df_summ)

            if not self.reco_signals_exist:
                self.overall_dip_score += pbr_dip_score
                self.overall_max_score += pbr_max_score

        except RuntimeError:
            print('\nError while generating PBR signals for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError while getting PBR signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            qbs_dip_score = 0
            qbs_max_score = 4
            qbs_signals = ''

            #Quarterly Balance sheet signals
            qbs_dip_score, qbs_max_score, qbs_signals = gqbs.get_qbs_signals(tsymbol, path)

            if not self.reco_signals_exist:
                self.overall_dip_score += qbs_dip_score
                self.overall_max_score += qbs_max_score

        except ValueError:
            print('\nError while getting QBS signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            ihp_dip_score = 0
            ihp_max_score = 1
            ihp_signals = ''

            #Institutional Holders Percentage signals
            ihp_dip_score, ihp_max_score, ihp_signals = gihp.get_ihp_signals(tsymbol, df_summ)

            if not self.reco_signals_exist:
                self.overall_dip_score += ihp_dip_score
                self.overall_max_score += ihp_max_score

        except ValueError:
            print('\nError while getting ihp signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            inshp_dip_score = 0
            inshp_max_score = 1
            inshp_signals = ''

            #Insider Holders Percentage signals
            inshp_dip_score, inshp_max_score, inshp_signals = ginshp.get_inshp_signals(tsymbol, df_summ)
        except ValueError:
            print('\nError while getting inshp signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            price_dip_score = 0
            price_max_score = 10
            price_signals = ''
            #Price signals
            price_dip_score, price_max_score, price_signals = gps.get_price_signals(tsymbol, df, df_summ)

            self.overall_dip_score += price_dip_score
            self.overall_max_score += price_max_score

        except ValueError:
            print('\nError generating price signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            rsi_dip_score = 0
            rsi_max_score = 10
            rsi_signals = ''
            #Relative Strength Index signals
            rsi, rsi_dip_score, rsi_max_score, rsi_signals = grs.get_rsi_signals(tsymbol, df, path)

            self.overall_dip_score += rsi_dip_score
            self.overall_max_score += rsi_max_score

        except RuntimeError:
            print('\nError generating RSI data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from RSI data ', tsymbol, ': ', sys.exc_info()[0])

        try:
            bb_dip_score = 0
            bb_max_score = 10
            bb_signals = ''
            #Bollinger bands signals
            ub, mb, lb, bb_dip_score, bb_max_score, bb_signals = gbbs.get_bollinger_bands_signals(tsymbol, df, path)

            self.overall_dip_score += bb_dip_score
            self.overall_max_score += bb_max_score

        except RuntimeError:
            print('\nError generating Bollinger Bands for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from Bollinger Bands for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            mfi_dip_score = 0
            mfi_max_score = 10
            mfi_signals = ''

            #MFI signals
            mfi, mfi_dip_score, mfi_max_score, mfi_signals = gms.get_mfi_signals(tsymbol, df, path)

            self.overall_dip_score += mfi_dip_score
            self.overall_max_score += mfi_max_score

        except RuntimeError:
            print('\nError generating MFI data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from MFI data ', tsymbol, ': ', sys.exc_info()[0])

        try:
            stoch_dip_score = 0
            stoch_max_score = 5
            stoch_slow_signals = ''

            #Stochastic slow signals
            slowk, slowd, stoch_dip_score, stoch_max_score, stoch_slow_signals = gss.get_stochastics_slow_signals(tsymbol, df)

            self.overall_dip_score += stoch_dip_score
            self.overall_max_score += stoch_max_score

        except RuntimeError:
            print('\nError generating stochastics data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from stochastics data ', tsymbol, ': ', sys.exc_info()[0])

        try:
            macd_dip_score = 0
            macd_max_score = 10
            macd_signals = ''

            #MACD signals
            macd, macd_signal, macd_dip_score, macd_max_score, macd_signals = gmacd.get_macd_signals(tsymbol, df, path)

            self.overall_dip_score += macd_dip_score
            self.overall_max_score += macd_max_score

        except RuntimeError:
            print('\nError generating MACD data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from MACD data ', tsymbol, ': ', sys.exc_info()[0])

        try:
            kf_dip_score = 0
            kf_max_score = 10
            kf_signals = ''

            #Kalman Filter signals
            ds_sm, kf_dip_score, kf_max_score, kf_signals = gkf.get_kf_state_means(tsymbol, df)

            self.overall_dip_score += kf_dip_score
            self.overall_max_score += kf_max_score

        except RuntimeError:
            print('\nError generating Kalman filter data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from Kalman filter data ', tsymbol, ': ', sys.exc_info()[0])

        try:
            ols_dip_score = 0
            ols_max_score = 10
            ols_signals = ''

            #Ordinary Least Squares line signals
            y1_series, y_predictions, ols_dip_score, ols_max_score, ols_signals = gols.get_ols_signals(tsymbol, df, path)

            self.overall_dip_score += ols_dip_score
            self.overall_max_score += ols_max_score

        except RuntimeError:
            print('\nError generating OLS data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from OLS data ', tsymbol, ': ', sys.exc_info()[0])

        try:
            options_dip_score = 0
            options_max_score = 10
            options_signals = ''

            #Options signals
            options_dip_score, options_max_score, options_signals = gos.get_options_signals(tsymbol, path, df.Close[len(df)-1], df_summ)

            self.overall_dip_score += options_dip_score
            self.overall_max_score += options_max_score

        except:
            print('\nError while getting options signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            st_dip_score = 0
            st_max_score = 5
            st_signals = ''

            #StockTwits signals
            st_dip_score, st_max_score, st_signals = gstw.get_stocktwits_signals(tsymbol, path)

            self.overall_dip_score += st_dip_score
            self.overall_max_score += st_max_score

        except RuntimeError:
            print('\nError while getting stocktwits signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            #Get events info
            events_info = gge.get_events_info(tsymbol, path)
        except:
            print('\nError while getting events info for ', tsymbol, ': ', sys.exc_info()[0])
            events_info = ''

        overall_signals = f'{price_signals}\n{rsi_signals}\n{bb_signals}\n{macd_signals}\n{kf_signals}\n{ols_signals}\n{mfi_signals}\n{stoch_slow_signals}\n{options_signals}\n{pe_signals}\n{peg_signals}\n{beta_signals}\n{ihp_signals}\n{inshp_signals}\n{qbs_signals}\n{pbr_signals}\n{reco_signals}\n{st_signals}\n{events_info}\n{self.note}'

        try:
            gscsi.score_n_signals_save(tsymbol, path, self.overall_dip_score, self.overall_max_score, overall_signals)
        except:
            print('\nError while computing final score and saving signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            gsc.plot_n_save_charts(tsymbol, df, ub, mb, lb, rsi, mfi, macd, macd_signal, slowk, slowd, ds_sm, y_predictions, y1_series)
        except:
            print('\nError while drawing and saving charts for ', tsymbol, ': ', sys.exc_info()[0])

