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

import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path
from talib import RSI, BBANDS, MACD, MFI, STOCH
from matplotlib import pyplot as plt
try:
    from gammath_spot import gammath_price_signals as gps
    from gammath_spot import gammath_rsi_signals as grs
    from gammath_spot import gammath_bb_signals as gbbs
    from gammath_spot import gammath_mfi_signals as gms
    from gammath_spot import gammath_stoch_signals as gss
    from gammath_spot import gammath_macd_signals as gmacd
    from gammath_spot import gammath_stcktwts_signals as gstw
    from gammath_spot import gammath_kf_signals as gkf
    from gammath_spot import gammath_options_signals as gos
    from gammath_spot import gammath_pe_signals as gpes
    from gammath_spot import gammath_peg_signals as gpeg
    from gammath_spot import gammath_beta_signals as gbeta
    from gammath_spot import gammath_ihp_signals as gihp
    from gammath_spot import gammath_inshp_signals as ginshp
    from gammath_spot import gammath_qbs_signals as gqbs
    from gammath_spot import gammath_pbr_signals as gpbrs
    from gammath_spot import gammath_reco_signals as greco
    from gammath_spot import gammath_ols_signals as gols
    from gammath_spot import gammath_lgstic_signals as glgst
    from gammath_spot import gammath_get_stocks_events_data as gge
    from gammath_spot import gammath_score_signals as gscsi
    from gammath_spot import gammath_si_charts as gsc
except:
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
    import gammath_lgstic_signals as glgst
    import gammath_get_stocks_events_data as gge
    import gammath_score_signals as gscsi
    import gammath_si_charts as gsc

import sys
import time
import os
import numpy as np

