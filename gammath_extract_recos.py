# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import sys
from pathlib import Path
import pandas as pd

if __name__ == '__main__':
    Tickers_dir = Path('tickers')

    #Get all the subdirs. Need to check for is_dir
    p = Path('tickers')
    
    #Somehow looks like os.is_dir isn't supported
    #Using pathlib/Path instead since is_dir is supported there
    subdirs = [x for x in p.iterdir() if x.is_dir()]

    print('\nNum of subdirs: ', len(subdirs))

    df_recos = pd.DataFrame(columns=['To Grade'], index=range(2000))

    for subdir in subdirs:
        if not subdir.exists():
            print('\nError. ', subdir, ' not found')
        else:
            try:
                path_check = subdir / f'{subdir.name}_reco.csv'
                print(path_check)
                df = pd.read_csv(subdir / f'{subdir.name}_reco.csv')
                df = df['To Grade'].sort_values().drop_duplicates().dropna()
                df.to_csv(subdir / 'recos_list.csv', index=False)
            except:
                print('\nError while getting Reco value for ', subdir.name, ': ', sys.exc_info()[0])

    for subdir in subdirs:
        if not subdir.exists():
            print('\nError. ', subdir, ' not found')
        else:
            try:
                path_check = subdir / 'recos_list.csv'
                print(path_check)
                df = pd.read_csv(subdir / 'recos_list.csv')
                df_recos = df_recos.append(df).dropna()
            except:
                print('\nError while getting Reco value for ', subdir.name, ': ', sys.exc_info()[0])

    df_recos['To Grade'].sort_values().drop_duplicates().dropna().to_csv('recos_strings.csv', index=False)
