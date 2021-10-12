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

    df_pbr = pd.DataFrame(columns=['Ticker', 'PBR'], index=range(len(subdirs)))

    i = 0

    for subdir in subdirs:
        if not subdir.exists():
            print('\nError. ', subdir, ' not found')
        else:
            try:
                path_check = subdir / f'{subdir.name}_summary.csv'
                print(path_check)
                sti = pd.read_csv(subdir / f'{subdir.name}_summary.csv')
                pbr = sti['priceToBook'][0]
                df_pbr['Ticker'][i] = f'{subdir.name}'
                df_pbr['PBR'][i] = int(pbr)
                print(f'{subdir.name}: {pbr}')
                i += 1
            except:
                print('\nError while getting PBR value for ', subdir.name, ': ', sys.exc_info()[0])

    df_pbr.sort_values('PBR').to_csv(Tickers_dir / 'sorted_PBRs.csv', index=False)
