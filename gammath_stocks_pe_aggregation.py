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

    p = Path('.')

#    df = pd.read_csv(p / 'SP500_US_ONLY.csv')
    df = pd.read_csv(p / 'SP500_list.csv')

    #Need to calculate sector-average so rearrange
    df_sp = df.sort_values('GICS Sector')

    df_sp_len = len(df_sp)

    df_pe = pd.DataFrame(columns=['TPE', 'FPE', 'LS_AVG_TPE', 'LS_AVG_FPE'], index=range(df_sp_len))

    p = Path('tickers')

    i = 0
    symbols = list(df_sp['Symbol'])

    for symbol in symbols:
        try:
            df_summ = pd.read_csv(p / f'{symbol}/{symbol}_summary.csv')
            tpe = df_summ['trailingPE'][0]
            fpe = df_summ['forwardPE'][0]

            #df_sp Symbols are arranged based on sectors so same order will be in df_pe
            df_pe['TPE'][i] = tpe
            df_pe['FPE'][i] = fpe
                
        except:
            print('\nError while getting stock PE values for ', symbol, ': ', sys.exc_info()[0])
            df_pe['TPE'][i] = 0
            df_pe['FPE'][i] = 0

        i += 1

    #Extract the sectors
#    df_sp = pd.read_csv(p / 'SP500_US_ONLY_SEC_PES.csv')
#    df_sp = pd.read_csv(p / 'SP500_SEC_PES.csv')
    print('DataFrame length: ', df_sp_len)

    #Extract unique sectors
    sectors = df_sp['GICS Sector'].drop_duplicates()
    print('\nSectors: ', sectors)
    sector_list = []

    #Calculate average and save for each sector; also save sectors
    i = 0
    new_tpe = 0
    new_fpe = 0

    sector_fields = list(df_sp['GICS Sector'])
    len_sector_fields = len(sector_fields)
    print('\nSector fields list size: ', len_sector_fields)
    tpes = list(df_pe['TPE'])
    fpes = list(df_pe['FPE'])

    for sector in sectors:
        sector_list.append(sector)
        curr_sector_tpe = 0
        curr_sector_tpe_count = 0
        curr_sector_fpe = 0
        curr_sector_fpe_count = 0
        start_index = i
        print('Sector field: ', sector_fields[i], 'Sector: ', sector)
        while (sector_fields[i] == sector):
            new_tpe = tpes[i]
            new_fpe = fpes[i]
            i += 1

            if (new_tpe > 0):
                curr_sector_tpe_count += 1
                curr_sector_tpe += new_tpe

            if (new_fpe > 0):
                curr_sector_fpe_count += 1
                curr_sector_fpe += new_fpe

            if (i == len_sector_fields):
                break

        end_index = i
        curr_sector_tpe_avg = 0
        curr_sector_fpe_avg = 0

        if (curr_sector_tpe_count):
            curr_sector_tpe_avg = curr_sector_tpe / curr_sector_tpe_count
            print('TPE AVG: ', curr_sector_tpe_avg, 'start_index: ', start_index, 'end_index: ', end_index)

        if (curr_sector_fpe_count):
            curr_sector_fpe_avg = curr_sector_fpe / curr_sector_fpe_count
            print('FPE AVG: ', curr_sector_fpe_avg, 'start_index: ', start_index, 'end_index: ', end_index)

        print(f'start index: {start_index}, end index: {end_index}')

        #Save average values at all indices for this sector
        df_pe['LS_AVG_TPE'][start_index:end_index] = curr_sector_tpe_avg
        df_pe['LS_AVG_FPE'][start_index:end_index] = curr_sector_fpe_avg

    print(df_pe)
    print(f'\nSector list: {sector_list}')

    #New data frame with columns from PE dataframe joined
    df_sp = df_sp.join(df_pe)
    #Drop unwanted fields
    df_sp = df_sp.dropna(0, how='all').drop('Unnamed: 0', axis=1)

#    df_sp.to_csv(p / 'SP500_US_ONLY_SEC_PES.csv', index=False)

    #Rearrange based on ticker symbol
    df_sp = df_sp.sort_values('Symbol')
#    df_sp.to_csv(p / 'SP500_US_ONLY_SEC_PES.csv', index=False)
#    df_sp.to_csv(p / 'SP500_SEC_PES.csv', index=False)

    p = Path('.')
#    df_sp.to_csv(p / 'SP500_US_ONLY_SEC_PES.csv', index=False)

    #Save for later reference and processing
    df_sp.to_csv(p / 'SP500_SEC_PES.csv', index=False)
