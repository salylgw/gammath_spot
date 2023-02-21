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

from pathlib import Path
import pandas as pd
from matplotlib import pyplot as plt
import os

try:
    from gammath_spot import gammath_utils as gut
    from gammath_spot import gammath_stocks_analysis as gsa
except:
    import gammath_utils as gut
    import gammath_stocks_analysis as gsa

def get_missing_gscores_count(df, gscores):

    mtdpy, mtd5y = gut.get_min_trading_days()
    df_len = len(df)
    gscores_len = len(gscores)
    missing_gscores_count = -1

    #Get last gscore date to search
    last_gscore_date = gscores.Date[gscores_len-1]

    bottom = (df_len-mtd5y-1)
    top = (df_len - 1)

    #Assuming history is not run that often so there might be a gap of many days
    #Using binary search on that premise to get O(logn)
    #Otherwise sequential search O(n) starting from end would be better (if history is run every week)
    while (bottom <= top):
        middle = (bottom + top)//2
        #Get df date at mid-index
        df_date = df.Date[middle].split(' ')[0]
        if (last_gscore_date == df_date):
            missing_gscores_count = (df_len - 1 - middle)
            break
        else:
            if (last_gscore_date > df_date):
                bottom = (middle + 1)
            else:
                top = (middle - 1)

    return missing_gscores_count

