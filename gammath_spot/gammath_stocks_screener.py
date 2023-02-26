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

#Stock screener based on micro-gScores
import sys
from pathlib import Path
import pandas as pd
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

def main():

    try:
        #Get the screening file for buy-criteria from pgm argument
        sf_name = sys.argv[1]
        df_gscores_screening = pd.read_csv(sf_name)

        #extract values for screening
        min_price_micro_gscore = df_gscores_screening.Price[0]
        min_rsi_micro_gscore = df_gscores_screening.RSI[0]
        min_bbands_micro_gscore = df_gscores_screening.BBANDS[0]
        min_macd_micro_gscore = df_gscores_screening.MACD[0]
        min_kf_micro_gscore = df_gscores_screening.KF[0]
        min_ols_micro_gscore = df_gscores_screening.OLS[0]
        min_mfi_micro_gscore = df_gscores_screening.MFI[0]
        min_stoch_micro_gscore = df_gscores_screening.Stoch[0]
        min_options_micro_gscore = df_gscores_screening.Options[0]
        min_reco_micro_gscore = df_gscores_screening.Reco[0]
        min_senti_micro_gscore = df_gscores_screening.Senti[0]
    except:
        print('INFO: No screening info provided. Using default values')

        #Get all; no filtering
        min_price_micro_gscore = -1
        min_rsi_micro_gscore = -1
        min_bbands_micro_gscore = -1
        min_macd_micro_gscore = -1
        min_kf_micro_gscore = -1
        min_ols_micro_gscore = -1
        min_mfi_micro_gscore = -1
        min_stoch_micro_gscore = -1
        min_options_micro_gscore = -1
        min_reco_micro_gscore = -1
        min_senti_micro_gscore = -1


    #Traverse through all sub-dirs
    p = gut.get_tickers_dir()
    subdirs = [x for x in p.iterdir() if x.is_dir()]

    df_list = pd.DataFrame(columns=['Symbol'], index=range(len(subdirs)))

    count = 0
    for subdir in subdirs:
        if subdir.exists():
            try:
                df_gscores = pd.read_csv(subdir / f'{subdir.name}_gscores.csv', index_col='Unnamed: 0')

                #Extract symbols that match screening criteria
                if ((df_gscores.Price[0] >= min_price_micro_gscore) and
                    (df_gscores.RSI[0] >= min_rsi_micro_gscore) and
                    (df_gscores.BBANDS[0] >= min_bbands_micro_gscore) and
                    (df_gscores.MACD[0] >= min_macd_micro_gscore) and
                    (df_gscores.KF[0] >= min_kf_micro_gscore) and
                    (df_gscores.OLS[0] >= min_ols_micro_gscore) and
                    (df_gscores.MFI[0] >= min_mfi_micro_gscore) and
                    (df_gscores.Stoch[0] >= min_stoch_micro_gscore) and
                    (df_gscores.Options[0] >= min_options_micro_gscore) and
                    (df_gscores.Reco[0] >= min_reco_micro_gscore) and
                    (df_gscores.Senti[0] >= min_senti_micro_gscore)):

                    df_list['Symbol'][count] = f'{subdir.name}'
                    count += 1
            except:
                continue

    df_list = df_list.truncate(after=(count-1))
    df_list.to_csv(p / 'screened_list.csv')

if __name__ == '__main__':
    main()
