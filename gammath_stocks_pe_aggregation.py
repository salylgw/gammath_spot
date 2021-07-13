# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd
import sys

if __name__ == '__main__':

    Tickers_dir = Path('tickers')

    df_sp = pd.read_csv('SP500_US_ONLY_WITH_PE.csv')
    #Get all the subdirs. Need to check for is_dir
    p = Path('tickers')
    
    #Somehow looks like os.is_dir isn't supported
    #Using pathlib/Path instead since is_dir is supported there
    subdirs = [x for x in p.iterdir() if x.is_dir()]
    subdirs_len = len(subdirs)
    print('\nNum of subdirs: ', subdirs_len)

    i = 0
    j = 0

    for subdir in subdirs:
        if not subdir.exists():
            print('\nError. ', subdir, ' not found')
        else:
            try:
                df = pd.read_csv(subdir / f'{subdir.name}_summary.csv')
                tpe = df['trailingPE'][0]
                fpe = df['forwardPE'][0]
                for i in range(subdirs_len):
                    if (df_sp['Symbol'][i] == subdir.name):
                        break
                
                if (i == subdirs_len):
                    print('ERROR: Symbol not found in CSV')
                else:
                    df_sp['TPE'][i] = tpe
                    df_sp['FPE'][i] = fpe
            except:
                print('\nError while getting stock PE values for ', subdir.name, ': ', sys.exc_info()[0])

    df_sp.to_csv(p / 'seg_pes.csv')


