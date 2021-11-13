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
import sys

def compute_final_score_and_save_signals(tsymbol, path, overall_dip_score, overall_max_score, overall_signals):

    overall_dip_rec = f'overall_dip_score:{overall_dip_score}/{overall_max_score}'

    if (overall_max_score != 0):
        final_dip_score = round((int(overall_dip_score)/int(overall_max_score)), 5)
    else:
        final_dip_score = 0

    final_dip_score_rec = f'final_dip_score:{final_dip_score}'

    try:
        f = open(path / 'signal.txt', 'w')
    except:
        print('\nERROR: opening signal file for ', tsymbol, ': ', sys.exc_info()[0])
    else:
        f.write(f'{overall_signals}\n{overall_dip_rec}\n{final_dip_score_rec}\n')
        f.close()
