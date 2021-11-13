# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
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
        self.Tickers_dir = Path('tickers')
        self.overall_dip_score = 0
        self.overall_max_score = 0
        self.reco_signals_exist = False
        self.note = 'Notes: None'

    def do_stock_analysis_and_compute_score(self, tsymbol):

        path = self.Tickers_dir / f'{tsymbol}'

        try:
            #Read Stock summary info into DataFrame.
            df_summ = pd.read_csv(path / f'{tsymbol}_summary.csv')
        except:
            print('\nERROR: Stock summary file not found for symbol ', tsymbol)
            return

        try:
            #Read CSV into DataFrame.
            df = pd.read_csv(path / f'{tsymbol}_history.csv')
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

        #Generate and get signals based on analyst recommendation
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
            print('\nERROR: while getting reco signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on options activity
        try:
            options_dip_score = 0
            options_max_score = 10
            options_signals = ''

            #Options signals
            options_dip_score, options_max_score, options_signals = gos.get_options_signals(tsymbol, path, df.Close[len(df)-1], df_summ)

            self.overall_dip_score += options_dip_score
            self.overall_max_score += options_max_score

        except:
            print('\nERROR: while getting options signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on fundamental analysis (PE, PEG, Beta, PBR, Quarterly balancesheet, Institutional holdings). Use it for scoring only of analyst recommendation don't exist for us
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
            print('\nERROR: while getting PE signals for ', tsymbol, ': ', sys.exc_info()[0])

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
            print('\nERROR: while getting PEG signals for ', tsymbol, ': ', sys.exc_info()[0])

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
            print('\nERROR: while getting beta signals for ', tsymbol, ': ', sys.exc_info()[0])

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
            print('\nERROR: while generating PBR signals for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: while getting PBR signals for ', tsymbol, ': ', sys.exc_info()[0])

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
            print('\nERROR: while getting QBS signals for ', tsymbol, ': ', sys.exc_info()[0])

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
            print('\nERROR: while getting ihp signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            inshp_dip_score = 0
            inshp_max_score = 1
            inshp_signals = ''

            #Insider Holders Percentage signals
            inshp_dip_score, inshp_max_score, inshp_signals = ginshp.get_inshp_signals(tsymbol, df_summ)
        except ValueError:
            print('\nERROR: while getting inshp signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Price history
        try:
            price_dip_score = 0
            price_max_score = 10
            price_signals = ''
            #Price signals
            price_dip_score, price_max_score, price_signals = gps.get_price_signals(tsymbol, df, df_summ)

            self.overall_dip_score += price_dip_score
            self.overall_max_score += price_max_score

        except ValueError:
            print('\nERROR: generating price signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Relative Strength Index Indicator
        try:
            rsi_dip_score = 0
            rsi_max_score = 10
            rsi_signals = ''
            #Relative Strength Index signals
            rsi_df, rsi_dip_score, rsi_max_score, rsi_signals = grs.get_rsi_signals(tsymbol, df, path)

            self.overall_dip_score += rsi_dip_score
            self.overall_max_score += rsi_max_score

        except RuntimeError:
            print('\nERROR: generating RSI data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from RSI data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Money Flow Index Indicator
        try:
            mfi_dip_score = 0
            mfi_max_score = 10
            mfi_signals = ''

            #MFI signals
            mfi_df, mfi_dip_score, mfi_max_score, mfi_signals = gms.get_mfi_signals(tsymbol, df, path)

            self.overall_dip_score += mfi_dip_score
            self.overall_max_score += mfi_max_score

        except RuntimeError:
            print('\nERROR: generating MFI data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from MFI data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Stochastic Indicator
        try:
            stoch_dip_score = 0
            stoch_max_score = 5
            stoch_slow_signals = ''

            #Stochastic slow signals
            stoch_df, stoch_dip_score, stoch_max_score, stoch_slow_signals = gss.get_stochastics_slow_signals(tsymbol, df)

            self.overall_dip_score += stoch_dip_score
            self.overall_max_score += stoch_max_score

        except RuntimeError:
            print('\nERROR: generating stochastics data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from stochastics data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Bollinger Bands Indicator
        try:
            bb_dip_score = 0
            bb_max_score = 10
            bb_signals = ''
            #Bollinger bands signals
            bb_df, bb_dip_score, bb_max_score, bb_signals = gbbs.get_bollinger_bands_signals(tsymbol, df, path)

            self.overall_dip_score += bb_dip_score
            self.overall_max_score += bb_max_score

        except RuntimeError:
            print('\nERROR: generating Bollinger Bands for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from Bollinger Bands for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Moving Average Convergence/Divergence Indicator
        try:
            macd_dip_score = 0
            macd_max_score = 10
            macd_signals = ''

            #MACD signals
            macd_df, macd_dip_score, macd_max_score, macd_signals = gmacd.get_macd_signals(tsymbol, df, path)

            self.overall_dip_score += macd_dip_score
            self.overall_max_score += macd_max_score

        except RuntimeError:
            print('\nERROR: generating MACD data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from MACD data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Kalman Filter state means
        try:
            kf_dip_score = 0
            kf_max_score = 10
            kf_signals = ''

            #Kalman Filter signals
            kf_df, kf_dip_score, kf_max_score, kf_signals = gkf.get_kf_state_means(tsymbol, df)

            self.overall_dip_score += kf_dip_score
            self.overall_max_score += kf_max_score

        except RuntimeError:
            print('\nERROR: generating Kalman filter data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from Kalman filter data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Ordinary Least Squares line
        try:
            ols_dip_score = 0
            ols_max_score = 10
            ols_signals = ''

            #Ordinary Least Squares line signals
            ols_df, ols_dip_score, ols_max_score, ols_signals = gols.get_ols_signals(tsymbol, df, path)

            self.overall_dip_score += ols_dip_score
            self.overall_max_score += ols_max_score

        except RuntimeError:
            print('\nERROR: generating OLS data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from OLS data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Stocktwits sentiment and volume change
        try:
            st_dip_score = 0
            st_max_score = 5
            st_signals = ''

            #StockTwits signals
            st_dip_score, st_max_score, st_signals = gstw.get_stocktwits_signals(tsymbol, path)

            self.overall_dip_score += st_dip_score
            self.overall_max_score += st_max_score

        except RuntimeError:
            print('\nERROR: while getting stocktwits signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Get info on earnings etc. to be aware before making buy/sell decision
        try:
            #Get events info
            events_info = gge.get_events_info(tsymbol, path)
        except:
            print('\nERROR: while getting events info for ', tsymbol, ': ', sys.exc_info()[0])
            events_info = ''

        #Augment all signals for saving in a file
        overall_signals = f'{price_signals}\n{rsi_signals}\n{bb_signals}\n{macd_signals}\n{kf_signals}\n{ols_signals}\n{mfi_signals}\n{stoch_slow_signals}\n{options_signals}\n{pe_signals}\n{peg_signals}\n{beta_signals}\n{ihp_signals}\n{inshp_signals}\n{qbs_signals}\n{pbr_signals}\n{reco_signals}\n{st_signals}\n{events_info}\n{self.note}'

        #Compute final score then save scores and signals
        try:
            gscsi.compute_final_score_and_save_signals(tsymbol, path, self.overall_dip_score, self.overall_max_score, overall_signals)
        except:
            print('\nERROR: while computing final score and saving signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Plot and save charts for reference
        try:
            gsc.plot_and_save_charts(tsymbol, bb_df, rsi_df, mfi_df, macd_df, stoch_df, kf_df, ols_df)
        except:
            print('\nERROR: while drawing and saving charts for ', tsymbol, ': ', sys.exc_info()[0])
