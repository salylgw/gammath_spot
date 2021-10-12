# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd
import os

def get_events_info(tsymbol, path):

    print(f'\nGetting events info for {tsymbol}')

    event = ''
    event_dates = []

    #Get the events data from existing file
    if ((path / f'{tsymbol}_calendar.csv').exists()):
        print(f'\nReading events for {tsymbol}')

        #Get the latest options expiry date
        df = pd.read_csv(path / f'{tsymbol}_calendar.csv', index_col='Unnamed: 0')

        num_rows = len(df.index)
        if (num_rows == 0):
            print(f'\nThere are no events reported for {tsymbol}')
        else:
            num_cols = len(df.columns)
            if (num_cols == 0):
                print(f'\nThere is no data associated with event for {tsymbol}')
            else:
                #For now only use Earnings event (happens to be the first event in the calendar)
                event = df.index[0]

                #Extract all event dates
                for i in range(num_cols):
                    event_dates.append(df[df.columns[i]][event])

    events_info = f'{event}: {event_dates}'
    
    return events_info

