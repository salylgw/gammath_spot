# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
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
