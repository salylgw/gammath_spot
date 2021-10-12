# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd

buy_recos = ('Above Average', 'Accumulate', 'Add', 'Buy', 'Conviction Buy', 'Gradually Accumulate', 'Long-Term Buy', 'Long-term Buy', 'Market Outperform', 'Outperform', 'Outperformer', 'Overweight', 'Positive', 'Sector Outperform', 'Strong Buy', 'Top Pick')

def get_reco_signals(tsymbol, path):

    print('\nGetting recommendations signals')

    reco_buy_score = 0
    reco_sell_score = 0
    reco_max_score = 0

    file_exists = (path / f'{tsymbol}_reco.csv').exists()

    #Check if file exists and is it from another day
    if file_exists:
        print(f'\nRecommendations for {tsymbol} exists')
        df = pd.read_csv(path / f'{tsymbol}_reco.csv')
        len_df = len(df)
        if (len_df == 0):
            print(f'\nERROR: Recommendations dataframe is empty for {tsymbol}')
        else:
            print(f'\nRead recommendations into dataframe for {tsymbol}')
            #Get shorter of last 10% of recommendations from entire list
            df_10p = len_df - int(len_df * 10 / 100)
            if (df_10p < len_df):
                start_index = df_10p
            else:
                start_index = 0

            shorter_df = df[start_index:len_df]

            buy_count = 0
            sell_coumt = 0

            for grade in shorter_df['To Grade']:
                if (grade in buy_recos):
                    buy_count += 1
                else:
                    sell_coumt += 1

            total_recos = len(shorter_df)

            buy_percentage = buy_count*100/total_recos

            if (buy_percentage > 50):
                reco_buy_score += 3
                reco_sell_score -= 3
            else:
                reco_buy_score -= 6
                reco_sell_score += 6

            if (buy_percentage > 75):
                reco_buy_score += 3
                reco_sell_score -= 3

            reco_max_score += 6

            print(f'\nRecommendations score based on current grade done for {tsymbol}')

            up_count = 0
            down_count = 0
            for action in shorter_df['Action']:
                if (action == 'up'):
                    up_count += 1
                elif (action == 'down'):
                    down_count += 1

            print(f'\nUpgrades: {up_count}, Downgrades: {down_count} for {tsymbol}')

            if (up_count > down_count):
                reco_buy_score += 6
                reco_sell_score -= 6
            else:
                reco_buy_score -= 6
                reco_sell_score += 6

            reco_max_score += 6
    else:
        print(f'\nERROR: Quarterly recommendation sheet for {tsymbol} does NOT exist. Need to fetch it')

    reco_buy_rec = f'reco_buy_score:{reco_buy_score}/{reco_max_score}'
    reco_sell_rec = f'reco_sell_score:{reco_sell_score}/{reco_max_score}'

    reco_signals = f'reco:{reco_buy_rec},{reco_sell_rec}'

    print(f'\nRecommendation signals extracted for {tsymbol}')
    return reco_buy_score, reco_sell_score, reco_max_score, reco_signals
