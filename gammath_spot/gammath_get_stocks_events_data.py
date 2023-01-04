# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works
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
__copyright__ = 'Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import pandas as pd
import os

def get_events_info(tsymbol, path):

    event = 'No events found'
    event_dates = []

    #Get the events data from existing file
    if ((path / f'{tsymbol}_calendar.csv').exists()):

        #Get the latest options expiry date
        df = pd.read_csv(path / f'{tsymbol}_calendar.csv', index_col='Unnamed: 0')

        num_rows = len(df.index)
        if (num_rows != 0):
            num_cols = len(df.columns)
            if (num_cols != 0):
                #For now only use Earnings event (happens to be the first event in the calendar)
                event = df.index[0]

                #Extract all event dates
                for i in range(num_cols):
                    event_dates.append(df[df.columns[i]][event])
    else:
        print(f'\nINFO: Events file for {tsymbol} not found')

    events_info = f'{event}: {event_dates}'

    return events_info

