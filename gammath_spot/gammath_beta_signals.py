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

def get_beta_signals(tsymbol, df_summ):

    beta_gscore = 0
    beta_max_score = 0

    try:
        #Get the beta value from summary DF
        beta = df_summ['beta'][0]
    except:
        raise ValueError('Beta value not found')

    if (beta > 0):
        #Closer to 1 is near market and is better
        if (beta < 2):
            beta_gscore += 1
        else:
            beta_gscore -= 1

    beta_max_score += 1

    #round it off for taking less space when displaying
    beta = round(beta, 3)

    beta_grec = f'beta_gscore:{beta_gscore}/{beta_max_score}'

    beta_signals = f'BETA:{beta},{beta_grec}'

    return beta_gscore, beta_max_score, beta_signals