class GSH:

    def get_gscores_history(self, tsymbol):

        Tickers_dir = gut.get_tickers_dir()
        path = Tickers_dir / f'{tsymbol}'

        mtdpy, mtd5y = gut.get_min_trading_days()

        try:
            #Read Stock summary info into DataFrame
            df = pd.read_csv(path / f'{tsymbol}_history.csv', usecols=['Date', 'High', 'Low', 'Close', 'Volume'])
            df_len = len(df)
            df_last_date = df.Date[df_len-1].split(' ')[0]

            initial_end_index = df_len - mtd5y + 1
            initial_start_index = initial_end_index - mtd5y

            if (initial_start_index < 0):
                print('\nInsufficient stock history for symbol ', tsymbol)
                raise ValueError('Insufficient stock history')

            #Check if we have micro-gscores history for this stock
            gscores_history_exists = (path / f'{tsymbol}_micro_gscores.csv').exists()

            if (gscores_history_exists):
                df_gscores = pd.read_csv(path / f'{tsymbol}_micro_gscores.csv', index_col='Unnamed: 0')
                gscores_len = len(df_gscores)
                gscores_last_date = df_gscores.Date[gscores_len-1]
                #Get the missing count for gScores history
                missing_gscores_count = get_missing_gscores_count(df, df_gscores)

                if (missing_gscores_count != -1):
                    #Add one to get last gScore again; Doing this to avoid mismatch if previous run was done before the closing price for the day was established
                    missing_gscores_count += 1
                    initial_end_index = (df_len - missing_gscores_count + 1)
                    initial_start_index = (initial_end_index - mtd5y)
                    #Clip missing_gscores_count-gscores from start to make room for missing gscores near the end. Also, we want to redo last one as noted above
                    df_gscores = df_gscores.truncate(after=gscores_len-2).truncate(before=missing_gscores_count-1).reset_index().drop(columns='index')
                else:
                    missing_gscores_count = mtd5y
            else:
                missing_gscores_count = mtd5y

            #Use a different df starting index 0
            df1 = pd.DataFrame(columns=df.columns, index=range(mtd5y))

            #Get the columns for micro-gScores
            interim_df_gscores = pd.DataFrame(columns=gut.get_sh_gscores_df_columns(), index=range(missing_gscores_count))

            #Create a GSA instance
            gsa_instance = gsa.GSA()

            #Brute force (initial experiment; optimize later) for now to run through entire history
            for i in range(missing_gscores_count):
                df1.iloc[0:mtd5y] = df.iloc[initial_start_index+i:initial_end_index+i]
                interim_df_gscores.iloc[i], signals = gsa_instance.do_stock_history_analysis(tsymbol, path, df1, False)

            if (gscores_history_exists):
                df_gscores = pd.concat([df_gscores, interim_df_gscores], ignore_index=True)
            else:
                df_gscores = interim_df_gscores

            #Save gscores history
            df_gscores.to_csv(path / f'{tsymbol}_micro_gscores.csv')

            SH_GSCORE_MIN_DISCOUNT_LEVEL, SH_GSCORE_NEUTRAL_LEVEL, SH_GSCORE_MIN_PREMIUM_LEVEL = df_gscores.SH_gScore.quantile([0.20, 0.5, 0.80])

            #Draw the charts (along with dates) to get a general idea of correlations
            figure, axes = plt.subplots(nrows=11, figsize=(28, 47))

            #Get DPI for the figure
            charts_dpi = figure.get_dpi()

            #Get the width and height in pixels
            charts_pw = figure.get_figwidth() * charts_dpi
            charts_ph = figure.get_figheight() * charts_dpi

            logo_file_found = True

            try:
                #Get the path of the program/package
                pgm_dir_path, fn = os.path.split(__file__)

                #Append the data dir
                pgm_data_path = os.path.join(pgm_dir_path, 'data')

                #Read the logo
                logo_data = plt.imread(f'{pgm_data_path}/logo.png')
            except:
                logo_file_found = False

            closing_prices_df = pd.DataFrame({tsymbol: df_gscores.Close[0:mtd5y]})
            closing_prices_df = closing_prices_df.set_index(df_gscores.Date[0:mtd5y])
            closing_prices_df.plot(ax=axes[0],lw=1,title='Stock history')
            sh_gscores_df = pd.DataFrame({'SH_gscores': df_gscores.SH_gScore[0:mtd5y]})
            sh_gscores_df = sh_gscores_df.set_index(df_gscores.Date)
            sh_gscores_df.plot(ax=axes[1],lw=1,title='Stock History based gScores')
            axes[1].axhline(SH_GSCORE_MIN_DISCOUNT_LEVEL,lw=1,ls='-',c='r')
            axes[1].axhline(SH_GSCORE_NEUTRAL_LEVEL,lw=1,ls='-',c='r')
            axes[1].axhline(SH_GSCORE_MIN_PREMIUM_LEVEL,lw=1,ls='-',c='r')
            price_gscores_df = pd.DataFrame({'Price-micro-gScores': df_gscores.Price[0:mtd5y]})
            price_gscores_df = price_gscores_df.set_index(df_gscores.Date)
            price_gscores_df.plot(ax=axes[2],lw=1,title='Price micro-gScores')
            rsi_gscores_df = pd.DataFrame({'RSI-micro-gScores': df_gscores.RSI[0:mtd5y]})
            rsi_gscores_df = rsi_gscores_df.set_index(df_gscores.Date)
            rsi_gscores_df.plot(ax=axes[3],lw=1,title='RSI micro-gScores')
            bbands_gscores_df = pd.DataFrame({'BBANDS-micro-gScores': df_gscores.BBANDS[0:mtd5y]})
            bbands_gscores_df = bbands_gscores_df.set_index(df_gscores.Date)
            bbands_gscores_df.plot(ax=axes[4],lw=1,title='BBANDS micro-gScores')
            macd_gscores_df = pd.DataFrame({'MACD-micro-gScores': df_gscores.MACD[0:mtd5y]})
            macd_gscores_df = macd_gscores_df.set_index(df_gscores.Date)
            macd_gscores_df.plot(ax=axes[5],lw=1,title='MACD micro-gScores')
            kf_gscores_df = pd.DataFrame({'KF-micro-gScores': df_gscores.KF[0:mtd5y]})
            kf_gscores_df = kf_gscores_df.set_index(df_gscores.Date)
            kf_gscores_df.plot(ax=axes[6],lw=1,title='KF micro-gScores')
            ols_gscores_df = pd.DataFrame({'OLS-micro-gScores': df_gscores.OLS[0:mtd5y]})
            ols_gscores_df = ols_gscores_df.set_index(df_gscores.Date)
            ols_gscores_df.plot(ax=axes[7],lw=1,title='OLS micro-gScores')
            mfi_gscores_df = pd.DataFrame({'MFI-micro-gScores': df_gscores.MFI[0:mtd5y]})
            mfi_gscores_df = mfi_gscores_df.set_index(df_gscores.Date)
            mfi_gscores_df.plot(ax=axes[8],lw=1,title='MFI micro-gScores')
            stoch_gscores_df = pd.DataFrame({'Stoch-micro-gScores': df_gscores.Stoch[0:mtd5y]})
            stoch_gscores_df = stoch_gscores_df.set_index(df_gscores.Date)
            stoch_gscores_df.plot(ax=axes[9],lw=1,title='Stoch micro-gScores')
            nup_gscores_df = pd.DataFrame({'NU-Prob': df_gscores.NUP[0:mtd5y]})
            nup_gscores_df = nup_gscores_df.set_index(df_gscores.Date)
            nup_gscores_df.plot(ax=axes[10],lw=1,title='Next day UP Probability')

            if (logo_file_found):
                #Attach logo to the figure
                plt.figimage(logo_data, xo=charts_pw/2, yo=(charts_ph-100))

            #Save figure for later reference
            #Use PDF instead of png to save space
            plt.savefig(path / f'{tsymbol}_gscores_charts.pdf', format='pdf')
            plt.close(fig=None)
            return df_gscores
        except:
            print('\nERROR: gScores history failed for symbol ', tsymbol)
            return pd.DataFrame()

    def save_gscores_history(self, tsymbol):
        self.get_gscores_history(tsymbol)

