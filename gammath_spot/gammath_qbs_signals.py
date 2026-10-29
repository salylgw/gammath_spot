# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-Present, Salyl Bhagwat, Gammath Works
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
__copyright__ = 'Copyright (c) 2021-Present, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd
import numpy as np

def get_qbs_signals(tsymbol, path, df_summ):

    qbs_gscore = 0
    qbs_max_score = 0
    cr_string = ''
    qr_string = ''

    cr = 0
    qr = 0

    #Check for current ratio for debt obligation readiness
    try:
        cr = df_summ['currentRatio'][0]
        if (np.isnan(cr)):
            cr_string = 'No current ratio data'
        else:
            cr = round(cr, 3)
            cr_string = f'{cr}'

            #Check if current ratio is >= 1
            if (cr >= 1):
                qbs_gscore += 1
            else:
                qbs_gscore -= 1
    except:
        cr_string = 'No current ratio data'

    qbs_max_score += 1

    #Check for quick ratio for debt obligation ease
    try:
        qr = df_summ['quickRatio'][0]
        if (np.isnan(qr)):
            qr_string = 'No quick ratio data'
        else:
            qr = round(qr, 3)
            qr_string = f'{qr}'
            #Check if quick ratio >= 1
            if (qr >= 1):
                qbs_gscore += 1
            else:
                qbs_gscore -= 1
    except:
        qr_string = 'No quick ratio data'

    qbs_max_score += 1

    qbs_grec = f'qbs_gscore:{qbs_gscore}/{qbs_max_score}'

    qbs_signals = f'qbs:cr:{cr_string},qr:{qr_string},{qbs_grec}'

    return qbs_gscore, qbs_max_score, qbs_signals
