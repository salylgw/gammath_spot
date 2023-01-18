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
    from gammath_spot import gammath_pdp as gpdp
    from gammath_spot import gammath_mtpc as gmtpc
    from gammath_spot import gammath_get_stocks_events_data as gge
    from gammath_spot import gammath_si_charts as gsc
    from gammath_spot import gammath_tc as gtc
    from gammath_spot import gammath_utils as gut
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
    import gammath_pdp as gpdp
    import gammath_mtpc as gmtpc
    import gammath_get_stocks_events_data as gge
    import gammath_si_charts as gsc
    import gammath_tc as gtc
    import gammath_utils as gut

import sys
import time
import os
import numpy as np

class GSA:

    def __init__(self):
        self.Tickers_dir = Path('tickers')
        self.overall_sh_gscore = 0
        self.overall_sci_gscore = 0
        self.sh_signals = ''
        self.sci_signals = ''

    def do_stock_history_analysis(self, tsymbol, path, df, need_charts):

        #Generate and get signals based on Price history
        try:
            price_gscore = 0
            price_max_score = 10
            price_signals = ''
            price_final_score = 0

            #Price signals
            price_gscore, price_max_score, price_signals = gps.get_price_signals(tsymbol, df)
            price_final_score = round((price_gscore/price_max_score), 3)
            self.overall_sh_gscore += price_final_score
        except ValueError:
            print('\nERROR: generating price signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Relative Strength Index Indicator
        try:
            rsi_df = pd.DataFrame()
            rsi_gscore = 0
            rsi_max_score = 10
            rsi_signals = ''
            rsi_final_score = 0

            #Relative Strength Index signals
            rsi_df, rsi_gscore, rsi_max_score, rsi_signals = grs.get_rsi_signals(tsymbol, df, path)
            rsi_final_score = round((rsi_gscore/rsi_max_score), 3)
            self.overall_sh_gscore += rsi_final_score
        except RuntimeError:
            print('\nERROR: generating RSI data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from RSI data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Money Flow Index Indicator
        try:
            mfi_df = pd.DataFrame()
            mfi_gscore = 0
            mfi_max_score = 10
            mfi_signals = ''
            mfi_final_score = 0

            #MFI signals
            mfi_df, mfi_gscore, mfi_max_score, mfi_signals = gms.get_mfi_signals(tsymbol, df, path)
            mfi_final_score = round((mfi_gscore/mfi_max_score), 3)
            self.overall_sh_gscore += mfi_final_score
        except RuntimeError:
            print('\nERROR: generating MFI data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from MFI data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Stochastic Indicator
        try:
            stoch_df = pd.DataFrame()
            stoch_gscore = 0
            stoch_max_score = 5
            stoch_slow_signals = ''
            stoch_final_score = 0

            #Stochastic slow signals
            stoch_df, stoch_gscore, stoch_max_score, stoch_slow_signals = gss.get_stochastics_slow_signals(tsymbol, df)
            #Adjust for proportion
            stoch_final_score = round((stoch_gscore/(stoch_max_score<<1)), 3)
            self.overall_sh_gscore += stoch_final_score
        except RuntimeError:
            print('\nERROR: generating stochastics data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from stochastics data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Bollinger Bands Indicator
        try:
            bb_df = pd.DataFrame()
            bb_gscore = 0
            bb_max_score = 10
            bb_signals = ''
            bb_final_score = 0

            #Bollinger bands signals
            bb_df, bb_gscore, bb_max_score, bb_signals = gbbs.get_bollinger_bands_signals(tsymbol, df, path)
            bb_final_score = round((bb_gscore/bb_max_score), 3)
            self.overall_sh_gscore += bb_final_score
        except RuntimeError:
            print('\nERROR: generating Bollinger Bands for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from Bollinger Bands for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Moving Average Convergence/Divergence Indicator
        try:
            macd_df = pd.DataFrame()
            macd_gscore = 0
            macd_max_score = 10
            macd_signals = ''
            macd_final_score = 0

            #MACD signals
            macd_df, macd_gscore, macd_max_score, macd_signals = gmacd.get_macd_signals(tsymbol, df, path)
            macd_final_score = round((macd_gscore/macd_max_score), 3)
            self.overall_sh_gscore += macd_final_score
        except RuntimeError:
            print('\nERROR: generating MACD data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from MACD data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Kalman Filter state means
        try:
            kf_df = pd.DataFrame()
            kf_gscore = 0
            kf_max_score = 10
            kf_signals = ''

            #Kalman Filter signals
            kf_df, kf_gscore, kf_max_score, kf_signals = gkf.get_kf_state_means(tsymbol, df)
            kf_final_score = round((kf_gscore/kf_max_score), 3)
            self.overall_sh_gscore += kf_final_score

        except RuntimeError:
            print('\nERROR: generating Kalman filter data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from Kalman filter data ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Ordinary Least Squares line
        try:
            ols_df = pd.DataFrame()
            ols_gscore = 0
            ols_max_score = 10
            ols_signals = 0

            #Ordinary Least Squares line signals
            ols_df, ols_gscore, ols_max_score, ols_signals = gols.get_ols_signals(tsymbol, df, path)
            ols_final_score = round((ols_gscore/ols_max_score), 3)
            self.overall_sh_gscore += ols_final_score
        except RuntimeError:
            print('\nERROR: generating OLS data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from OLS data ', tsymbol, ': ', sys.exc_info()[0])

        # Price direction probability (overall and next day)
        try:
            nup = 0
            pdp = ''

            #Get the next day probability for decision-making
            nup, pdp = gpdp.get_price_dir_probability(df)
        except ValueError:
            print('\nERROR: generating next day price direction probability for ', tsymbol, ': ', sys.exc_info()[0])

        # Moving Technical 5Y Price Conjecture
        try:
            tpc5y = 0
            mtcp = ''

            #Get 5Y price conjecture for decision-making
            tpc5y, mtcp = gmtpc.get_moving_technical_price_conjecture(df)
        except ValueError:
            print('\nERROR: generating moving 5y technical price conjecture for ', tsymbol, ': ', sys.exc_info()[0])

        # Logistic regression signals
        try:
            a5dup = 0
            a20dup = 0
            lgst_signals = ''

            a5dup, a20dup, lgst_signals = glgst.get_lgstic_signals(tsymbol, df, path)
        except RuntimeError:
            print('\nERROR: generating Logistic regression data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: generating signals from Logistic regression data ', tsymbol, ': ', sys.exc_info()[0])

        # Get support and resistance level
        try:
            current_support_level_y = 0
            support_line_slope = 0
            pdsl = 0
            current_resistance_level_y = 0
            resistance_line_slope = 0
            pdrl = 0
            gtrends = gtc.GTRENDS()
            sr_df = gtrends.compute_support_and_resistance_levels(tsymbol, path, df, need_charts)
            #Extract data
            current_support_level_y = sr_df['CS_Y'][0]
            support_line_slope = sr_df['SLS'][0]
            pdsl = sr_df['PDSL'][0]
            current_resistance_level_y = sr_df['CR_Y'][0]
            resistance_line_slope = sr_df['RLS'][0]
            pdrl = sr_df['PDRL'][0]
            #Log support and resistance level for convenient reference
            support_resistance_string = f'Current Approx. Moving Support level: {current_support_level_y},support_line_slope:{support_line_slope},pct_diff: {pdsl}\nCurrent Approx. Moving Resistance level: {current_resistance_level_y},resistance_line_slope:{resistance_line_slope},pct_diff:{pdrl}'
        except:
            print('\nERROR: generating support and resistance level data ', tsymbol, ': ', sys.exc_info()[0])

        #Create a data frame for all stock history specific (micro)gScores
        df_len = len(df)
        sh_gScore_df = pd.DataFrame({'Date': df.Date[df_len-1].split(' ')[0], 'Close': round(df.Close[df_len-1], 3), 'Price': price_final_score, 'RSI': rsi_final_score, 'BBANDS': bb_final_score, 'MACD': macd_final_score, 'KF': kf_final_score, 'OLS': ols_final_score, 'MFI': mfi_final_score, 'Stoch': stoch_final_score, 'SH_gScore': round((self.overall_sh_gscore/10), 3), 'NUP': nup, 'A5DUP': a5dup, 'A20DUP': a20dup, 'TPC5Y': tpc5y, 'CSL': current_support_level_y, 'SLS': support_line_slope, 'PDSL': pdsl, 'CRL': current_resistance_level_y, 'RLS': resistance_line_slope, 'PDRL': pdrl}, index=range(1))

        #No need to draw charts for backtesting
        if need_charts:
            #Plot and save charts for reference
            try:
                gsc.plot_and_save_charts(tsymbol, path, bb_df, rsi_df, mfi_df, macd_df, stoch_df, kf_df, ols_df)
            except:
                print('\nERROR: while drawing and saving charts for ', tsymbol, ': ', sys.exc_info()[0])


        #Aggregate stock history-specific signals
        self.sh_signals = '\n'.join([price_signals, rsi_signals, bb_signals, macd_signals, kf_signals, ols_signals, mfi_signals, stoch_slow_signals, pdp, mtcp, lgst_signals, support_resistance_string])

        return sh_gScore_df

    def do_stock_current_info_analysis(self, tsymbol, path, df, df_summ):

        reco_signals_exist = False

        #Generate and get signals based on analyst recommendation
        try:
            #Reco signals
            reco_gscore = 0
            reco_max_score = 0
            reco_signals = ''
            reco_final_score = 0

            reco_gscore, reco_max_score, reco_signals = greco.get_reco_signals(tsymbol, path)

            reco_signals_exist = ((reco_gscore != 0) and (reco_max_score != 0))
            if (reco_max_score > 0):
                reco_final_score = round((reco_gscore/reco_max_score), 3)
                self.overall_sci_gscore += reco_final_score

        except RuntimeError:
            print('\nERROR: while getting reco signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on options activity
        try:
            options_gscore = 0
            options_max_score = 10
            options_signals = ''
            options_final_score = 0

            #Options signals
            options_gscore, options_max_score, options_signals = gos.get_options_signals(tsymbol, path, df.Close[len(df)-1], df_summ)
            options_final_score = round((options_gscore/options_max_score), 3)
            self.overall_sci_gscore += options_final_score
        except:
            print('\nERROR: while getting options signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on fundamental analysis (PE, PEG, Beta, PBR, Quarterly balancesheet, Institutional holdings). Use it for scoring only of analyst recommendation don't exist for us
        try:
            pe_gscore = 0
            pe_max_score = 2
            pe_signals = ''
            pe_final_score = 0

            #PE signals
            pe_gscore, pe_max_score, pe_signals = gpes.get_pe_signals(tsymbol, df_summ, self.Tickers_dir)
            #Maintain proportion
            pe_final_score = round((pe_gscore/10), 3)
            if not reco_signals_exist:
                self.overall_sci_gscore += pe_final_score

        except ValueError:
            print('\nERROR: while getting PE signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            peg_gscore = 0
            peg_max_score = 1
            peg_signals = ''
            peg_final_score = 0

            #PEG signals
            peg_gscore, peg_max_score, peg_signals = gpeg.get_peg_signals(tsymbol, df_summ)

            #Maintain proportion
            peg_final_score = round((peg_gscore/10), 3)
            if not reco_signals_exist:
                self.overall_sci_gscore += peg_final_score

        except ValueError:
            print('\nERROR: while getting PEG signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            beta_gscore = 0
            beta_max_score = 1
            beta_signals = ''
            beta_final_score = 0

            #Beta signals
            beta_gscore, beta_max_score, beta_signals = gbeta.get_beta_signals(tsymbol, df_summ)

            #Maintain proportion
            beta_final_score = round((beta_gscore/10), 3)
            if not reco_signals_exist:
                self.overall_sci_gscore += beta_final_score

        except ValueError:
            print('\nERROR: while getting beta signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            pbr_gscore = 0
            pbr_max_score = 1
            pbr_signals = ''
            pbr_final_score = 0

            #PBR signals
            pbr_gscore, pbr_max_score, pbr_signals = gpbrs.get_pbr_signals(tsymbol, df_summ)

            pbr_final_score = round((pbr_gscore/10), 3)
            if not reco_signals_exist:
                self.overall_sci_gscore += pbr_final_score
        except RuntimeError:
            print('\nERROR: while generating PBR signals for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nERROR: while getting PBR signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            qbs_gscore = 0
            qbs_max_score = 4
            qbs_signals = ''
            qbs_final_score = 0

            #Quarterly Balance sheet signals
            qbs_gscore, qbs_max_score, qbs_signals = gqbs.get_qbs_signals(tsymbol, path, df_summ)

            #Maintain proportion
            qbs_final_score = round((qbs_gscore/10), 3)
            if not reco_signals_exist:
                self.overall_sci_gscore += qbs_final_score
        except ValueError:
            print('\nERROR: while getting QBS signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            ihp_gscore = 0
            ihp_max_score = 1
            ihp_signals = ''
            ihp_final_score = 0

            #Institutional Holders Percentage signals
            ihp_gscore, ihp_max_score, ihp_signals = gihp.get_ihp_signals(tsymbol, df_summ)

            #Maintain proportion
            ihp_final_score = round((ihp_gscore/10), 3)
            if not reco_signals_exist:
                self.overall_sci_gscore += ihp_final_score
        except ValueError:
            print('\nERROR: while getting ihp signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            inshp_gscore = 0
            inshp_max_score = 1
            inshp_signals = ''

            #Insider Holders Percentage signals
            #Not included in overall sci score. For reference only
            inshp_gscore, inshp_max_score, inshp_signals = ginshp.get_inshp_signals(tsymbol, df_summ)
        except ValueError:
            print('\nERROR: while getting inshp signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Generate and get signals based on Stocktwits sentiment and volume change
        try:
            st_gscore = 0
            st_max_score = 5
            st_signals = ''
            st_final_score = 0

            #StockTwits signals
            st_gscore, st_max_score, st_signals = gstw.get_stocktwits_signals(tsymbol, path)
            #Maintain proportion
            st_final_score = round((st_gscore/10), 3)
            self.overall_sci_gscore += st_final_score
        except RuntimeError:
            print('\nERROR: while getting stocktwits signals for ', tsymbol, ': ', sys.exc_info()[0])

        #Get info on earnings etc. to be aware before making buy/sell decision
        try:
            #Get events info
            events_info = gge.get_events_info(tsymbol, path)
        except:
            print('\nERROR: while getting events info for ', tsymbol, ': ', sys.exc_info()[0])
            events_info = ''

        #Create a data frame for all stock's current info specific (micro)gScores
        sci_gScore_df = pd.DataFrame({'Options': options_final_score, 'PE': pe_final_score, 'PEG': peg_final_score, 'Beta': beta_final_score, 'PBR': pbr_final_score, 'QBS': qbs_final_score, 'IHP': ihp_final_score, 'Reco': reco_final_score, 'SENTI': st_final_score, 'SCI_gScore': round((self.overall_sci_gscore/10), 3)}, index=range(1))

        #Aggregate stock current info-specific signals
        self.sci_signals = '\n'.join([options_signals, pe_signals, peg_signals, beta_signals, pbr_signals, qbs_signals, ihp_signals, inshp_signals, reco_signals, st_signals, events_info])

        return sci_gScore_df

    def do_stock_analysis_and_compute_score(self, tsymbol, df):

        mtdpy, mtd5y = gut.get_min_trading_days()
        path = self.Tickers_dir / f'{tsymbol}'
        sh_gScore_df = pd.DataFrame()
        sci_gScore_df = pd.DataFrame()
        note = 'Notes: None'

        try:
            #Read Stock summary info into DataFrame.
            df_summ = pd.read_csv(path / f'{tsymbol}_summary.csv')
        except:
            print('\nERROR: Stock summary file not found for symbol ', tsymbol)
            return

        try:
            if not len(df):
                try:
                    df_orig = pd.read_csv(path / f'{tsymbol}_history.csv')
                    df_orig_len = len(df_orig)
                    start_index = (df_orig_len - mtd5y)
                    if (start_index < 0):
                        raise ValueError('Not enough stock history')

                    end_index = df_orig_len

                    #Use a different df for starting with 0-index
                    df = df_orig.copy()
                    df.iloc[0:mtd5y] = df_orig.iloc[start_index:end_index]
                    df = df.truncate(after=mtd5y-1)
                except:
                    raise RuntimeError('No price history data')

            #Check stock history data frame length.
            stock_history_len = len(df)

            #Analyze only if we have at least 5Y price data
            if (stock_history_len < mtd5y):
                print(f'History doesn\'t have 5Y worth of data. Len: {stock_history_len} for {tsymbol}')
                raise RuntimeError('Not enough price history data')

            #Sometimes the price history doesn't have today's data.
            #Following is the workaround to detect that
            #This will show a note as an FYI (also if you ran it before market opens or on a holiday)
            dt = time.strftime('%x').split('/')
            df_ld = df.Date[stock_history_len-1]
            #Date field format appears to have changed. Following is t accomodate that
            #We only want the date part
            df_ld = df_ld.split(' ')
            #Get year, month, date
            df_ld = df_ld[0].split('-')
            if ((int(dt[0]) != int(df_ld[1])) or (int(dt[1]) != int(df_ld[2]))):
                note = 'Note: NO_PRICE_DATA_FROM_TODAY'
        except:
            print('\nERROR: Stock price history error for ', tsymbol)
            return

        try:
            sh_gScore_df = self.do_stock_history_analysis(tsymbol, path, df, True)
        except:
            print('\nERROR: while computing stock history specific gscore for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            sci_gScore_df = self.do_stock_current_info_analysis(tsymbol, path, df, df_summ)
        except:
            print('\nERROR: while computing stock current info specific gscore for ', tsymbol, ': ', sys.exc_info()[0])

        #Add up micro-gScores then save scores and signals
        overall_gscore = round(((self.overall_sh_gscore + self.overall_sci_gscore)/10), 3)

        final_gscore_string = f'final_gscore:{overall_gscore}'

        #Get all signals info for saving in a file for later reference
        overall_signals = '\n'.join([self.sh_signals, self.sci_signals, note, final_gscore_string])

        #Create a data frame for all (micro)gScores
        gScore_df = pd.DataFrame({'gScore': overall_gscore}, index=range(1))
        gScore_df = gScore_df.join(pd.DataFrame.join(sh_gScore_df, sci_gScore_df))

        #Save the CSV file for later reference
        gScore_df.to_csv(path / f'{tsymbol}_gscores.csv')

        try:
            f = open(path / f'{tsymbol}_signal.txt', 'w')
        except:
            print('\nERROR: opening signal file for ', tsymbol, ': ', sys.exc_info()[0])
        else:
            f.write(f'{overall_signals}\n')
            f.close()
