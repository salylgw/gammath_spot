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

import pandas as pd
import numpy as np

def get_pbr_signals(tsymbol, df_summ):

    pbr_gscore = 0
    pbr_max_score = 0

    try:
        if (len(df_summ) > 0):
            try:
                pbr = df_summ['priceToBook'][0]
                if (np.isnan(pbr)):
                    PBR_string = 'No PBR data'
                else:
                    pbr = round(pbr, 3)
                    PBR_string = f'{pbr}'
                    if (pbr > 0):

                        #Lower PBR is better; Not giving more weight as we have analyst reco and other factors accouting for "selection" criteria
                        if (pbr < 20):
                            pbr_gscore += 1
                        else:
                            pbr_gscore -= 1
            except:
                raise ValueError('PBR not found')

        else:
            raise RuntimeError('Dataframe empty')

    except:
        pbr = 0
        PBR_string = 'No PBR data'

    pbr_max_score += 1

    pbr_grec = f'pbr_gscore:{pbr_gscore}/{pbr_max_score}'

    pbr_signals = f'PBR:{PBR_string},{pbr_grec}'

    return pbr_gscore, pbr_max_score, pbr_signals
