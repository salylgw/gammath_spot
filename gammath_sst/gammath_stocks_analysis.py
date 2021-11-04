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
import gammath_lgstic_signals as glgs
import gammath_get_events as gge
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
            return
        except:
            print('\nERROR: Stock history file not found for ', tsymbol)
            return

        try:
            reco_buy_score = reco_sell_score = 0
            reco_max_score = 0 #In case there is an exception, we should do fundamental analysis
            reco_signals = ''
            #Reco signals
            reco_buy_score, reco_sell_score, reco_max_score, reco_signals = greco.get_reco_signals(tsymbol, path)
        except RuntimeError:
            print('\nError while getting reco signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            pe_buy_score = pe_sell_score = 0
            pe_max_score = 2
            pe_signals = ''

            #PE signals
            pe_buy_score, pe_sell_score, pe_max_score, pe_signals = gpes.get_pe_signals(tsymbol, df_summ)
        except ValueError:
            print('\nError while getting PE signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            peg_buy_score = peg_sell_score = 0
            peg_max_score = 1
            peg_signals = ''

            #PEG signals
            peg_buy_score, peg_sell_score, peg_max_score, peg_signals = gpeg.get_peg_signals(tsymbol, df_summ)
        except ValueError:
            print('\nError while getting PEG signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            beta_buy_score = beta_sell_score = 0
            beta_max_score = 1
            beta_signals = ''

            #Beta signals
            beta_buy_score, beta_sell_score, beta_max_score, beta_signals = gbeta.get_beta_signals(tsymbol, df_summ)
        except ValueError:
            print('\nError while getting beta signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            pbr_buy_score = pbr_sell_score = 0
            pbr_max_score = 1
            pbr_signals = ''

            #PBR signals
            pbr_buy_score, pbr_sell_score, pbr_max_score, pbr_signals = gpbrs.get_pbr_signals(tsymbol, df_summ)
        except RuntimeError:
            print('\nError while generating PBR signals for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError while getting PBR signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            qbs_buy_score = qbs_sell_score = 0
            qbs_max_score = 4
            qbs_signals = ''

            #Quarterly Balance sheet signals
            qbs_buy_score, qbs_sell_score, qbs_max_score, qbs_signals = gqbs.get_qbs_signals(tsymbol, path)
        except ValueError:
            print('\nError while getting QBS signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            ihp_buy_score = ihp_sell_score = 0
            ihp_max_score = 1
            ihp_signals = ''

            #Institutional Holders Percentage signals
            ihp_buy_score, ihp_sell_score, ihp_max_score, ihp_signals = gihp.get_ihp_signals(tsymbol, df_summ)
        except ValueError:
            print('\nError while getting ihp signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            inshp_buy_score = inshp_sell_score = 0
            inshp_max_score = 1
            inshp_signals = ''

            #Insider Holders Percentage signals
            inshp_buy_score, inshp_sell_score, inshp_max_score, inshp_signals = ginshp.get_inshp_signals(tsymbol, df_summ)
        except ValueError:
            print('\nError while getting inshp signals for ', tsymbol, ': ', sys.exc_info()[0])

        if (((reco_buy_score != 0) or (reco_sell_score != 0)) and (reco_max_score != 0)):

            print('\nThere are reco signals for ', tsymbol)

            #Omit buy/sell scores for fundamental analysis as analyst recommendation score is used for those stocks

            pe_buy_score = pe_sell_score = pe_max_score = 0
            peg_buy_score = peg_sell_score = peg_max_score = 0
            beta_buy_score = beta_sell_score = beta_max_score = 0
            pbr_buy_score = pbr_sell_score = pbr_max_score = 0
            qbs_buy_score = qbs_sell_score = qbs_max_score = 0
            ihp_buy_score = ihp_sell_score = ihp_max_score = 0
            inshp_buy_score = inshp_sell_score = inshp_max_score = 0

        try:
            price_buy_score = price_sell_score = 0
            price_max_score = 10
            price_signals = ''
            #Price signals
            price_buy_score, price_sell_score, price_max_score, price_signals = gps.get_price_signals(tsymbol, df, df_summ)
        except ValueError:
            print('\nError generating price signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            rsi_buy_score = rsi_sell_score = 0
            rsi_max_score = 10
            rsi_signals = ''
            #Relative Strength Index signals
            rsi, rsi_buy_score, rsi_sell_score, rsi_max_score, rsi_signals = grs.get_rsi_signals(tsymbol, df, path)
        except RuntimeError:
            print('\nError generating RSI data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from RSI data ', tsymbol, ': ', sys.exc_info()[0])

        try:
            bb_buy_score = bb_sell_score = 0
            bb_max_score = 10
            bb_signals = ''
            #Bollinger bands signals
            mb, ub, lb, bb_buy_score, bb_sell_score, bb_max_score, bb_signals = gbbs.get_bollinger_bands_signals(tsymbol, df, path)
        except RuntimeError:
            print('\nError generating Bollinger Bands for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from Bollinger Bands for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            mfi_buy_score = mfi_sell_score = 0
            mfi_max_score = 10
            mfi_signals = ''

            #MFI signals
            mfi, mfi_buy_score, mfi_sell_score, mfi_max_score, mfi_signals = gms.get_mfi_signals(tsymbol, df, path)
        except RuntimeError:
            print('\nError generating MFI data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from MFI data ', tsymbol, ': ', sys.exc_info()[0])

        try:
            stoch_buy_score = stoch_sell_score = 0
            stoch_max_score = 5
            stoch_slow_signals = ''

            #Stochastic slow signals
            slowk, slowd, stoch_buy_score, stoch_sell_score, stoch_max_score, stoch_slow_signals = gss.get_stochastics_slow_signals(tsymbol, df)
        except RuntimeError:
            print('\nError generating stochastics data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from stochastics data ', tsymbol, ': ', sys.exc_info()[0])

        try:
            macd_buy_score = macd_sell_score = 0
            macd_max_score = 10
            macd_signals = ''

            #MACD signals
            macd, macd_signal, macd_buy_score, macd_sell_score, macd_max_score, macd_signals = gmacd.get_macd_signals(tsymbol, df, path)
        except RuntimeError:
            print('\nError generating MACD data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from MACD data ', tsymbol, ': ', sys.exc_info()[0])

        try:
            kf_buy_score = kf_sell_score = 0
            kf_max_score = 10
            kf_signals = ''

            #Kalman Filter signals
            ds_sm, kf_buy_score, kf_sell_score, kf_max_score, kf_signals = gkf.get_kf_state_means(tsymbol, df)
        except RuntimeError:
            print('\nError generating Kalman filter data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from Kalman filter data ', tsymbol, ': ', sys.exc_info()[0])

        try:
            ols_buy_score = ols_sell_score = 0
            ols_max_score = 10
            ols_signals = ''

            #Ordinary Least Squares line signals
            ols_y1_predictions, ols_y_predictions, ols_buy_score, ols_sell_score, ols_max_score, ols_signals = gols.get_ols_signals(tsymbol, df, path)
        except RuntimeError:
            print('\nError generating OLS data for ', tsymbol, ': ', sys.exc_info()[0])
        except ValueError:
            print('\nError generating signals from OLS data ', tsymbol, ': ', sys.exc_info()[0])

        try:
            #Logistic regression signals
            lgstic_signals = glgs.get_lgstic_signals(tsymbol, df, path)
        except:
            print('\nError while getting lgstic regr signals for ', tsymbol, ': ', sys.exc_info()[0])
            lgstic_signals = ''

        try:
            options_buy_score = options_sell_score = 0
            options_max_score = 10
            options_signals = ''

            #Options signals
            options_buy_score, options_sell_score, options_max_score, options_signals = gos.get_options_signals(tsymbol, path, df.Close[len(df)-1], df_summ)
        except:
            print('\nError while getting options signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            st_buy_score = st_sell_score = 0
            st_max_score = 5
            st_signals = ''

            #StockTwits signals
            st_buy_score, st_sell_score, st_max_score, st_signals = gstw.get_stocktwits_signals(tsymbol, path)
        except RuntimeError:
            print('\nError while getting stocktwits signals for ', tsymbol, ': ', sys.exc_info()[0])

        try:
            #Get events info
            events_info = gge.get_events_info(tsymbol, path)
        except:
            print('\nError while getting events info for ', tsymbol, ': ', sys.exc_info()[0])
            events_info = ''

        overall_buy_score = price_buy_score + rsi_buy_score + bb_buy_score + mfi_buy_score + stoch_buy_score + macd_buy_score + kf_buy_score + ols_buy_score + options_buy_score + pe_buy_score + peg_buy_score + beta_buy_score + ihp_buy_score  + qbs_buy_score + pbr_buy_score + reco_buy_score + st_buy_score
        overall_sell_score = price_sell_score + rsi_sell_score + bb_sell_score + mfi_sell_score + stoch_sell_score + macd_sell_score + kf_sell_score + ols_sell_score + options_sell_score + pe_sell_score + peg_sell_score + beta_sell_score + ihp_sell_score + qbs_sell_score + pbr_sell_score + reco_sell_score + st_sell_score
        overall_max_score = price_max_score + rsi_max_score + bb_max_score + mfi_max_score + stoch_max_score + macd_max_score + kf_max_score + ols_max_score + options_max_score + pe_max_score + peg_max_score + beta_max_score + ihp_max_score + qbs_max_score + pbr_max_score + reco_max_score + st_max_score

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
            f.write(f'{price_signals}\n{rsi_signals}\n{bb_signals}\n{macd_signals}\n{kf_signals}\n{ols_signals}\n{lgstic_signals}\n{mfi_signals}\n{stoch_slow_signals}\n{options_signals}\n{pe_signals}\n{peg_signals}\n{beta_signals}\n{ihp_signals}\n{inshp_signals}\n{qbs_signals}\n{pbr_signals}\n{reco_signals}\n{st_signals}\n{overall_buy_rec}\n{overall_sell_rec}\n{final_buy_score_rec}\n{final_sell_score_rec}\n{events_info}')
            f.close()

        try:
            gsc.plot_n_save_charts(tsymbol, df, ub, mb, lb, rsi, mfi, macd, macd_signal, slowk, slowd, ds_sm, ols_y_predictions, ols_y1_predictions)
        except:
            print(f'\nCharts not drawn for {tsymbol} due to missing params')

    def aggregate_scores(self):
        print('\nGSA aggregate_scores')

        #Get all the subdirs. Need to check for is_dir
        p = self.Tickers_dir

        #Somehow looks like os.is_dir isn't supported
        #Using pathlib/Path instead since is_dir is supported there
        subdirs = [x for x in p.iterdir() if x.is_dir()]

        print('\nNum of subdirs: ', len(subdirs))

        pattern_for_final_buy_score = re.compile(r'(final_buy_score):([-]*[0-9]*[.]*[0-9]+)')
        pattern_for_final_sell_score = re.compile(r'(final_sell_score):([-]*[0-9]*[.]*[0-9]+)')

        #Collect 1Y OLS regression fit scores for debugging
        pattern_for_1y_ols_fit_score = re.compile(r'(ols_1y_fit_score):([-]*[0-9]*[.]*[0-9]+)')

        #Collect OLS regression fit scores for debugging
        pattern_for_ols_fit_score = re.compile(r'(ols_fit_score):([-]*[0-9]*[.]*[0-9]+)')

        df_b = pd.DataFrame(columns=['Ticker', 'final_buy_score'], index=range(len(subdirs)))

        df_s = pd.DataFrame(columns=['Ticker', 'final_sell_score'], index=range(len(subdirs)))

        df_fs = pd.DataFrame(columns=['Ticker', 'ols_1y_fit_score', 'ols_fit_score'], index=range(len(subdirs)))

        i = 0
        j = 0
        k = 0

        for subdir in subdirs:
            if not subdir.exists():
                print('\nError. ', subdir, ' not found')
            else:
                try:
                    f = open(subdir / 'signal.txt', 'r')
                    content = f.read()
                    matched_string = pattern_for_final_buy_score.search(content)
                    if (matched_string):
                        kw, val = matched_string.groups()
                        print(f'\n{kw} for {subdir.name}: {val}')
                        df_b['Ticker'][i] = f'{subdir.name}'
                        df_b['final_buy_score'][i] = float(val)
                        i += 1
                    else:
                        print(f'\n{kw} NOT found for {subdir}')

                    matched_string = pattern_for_final_sell_score.search(content)
                    if (matched_string):
                        kw, val = matched_string.groups()
                        print(f'\n{kw} for {subdir.name}: {val}')
                        df_s['Ticker'][j] = f'{subdir.name}'
                        df_s['final_sell_score'][j] = float(val)
                        j += 1
                    else:
                        print(f'\n{kw} NOT found for {subdir}')


                    matched_string = pattern_for_1y_ols_fit_score.search(content)
                    if (matched_string):
                        kw, val = matched_string.groups()
                        print(f'\n{kw} for {subdir.name}: {val}')
                        df_fs['Ticker'][k] = f'{subdir.name}'
                        df_fs['ols_1y_fit_score'][k] = float(val)
                    else:
                        print(f'\n{kw} NOT found for {subdir}')

                    matched_string = pattern_for_ols_fit_score.search(content)
                    if (matched_string):
                        kw, val = matched_string.groups()
                        print(f'\n{kw} for {subdir.name}: {val}')
                        df_fs['Ticker'][k] = f'{subdir.name}'
                        df_fs['ols_fit_score'][k] = float(val)
                    else:
                        print(f'\n{kw} NOT found for {subdir}')

                    k += 1
                    f.close()
                except:
                    print('\nError while getting stock signals for ', subdir.name, ': ', sys.exc_info()[0])

        df_b.sort_values('final_buy_score').dropna(how='all').to_csv(self.Tickers_dir / 'overall_buy_scores.csv', index=False)
        df_s.sort_values('final_sell_score').dropna(how='all').to_csv(self.Tickers_dir / 'overall_sell_scores.csv', index=False)

        #Regression fit scores Debug data
        df_fs.sort_values('Ticker').dropna(how='all').to_csv(self.Tickers_dir / 'overall_regression_fit_scores.csv', index=False)

    
