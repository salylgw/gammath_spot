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

def get_inshp_signals(tsymbol, df_summ):

    inshp_gscore = 0
    inshp_max_score = 0

    try:
        inshp = df_summ['heldPercentInsiders'][0]
    except:
        raise ValueError('heldPercentInsiders not found')

    if (inshp > 0):
        inshp_gscore += 1
    else:
        inshp_gscore -= 1

    inshp_max_score += 1

    #Round it off to take less space displaying the value
    inshp = round(inshp, 3)

    #At some point, we can add percent change. Right now requires to be checked using local old val with new val; REVISIT

    inshp_grec = f'inshp_gscore:{inshp_gscore}/{inshp_max_score}'

    inshp_signals = f'inshp:{inshp},{inshp_grec}'

    return inshp_gscore, inshp_max_score, inshp_signals
