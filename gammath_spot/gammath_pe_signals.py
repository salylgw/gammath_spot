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

from pathlib import Path
import pandas as pd
import numpy as np


def get_pe_signals(tsymbol, df_summ, path):

    pe_gscore = 0
    pe_max_score = 2

    try:
        if (path / 'SP500_SEC_PES.csv').exists():
            df_sp = pd.read_csv(path / 'SP500_SEC_PES.csv')
    except:
        raise ValueError('No PE reference file')

    tpe = 0
    fpe = 0

    try:
        tpe = df_summ['trailingPE'][0]
        if (np.isnan(tpe)):
            tpe_string = 'No TPE data'
        else:
            tpe = round(tpe, 3)
            tpe_string = f'{tpe}'
    except:
        tpe_string = 'No TPE data'

    try:
        fpe = df_summ['forwardPE'][0]
        if (np.isnan(fpe)):
            fpe_string = 'No FPE data'
        else:
            fpe = round(fpe, 3)
            fpe_string = f'{fpe}'
    except:
        fpe_string = 'No FPE data'


    # For now just check if FPE is less or more than TPE
    # If forward PE is less than trailing PE then view this as a +ve sign
    if ((fpe > 0) and (tpe > 0)):
        if (fpe < tpe):
            pe_gscore += 2
        else:
            pe_gscore -= 2
    else:
        pe_gscore -= 2


    avg_tpe = 0
    avg_fpe = 0

    len_df_sp = len(df_sp)

    for i in range(len_df_sp):
        if (df_sp['Symbol'][i] == tsymbol):
            try:
                avg_tpe = df_sp['LS_AVG_TPE'][i]
                if (np.isnan(avg_tpe)):
                    avg_tpe_string = 'No Avg TPE data'
                else:
                    avg_tpe = round(avg_tpe, 3)
                    avg_tpe_string = f'{avg_tpe}'
            except:
                avg_tpe_string = 'No Avg TPE data'

            try:
                avg_fpe = df_sp['LS_AVG_FPE'][i]
                if (np.isnan(avg_fpe)):
                    avg_fpe_string = 'No Avg FPE data'
                else:
                    avg_fpe = round(avg_fpe, 3)
                    avg_fpe_string = f'{avg_fpe}'
            except:
                avg_fpe_string = 'No Avg FPE data'

            # Avg TPE and Avg FPE data needs to be authentic before we can factor it into score computation.
            # Currently, this avg is based on very limited data and also does not include sub-sectors
            # For now just use this for logging for later manual and rough comparison
            break

    if (i == (len_df_sp-1)):
        avg_tpe_string = 'No Avg TPE data'
        avg_fpe_string = 'No Avg FPE data'


    pe_grec = f'pe_gscore:{pe_gscore}/{pe_max_score}'

    pe_signals = f'PE: TPE:{tpe_string},ATPE:{avg_tpe_string},FPE:{fpe_string},AFPE:{avg_fpe_string},{pe_grec}'

    return pe_gscore, pe_max_score, pe_signals
