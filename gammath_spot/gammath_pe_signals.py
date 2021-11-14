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

from pathlib import Path
import pandas as pd


def get_pe_signals(tsymbol, df_summ):

    Tickers_dir = Path('./tickers')

    path = Tickers_dir
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    pe_gscore = 0
    pe_max_score = 0

    if (path / 'SP500_SEC_PES.csv').exists():
        df_sp = pd.read_csv(path / 'SP500_SEC_PES.csv')

    try:
        tpe = round(df_summ['trailingPE'][0], 3)
        fpe = round(df_summ['forwardPE'][0], 3)
    except:
        raise ValueError('PE values not found')

    avg_tpe = 0
    avg_fpe = 0

    len_df_sp = len(df_sp)

    for i in range(len_df_sp):
        if (df_sp['Symbol'][i] == tsymbol):
            avg_tpe = round(df_sp['LS_AVG_TPE'][i], 3)
            avg_fpe = round(df_sp['LS_AVG_FPE'][i], 3)

            #Avg TPE and FPE data needs to be authentic before we can factor it into score computation. For now just check if FPE is less or more than TPE
            #If forward PE is less than trailing PE then view this as a +ve sign
            if ((fpe > 0) and (tpe > 0)):
                if (fpe < tpe):
                    pe_gscore += 2
                else:
                    pe_gscore -= 2
            else:
                pe_gscore -= 2

            pe_max_score += 2

            break

    if (i == (len_df_sp-1)):
        pe_gscore = 0

        #No data viewed as a -ve so have an impact on total score
        pe_max_score = 2

    pe_grec = f'pe_gscore:{pe_gscore}/{pe_max_score}'

    pe_signals = f'PE: TPE:{tpe},ATPE:{avg_tpe},FPE:{fpe},AFPE:{avg_fpe},{pe_grec}'

    return pe_gscore, pe_max_score, pe_signals
