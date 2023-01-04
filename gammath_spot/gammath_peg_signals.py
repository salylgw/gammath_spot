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

import pandas as pd
import numpy as np

def get_peg_signals(tsymbol, df_summ):

    peg_gscore = 0
    peg_max_score = 0

    try:
        peg = round(df_summ['pegRatio'][0], 3)
        if (np.isnan(peg)):
            peg_string = 'No PEG data'
        else:
            peg_string = f'{peg}'
            if (peg > 0):
                if (peg < 3):
                    peg_gscore += 1
            else:
                peg_gscore -= 1
    except:
        peg_string = 'No PEG data'


    peg_max_score += 1

    peg_grec = f'peg_gscore:{peg_gscore}/{peg_max_score}'

    peg_signals = f'PEG:{peg_string},{peg_grec}'

    return peg_gscore, peg_max_score, peg_signals
