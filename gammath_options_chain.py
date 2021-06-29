# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import yfinance as yf
from pathlib import Path


Options_Tickers_dir = Path('tickers/options')

def get_ticker_options(tsymbol):
    if (len(tsymbol) == 0):
        return None

    path = Options_Tickers_dir / f'{tsymbol}'
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    ticker = yf.Ticker(tsymbol)
    option_dates = ticker.options

    for option_date in option_dates:
        options = ticker.option_chain(option_date)
        options.calls.info()
        options.puts.info()
        options.calls.to_csv(path / f'{tsymbol}_call_{option_date}.csv')
        options.puts.to_csv(path / f'{tsymbol}_put_{option_date}.csv')

    return path
