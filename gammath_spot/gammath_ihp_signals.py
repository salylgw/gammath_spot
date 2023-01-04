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

#Get percentage held by institutions for tsymbol
def get_ihp_signals(tsymbol, df_summ):

    ihp_gscore = 0
    ihp_max_score = 0

    try:
        #Get data about percentage held from summary dataframe
        ihp = df_summ['heldPercentInstitutions'][0]
    except:
        raise ValueError('heldPercentInstitutions value not found')

    #We can do checks for different levels but for now this will suffice
    if (ihp > 0):
        if (ihp > 0.7):
            ihp_gscore += 1
        else:
            ihp_gscore -= 1

    ihp_max_score += 1

    #Round it off to take less space when displaying
    ihp = round(ihp, 3)

    #At some point, we can add percent change. Right now requires to be checked using local old val with new val; REVISIT

    ihp_grec = f'ihp_gscore:{ihp_gscore}/{ihp_max_score}'

    ihp_signals = f'IHP:{ihp},{ihp_grec}'

    return ihp_gscore, ihp_max_score, ihp_signals
