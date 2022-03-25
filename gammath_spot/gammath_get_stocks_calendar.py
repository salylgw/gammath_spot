# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2022, Salyl Bhagwat, Gammath Works
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
__copyright__ = 'Copyright (c) 2021-2022, Salyl Bhagwat, Gammath Works'

import yfinance as yf
from pathlib import Path
import pandas as pd
import time
import os
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

def get_ticker_calendar(tsymbol, ticker, path):

    if (len(tsymbol) == 0):
        raise ValueError('Invalid symbol')

    calendar_dont_need_fetch = True

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    try:
        file_exists = (path / f'{tsymbol}_calendar.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_calendar.csv')
            calendar_dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            calendar_dont_need_fetch = False
    except:
        raise RuntimeError('Error calendar data file')

    if not calendar_dont_need_fetch:
        try:
            stock_calendar_sheet = ticker.calendar
            if (len(stock_calendar_sheet) > 0):
                #Save the data for reference and processing
                stock_calendar_sheet.to_csv(path / f'{tsymbol}_calendar.csv')
        except:
            raise RuntimeError('Error getting calendar data')


    return
