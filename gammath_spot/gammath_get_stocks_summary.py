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

import yfinance as yf
from pathlib import Path
import pandas as pd
import sys
import time
import os

def get_ticker_summary(tsymbol, ticker, path):

    #Get stock info summary from the internet

    if (len(tsymbol) == 0):
        raise ValueError('Invalid symbol')

    #Check if file exists and is it from another day
    file_exists = (path / f'{tsymbol}_summary.csv').exists()

    if file_exists:
        fstat = os.stat(path / f'{tsymbol}_summary.csv')
        fct_time = time.ctime(fstat.st_ctime).split(' ')
        if (fct_time[2] == ''):
            fct_date_index = 3
        else:
            fct_date_index = 2

        fct_date = int(fct_time[fct_date_index])
        dt = time.strftime('%x').split('/')
        dt_date = int(dt[1])

        if (fct_date == dt_date):
            dont_need_fetch = True
        else:
            dont_need_fetch = False
    else:
        dont_need_fetch = False

    #Check if we need to get new summary info
    if (dont_need_fetch):
        return
    else:
        try:
            stock_summary = ticker.info
        except:
            raise ValueError('Stock summary not found')

    #Extract the items of interest
    #trailingPE
    #forwardPE
    #shortRatio
    #pegRatio
    #currentRatio
    #quickRatio
    #beta
    #heldPercentInstitutions
    #heldPercentInsiders
    #priceToBook
    #state
    #country

    try:
        trailingPE = stock_summary['trailingPE']
    except:
        trailingPE = 0

    try:
        forwardPE = stock_summary['forwardPE']
    except:
        forwardPE = 0

    try:
        shortRatio = stock_summary['shortRatio']
    except:
        shortRatio = 0

    try:
        pegRatio = stock_summary['pegRatio']
    except:
        pegRatio = 0

    try:
        currentRatio = stock_summary['currentRatio']
    except:
        currentRatio = 0

    try:
        quickRatio = stock_summary['quickRatio']
    except:
        quickRatio = 0

    try:
        beta = stock_summary['beta']
    except:
        beta = 0

    try:
        heldPercentInstitutions = stock_summary['heldPercentInstitutions']
    except:
        heldPercentInstitutions = 0
    try:
        heldPercentInsiders = stock_summary['heldPercentInsiders']
    except:
        heldPercentInsiders = 0

    try:
        pbr = stock_summary['priceToBook']
    except:
        pbr = 0

    try:
        state = stock_summary['state']
    except:
        state = ''

    try:
        country = stock_summary['country']
    except:
        country = ''

    df = pd.DataFrame({'trailingPE': trailingPE, 'forwardPE': forwardPE, 'shortRatio': shortRatio, 'pegRatio': pegRatio, 'currentRatio': currentRatio, 'quickRatio': quickRatio, 'beta': beta, 'heldPercentInstitutions': heldPercentInstitutions, 'heldPercentInsiders': heldPercentInsiders, 'priceToBook': pbr, 'state': state, 'country': country}, index=range(1))

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    #Save the history for reference and processing
    df.to_csv(path / f'{tsymbol}_summary.csv')

    return
