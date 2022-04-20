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
import sys
import time
import os
try:
    from gammath_spot import gammath_get_stocks_summary as gss
    from gammath_spot import gammath_get_stocks_financials as gsf
    from gammath_spot import gammath_get_stocks_history as gsh
    from gammath_spot import gammath_get_stocks_options_data as gso
    from gammath_spot import gammath_get_stcktwts as ggstw
    from gammath_spot import gammath_get_stocks_calendar as gsc
except:
    import gammath_get_stocks_summary as gss
    import gammath_get_stocks_financials as gsf
    import gammath_get_stocks_history as gsh
    import gammath_get_stocks_options_data as gso
    import gammath_get_stcktwts as ggstw
    import gammath_get_stocks_calendar as gsc

class GSD:
    def __init__(self):
        self.Tickers_dir = Path('tickers')

    def get_stocks_data(self, tsymbol):

        #Get data for stock ticker symbol from the internet

        if (len(tsymbol) == 0):
            raise ValueError('Invalid ticker symbol')

        path = self.Tickers_dir / f'{tsymbol}'

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        try:
            #Fetch stocktwits page; Finish getting all data outside of yahoo
            ggstw.get_stocktwits_ticker_info(tsymbol, path)
        except:
            print(f'\nERROR: Failed to get Stocktwits info for {tsymbol}')

        try:
            #Create Yahoo finance ticker handle
            ticker = yf.Ticker(tsymbol)
        except:
            print(f'\nERROR: Failed to create Yahoo ticker handle for {tsymbol}')
            raise RuntimeError('Failed to create Yahoo ticker handle')

        try:
            #Get stock info
            gss.get_ticker_summary(tsymbol, ticker, path)

        except ValueError:
            print(f'Error while getting stock summary for {tsymbol}')

        try:
            #Get stock financials
            gsf.get_ticker_financials(tsymbol, ticker, path)
        except ValueError:
            print(f'Error while getting stock financial data for {tsymbol}')

        try:
            #Get stock options data [NOTE: This is very slow]
            gso.get_options_data(tsymbol, ticker, path)
        except ValueError:
            print(f'Error while getting stock options data for {tsymbol}')
        except RuntimeError:
            print(f'Could not get stock options data for {tsymbol}')

        try:
            #Get calendar info [NOTE: This is very low]
            gsc.get_ticker_calendar(tsymbol, ticker, path)
        except ValueError:
            print(f'Error while getting stock calendar data for {tsymbol}')
        except RuntimeError:
            print(f'Could not get stock calendar data for {tsymbol}')

        try:
            #Get stock history
            result = gsh.get_ticker_history(tsymbol, ticker, path)
        except ValueError:
            print(f'\nError while getting ticker price history for {tsymbol}')
        except RuntimeError:
            print(f'\nCould not get stock price history data for {tsymbol}')

        return