class GSA:

    def __init__(self):
        self.Tickers_dir = Path('tickers')
        self.overall_gscore = 0
        self.overall_max_score = 100
        self.overall_sh_gscore = 0
        self.overall_sh_max_gscore = 0
        self.overall_sci_gscore = 0
        self.overall_sci_max_gscore = 0
        self.reco_signals_exist = False
        self.note = 'Notes: None'
        self.price_gscore = 0
        self.price_max_score = 10
        self.price_signals = ''
        self.price_final_score = 0

        self.rsi_gscore = 0
        self.rsi_max_score = 10
        self.rsi_signals = ''
        self.rsi_final_score = 0
        self.rsi_df = pd.DataFrame()

        self.mfi_gscore = 0
        self.mfi_max_score = 10
        self.mfi_signals = ''
        self.mfi_final_score = 0
        self.mfi_df = pd.DataFrame()

        self.stoch_gscore = 0
        self.stoch_max_score = 5
        self.stoch_slow_signals = ''
        self.stoch_final_score = 0
        self.stoch_df = pd.DataFrame()

        self.bb_gscore = 0
        self.bb_max_score = 10
        self.bb_signals = ''
        self.bb_final_score = 0
        self.bb_df = pd.DataFrame()

        self.macd_gscore = 0
        self.macd_max_score = 10
        self.macd_signals = ''
        self.macd_final_score = 0
        self.macd_df = pd.DataFrame()

        self.kf_gscore = 0
        self.kf_max_score = 10
        self.kf_signals = ''
        self.kf_final_score = 0
        self.kf_df = pd.DataFrame()

        self.ols_gscore = 0
        self.ols_max_score = 10
        self.ols_signals = ''
        self.ols_final_score = 0
        self.ols_df = pd.DataFrame()

        self.lgst_signals = ''

        self.total_sh_gscore = 0

        self.reco_gscore = 0
        self.reco_max_score = 0 #In case there is an exception, we should do fundamental analysis
        self.reco_signals = ''
        self.reco_final_score = 0

        self.options_gscore = 0
        self.options_max_score = 10
        self.options_signals = ''
        self.options_final_score = 0

        self.pe_gscore = 0
        self.pe_max_score = 2
        self.pe_signals = ''
        self.pe_final_score = 0

        self.peg_gscore = 0
        self.peg_max_score = 1
        self.peg_signals = ''
        self.peg_final_score = 0

        self.beta_gscore = 0
        self.beta_max_score = 1
        self.beta_signals = ''
        self.beta_final_score = 0

        self.pbr_gscore = 0
        self.pbr_max_score = 1
        self.pbr_signals = ''
        self.pbr_final_score = 0

        self.qbs_gscore = 0
        self.qbs_max_score = 4
        self.qbs_signals = ''
        self.qbs_final_score = 0

        self.ihp_gscore = 0
        self.ihp_max_score = 1
        self.ihp_signals = ''
        self.ihp_final_score = 0

        self.inshp_gscore = 0
        self.inshp_max_score = 1
        self.inshp_signals = ''
        self.inshp_final_score = 0

        self.st_gscore = 0
        self.st_max_score = 5
        self.st_signals = ''
        self.st_final_score = 0

        self.events_info = ''

        self.total_sci_gscore = 0

        self.total_final_score = 0
        self.overall_signals = ''

    def do_stock_history_analysis(self, tsymbol, path, df):

        #Generate and get signals based on Price history
        try:
            self.overall_sh_max_gscore += self.price_max_score

            #Price signals
            self.price_gscore, self.price_max_score, self.price_signals = gps.get_price_signals(tsymbol, df)
            self.overall_sh_gscore += self.price_gscore
            self.price_final_score = round(self.price_gscore/self.price_max_score, 3)
        except ValueError:
            print('\nERROR: generating price signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Relative Strength Index Indicator
        try:
            self.overall_sh_max_gscore += self.rsi_max_score

            #Relative Strength Index signals
            self.rsi_df, self.rsi_gscore, self.rsi_max_score, self.rsi_signals = grs.get_rsi_signals(tsymbol, df, path)
            self.overall_sh_gscore += self.rsi_gscore
            self.rsi_final_score = round(self.rsi_gscore/self.rsi_max_score, 3)
        except RuntimeError:
            print('\nERROR: generating RSI data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from RSI data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Money Flow Index Indicator
        try:
            self.overall_sh_max_gscore += self.mfi_max_score

            #MFI signals
            self.mfi_df, self.mfi_gscore, self.mfi_max_score, self.mfi_signals = gms.get_mfi_signals(tsymbol, df, path)
            self.overall_sh_gscore += self.mfi_gscore
            self.mfi_final_score = round(self.mfi_gscore/self.mfi_max_score, 3)

        except RuntimeError:
            print('\nERROR: generating MFI data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from MFI data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Stochastic Indicator
        try:
            self.overall_sh_max_gscore += self.stoch_max_score

            #Stochastic slow signals
            self.stoch_df, self.stoch_gscore, self.stoch_max_score, self.stoch_slow_signals = gss.get_stochastics_slow_signals(tsymbol, df)
            self.overall_sh_gscore += self.stoch_gscore
            self.stoch_final_score = round(self.stoch_gscore/self.stoch_max_score, 3)

        except RuntimeError:
            print('\nERROR: generating stochastics data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from stochastics data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Bollinger Bands Indicator
        try:
            self.overall_sh_max_gscore += self.bb_max_score

            #Bollinger bands signals
            self.bb_df, self.bb_gscore, self.bb_max_score, self.bb_signals = gbbs.get_bollinger_bands_signals(tsymbol, df, path)
            self.overall_sh_gscore += self.bb_gscore
            self.bb_final_score = round(self.bb_gscore/self.bb_max_score, 3)

        except RuntimeError:
            print('\nERROR: generating Bollinger Bands for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from Bollinger Bands for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Moving Average Convergence/Divergence Indicator
        try:
            self.overall_sh_max_gscore += self.macd_max_score

            #MACD signals
            self.macd_df, self.macd_gscore, self.macd_max_score, self.macd_signals = gmacd.get_macd_signals(tsymbol, df, path)
            self.overall_sh_gscore += self.macd_gscore
            self.macd_final_score = round(self.macd_gscore/self.macd_max_score, 3)
        except RuntimeError:
            print('\nERROR: generating MACD data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from MACD data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Kalman Filter state means
        try:
            self.overall_sh_max_gscore += self.kf_max_score

            #Kalman Filter signals
            self.kf_df, self.kf_gscore, self.kf_max_score, self.kf_signals = gkf.get_kf_state_means(tsymbol, df)
            self.overall_sh_gscore += self.kf_gscore
            self.kf_final_score = round(self.kf_gscore/self.kf_max_score, 3)

        except RuntimeError:
            print('\nERROR: generating Kalman filter data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from Kalman filter data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Ordinary Least Squares line
        try:
            self.overall_sh_max_gscore += self.ols_max_score

            #Ordinary Least Squares line signals
            self.ols_df, self.ols_gscore, self.ols_max_score, self.ols_signals = gols.get_ols_signals(tsymbol, df, path)
            self.overall_sh_gscore += self.ols_gscore
            self.ols_final_score = round(self.ols_gscore/self.ols_max_score, 3)
        except RuntimeError:
            print('\nERROR: generating OLS data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from OLS data ', tsymbol, ': ', sys.exc_info()[0])

        #TBD. Just log Logistic regression signal for now
        try:
            #Logistic regression signals; Usage will change later
            self.lgst_signals = glgst.get_lgstic_signals(tsymbol, df, path)

        except RuntimeError:
            print('\nERROR: generating Logistic regression data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from Logistic regression data ', tsymbol, ': ', sys.exc_info()[0])

        #Save the stock history specific gscore in proportion of overall max score
        self.total_sh_gscore = round(self.overall_sh_gscore/self.overall_max_score, 3)

        #Create a data frame for all stock history specific (micro)gScores
        sh_gScore_df = pd.DataFrame({'Price': self.price_final_score, 'RSI': self.rsi_final_score, 'BBANDS': self.bb_final_score, 'MACD': self.macd_final_score, 'KF': self.kf_final_score, 'OLS': self.ols_final_score, 'MFI': self.mfi_final_score, 'Stoch': self.stoch_final_score, 'Total': self.total_sh_gscore}, index=range(1))

        return sh_gScore_df

    def do_stock_current_info_analysis(self, tsymbol, path, df, df_summ):

        #Generate and get signals based on analyst recommendation
        try:
            #Reco signals
            self.reco_gscore, self.reco_max_score, self.reco_signals = greco.get_reco_signals(tsymbol, path)

            self.overall_sci_gscore += self.reco_gscore
            self.overall_sci_max_gscore += self.reco_max_score
            self.reco_signals_exist = ((self.reco_gscore != 0) and (self.reco_max_score != 0))
            if (self.reco_max_score > 0):
                self.reco_final_score = round(self.reco_gscore/self.reco_max_score, 3)
            else:
                self.reco_final_score = 0

        except RuntimeError:
            print('\nERROR: while getting reco signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on options activity
        try:
            self.overall_sci_max_gscore += self.options_max_score

            #Options signals
            self.options_gscore, self.options_max_score, self.options_signals = gos.get_options_signals(tsymbol, path, df.Close[len(df)-1], df_summ)
            self.overall_sci_gscore += self.options_gscore
            self.options_final_score = round(self.options_gscore/self.options_max_score, 3)
        except:
            print('\nERROR: while getting options signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on fundamental analysis (PE, PEG, Beta, PBR, Quarterly balancesheet, Institutional holdings). Use it for scoring only of analyst recommendation don't exist for us
        try:
            if not self.reco_signals_exist:
                self.overall_sci_max_gscore += self.pe_max_score

            #PE signals
            self.pe_gscore, self.pe_max_score, self.pe_signals = gpes.get_pe_signals(tsymbol, df_summ, self.Tickers_dir)
            if not self.reco_signals_exist:
                self.overall_sci_gscore += self.pe_gscore
            self.pe_final_score = round(self.pe_gscore/self.pe_max_score, 3)

        except ValueError:
            print('\nERROR: while getting PE signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            if not self.reco_signals_exist:
                self.overall_sci_max_gscore += self.peg_max_score

            #PEG signals
            self.peg_gscore, self.peg_max_score, self.peg_signals = gpeg.get_peg_signals(tsymbol, df_summ)

            if not self.reco_signals_exist:
                self.overall_sci_gscore += self.peg_gscore
            self.peg_final_score = round(self.peg_gscore/self.peg_max_score, 3)

        except ValueError:
            print('\nERROR: while getting PEG signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            if not self.reco_signals_exist:
                self.overall_sci_max_gscore += self.beta_max_score

            #Beta signals
            self.beta_gscore, self.beta_max_score, self.beta_signals = gbeta.get_beta_signals(tsymbol, df_summ)

            if not self.reco_signals_exist:
                self.overall_sci_gscore += self.beta_gscore
            self.beta_final_score = round(self.beta_gscore/self.beta_max_score, 3)
        except ValueError:
            print('\nERROR: while getting beta signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            if not self.reco_signals_exist:
                self.overall_sci_max_gscore += self.pbr_max_score

            #PBR signals
            self.pbr_gscore, self.pbr_max_score, self.pbr_signals = gpbrs.get_pbr_signals(tsymbol, df_summ)

            if not self.reco_signals_exist:
                self.overall_sci_gscore += self.pbr_gscore
            self.pbr_final_score = round(self.pbr_gscore/self.pbr_max_score, 3)
        except RuntimeError:
            print('\nERROR: while generating PBR signals for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: while getting PBR signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            if not self.reco_signals_exist:
                self.overall_sci_max_gscore += self.qbs_max_score

            #Quarterly Balance sheet signals
            self.qbs_gscore, self.qbs_max_score, self.qbs_signals = gqbs.get_qbs_signals(tsymbol, path, df_summ)

            if not self.reco_signals_exist:
                self.overall_sci_gscore += self.qbs_gscore
            self.qbs_final_score = round(self.qbs_gscore/self.qbs_max_score, 3)
        except ValueError:
            print('\nERROR: while getting QBS signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            if not self.reco_signals_exist:
                self.overall_sci_max_gscore += self.ihp_max_score

            #Institutional Holders Percentage signals
            self.ihp_gscore, self.ihp_max_score, self.ihp_signals = gihp.get_ihp_signals(tsymbol, df_summ)

            if not self.reco_signals_exist:
                self.overall_sci_gscore += self.ihp_gscore
            self.ihp_final_score = round(self.ihp_gscore/self.ihp_max_score, 3)
        except ValueError:
            print('\nERROR: while getting ihp signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            #Insider Holders Percentage signals
            self.inshp_gscore, self.inshp_max_score, self.inshp_signals = ginshp.get_inshp_signals(tsymbol, df_summ)
            self.inshp_final_score = round(self.inshp_gscore/self.inshp_max_score, 3)
        except ValueError:
            print('\nERROR: while getting inshp signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Stocktwits sentiment and volume change
        try:
            self.overall_sci_max_gscore += self.st_max_score

            #StockTwits signals
            self.st_gscore, self.st_max_score, self.st_signals = gstw.get_stocktwits_signals(tsymbol, path)
            self.overall_sci_gscore += self.st_gscore
            self.st_final_score = round(self.st_gscore/self.st_max_score, 3)
        except RuntimeError:
            print('\nERROR: while getting stocktwits signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Get info on earnings etc. to be aware before making buy/sell decision
        try:
            #Get events info
            self.events_info = gge.get_events_info(tsymbol, path)
        except:
            print('\nERROR: while getting events info for ', tsymbol, ': ', sys.exc_info()[0])
            self.events_info = ''

        #Save the stock current info specific gscore in proportion of total max score
        self.total_sci_gscore = round(self.overall_sci_gscore/self.overall_max_score, 3)

        #Create a data frame for all stock's current info specific (micro)gScores
        sci_gScore_df = pd.DataFrame({'Options': self.options_final_score, 'PE': self.pe_final_score, 'PEG': self.peg_final_score, 'Beta': self.beta_final_score, 'PBR': self.pbr_final_score, 'QBS': self.qbs_final_score, 'IHP': self.ihp_final_score, 'INSHP': self.inshp_final_score, 'Reco': self.reco_final_score, 'SENTI': self.st_final_score, 'Total': self.total_sci_gscore}, index=range(1))

        return sci_gScore_df

    def do_stock_analysis_and_compute_score(self, tsymbol, df):

        MIN_TRADING_DAYS_PER_YEAR = 249
        need_charts = False
        path = self.Tickers_dir / f'{tsymbol}'

        try:
            #Read Stock summary info into DataFrame.
            df_summ = pd.read_csv(path / f'{tsymbol}_summary.csv')
        except:
            print('\nERROR: Stock summary file not found for symbol ', tsymbol)
            return

        try:
            MIN_TRADING_DAYS_FOR_5_YEARS = (MIN_TRADING_DAYS_PER_YEAR*5)

            if not len(df):
                try:
                    df_orig = pd.read_csv(path / f'{tsymbol}_history.csv')
                    df_orig_len = len(df_orig)
                    start_index = (df_orig_len - MIN_TRADING_DAYS_FOR_5_YEARS)
                    if (start_index < 0):
                        raise ValueError('Not enough stock history')

                    end_index = df_orig_len

                    #Use a different df for starting with 0-index
                    df = df_orig.copy()
                    df.iloc[0:MIN_TRADING_DAYS_FOR_5_YEARS] = df_orig.iloc[start_index:end_index]
                    df = df.truncate(after=MIN_TRADING_DAYS_FOR_5_YEARS-1)
                    need_charts = True
                except:
                    raise RuntimeError('No price history data')

            #Check stock history data frame length.
            stock_history_len = len(df)

            #Analyze only if we have at least 5Y price data
            if (stock_history_len < MIN_TRADING_DAYS_FOR_5_YEARS):
                print(f'History doesn\'t have 5Y worth of data. Len: {stock_history_len} for {tsymbol}')
                raise RuntimeError('Not enough price history data')

            #Sometimes the price history doesn't have today's data.
            #Following is the workaround to detect that
            #This will show a note as an FYI (also if you ran it before market opens or on a holiday)
            dt = time.strftime('%x').split('/')
            df_ld = df.Date[stock_history_len-1]
            df_ld = df_ld.split('-')
            if ((int(dt[0]) != int(df_ld[1])) or (int(dt[1]) != int(df_ld[2]))):
                self.note = 'Note: NO_PRICE_DATA_FROM_TODAY'
        except:
            print('\nERROR: Stock price history error for ', tsymbol)
            return

        try:
            sh_gScore_df = self.do_stock_history_analysis(tsymbol, path, df)
        except:
            print('\nERROR: while computing stock history specific gscore for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            sci_gScore_df = self.do_stock_current_info_analysis(tsymbol, path, df, df_summ)
        except:
            print('\nERROR: while computing stock current info specific gscore for ', tsymbol, ': ', sys.exc_info()[0])

        #Augment all signals for saving in a file
        #TBD lgst_signals to be included for logging purposes only for now
        self.overall_signals = f'{self.price_signals}\n{self.rsi_signals}\n{self.bb_signals}\n{self.macd_signals}\n{self.kf_signals}\n{self.ols_signals}\n{self.mfi_signals}\n{self.stoch_slow_signals}\n{self.options_signals}\n{self.pe_signals}\n{self.peg_signals}\n{self.beta_signals}\n{self.ihp_signals}\n{self.inshp_signals}\n{self.qbs_signals}\n{self.pbr_signals}\n{self.reco_signals}\n{self.st_signals}\n{self.events_info}\n{self.note}\n{self.lgst_signals}'

        #Compute final score then save scores and signals
        self.overall_gscore = (self.overall_sh_gscore + self.overall_sci_gscore)

        try:
            gscsi.compute_final_score_and_save_signals(tsymbol, path, self.overall_gscore, self.overall_max_score, self.overall_signals)
        except:
            print('\nERROR: while computing final score and saving signals for ', tsymbol, ': ', sys.exc_info()[0])

        self.total_final_score = round(self.overall_gscore/self.overall_max_score, 3)

        #Create a data frame for all (micro)gScores
        gScore_df = pd.DataFrame({'Price': self.price_final_score, 'RSI': self.rsi_final_score, 'BBANDS': self.bb_final_score, 'MACD': self.macd_final_score, 'KF': self.kf_final_score, 'OLS': self.ols_final_score, 'MFI': self.mfi_final_score, 'Stoch': self.stoch_final_score, 'Options': self.options_final_score, 'PE': self.pe_final_score, 'PEG': self.peg_final_score, 'Beta': self.beta_final_score, 'PBR': self.pbr_final_score, 'QBS': self.qbs_final_score, 'IHP': self.ihp_final_score, 'INSHP': self.inshp_final_score, 'Reco': self.reco_final_score, 'SENTI': self.st_final_score, 'SH_Total': self.total_sh_gscore, 'SCI_Total': self.total_sci_gscore, 'Total': self.total_final_score}, index=range(1))

        #Save the CSV file for later reference
        gScore_df.to_csv(path / f'{tsymbol}_gscores.csv')

        #No need to draw charts for backtesting
        if need_charts:
            #Plot and save charts for reference
            try:
                gsc.plot_and_save_charts(tsymbol, path, self.bb_df, self.rsi_df, self.mfi_df, self.macd_df, self.stoch_df, self.kf_df, self.ols_df)
            except:
                print('\nERROR: while drawing and saving charts for ', tsymbol, ': ', sys.exc_info()[0])
