# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import sys

def score_n_signals_save(tsymbol, path, overall_buy_score, overall_sell_score, overall_max_score, overall_signals):

    print(f'\nComputing final score saving signals for {tsymbol}')

    overall_buy_rec = f'overall_buy_score:{overall_buy_score}/{overall_max_score}'
    overall_sell_rec = f'overall_sell_score:{overall_sell_score}/{overall_max_score}'

    if (overall_max_score != 0):
        final_buy_score = round((int(overall_buy_score)/int(overall_max_score)), 5)
        final_sell_score = round((int(overall_sell_score)/int(overall_max_score)), 5)
    else:
        final_buy_score = 0
        final_sell_score = 0

    final_buy_score_rec = f'final_buy_score:{final_buy_score}'
    final_sell_score_rec = f'final_sell_score:{final_sell_score}'

    try:
        f = open(path / 'signal.txt', 'w')
    except:
        print('\nError while opening signal file for ', tsymbol, ': ', sys.exc_info()[0])
    else:
        f.write(f'{overall_signals}\n{overall_buy_rec}\n{overall_sell_rec}\n{final_buy_score_rec}\n{final_sell_score_rec}')
        f.close()
