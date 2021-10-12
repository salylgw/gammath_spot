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

    print(f'\nGetting signals out of Analysts recommendation for {tsymbol}')

    reco_buy_score = 0
    reco_sell_score = 0
    reco_max_score = 0

    file_exists = (path / f'{tsymbol}_reco.csv').exists()

    #Check if file exists and is it from another day
    if file_exists:
        print(f'\nAnalysts recommendations for {tsymbol} exists')
        df = pd.read_csv(path / f'{tsymbol}_reco.csv')
        len_df = len(df)
        if (len_df == 0):
            print(f'\nERROR: Analysts recommendations dataframe is empty for {tsymbol}')
        else:
            print(f'\nRead Analysts recommendations into dataframe for {tsymbol}')
            #We only want recent data so get shorter of last 20% of recommendations from entire list
            df_20p_index = len_df - int((len_df * 20) / 100)
            if (df_20p_index < len_df):
                start_index = df_20p_index
            else:
                start_index = 0

            #Shorter list for recent recommendations
            shorter_df = df[start_index:len_df]

            total_recos = len(shorter_df)

            buy_count = 0
            sell_count = 0

            #Extract count for buy/sell/positive recommendations
            for grade in shorter_df['To Grade']:
                if (grade in buy_recos):
                    buy_count += 1
                else:
                    sell_count += 1


            #Get the percentage of +ve recommendations
            buy_percentage = buy_count*100/total_recos
            print(f'\nBuy count: {buy_count}, Sell count: {sell_count} for {tsymbol}. buy pct: {buy_percentage}')

            #Reduce buy score and increase sell score
            if (buy_percentage < 50):
                reco_buy_score -= 10
                reco_sell_score += 10
            else:
                reco_buy_score += 5
                reco_sell_score -= 5

                if (buy_percentage > 75):
                    reco_buy_score += 5
                    reco_sell_score -= 5

            reco_max_score += 10

            #Extract count for recent upgrades/downgrades recommendations
            up_count = 0
            down_count = 0
            for action in shorter_df['Action']:
                if (action == 'up'):
                    up_count += 1
                elif (action == 'down'):
                    down_count += 1

            #Get the percentage of +ve recommendations
            up_percentage = (up_count*100)/(up_count + down_count)

            print(f'\nUpgrades: {up_count}, Downgrades: {down_count} for {tsymbol}. up pct: {up_percentage}')

            #Reduce buy score and increase sell score
            if (up_percentage < 50):
                reco_buy_score -= 10
                reco_sell_score += 10
            else:
                reco_buy_score += 5
                reco_sell_score -= 5

                if (up_percentage > 75):
                    reco_buy_score += 5
                    reco_sell_score -= 5

            reco_max_score += 10
    else:
        print(f'\nERROR: Quarterly recommendation sheet for {tsymbol} does NOT exist. Need to fetch it')

    reco_buy_rec = f'reco_buy_score:{reco_buy_score}/{reco_max_score}'
    reco_sell_rec = f'reco_sell_score:{reco_sell_score}/{reco_max_score}'

    reco_signals = f'reco:{reco_buy_rec},{reco_sell_rec}'

    print(f'\nRecommendation signals extracted for {tsymbol}')
    return reco_buy_score, reco_sell_score, reco_max_score, reco_signals
