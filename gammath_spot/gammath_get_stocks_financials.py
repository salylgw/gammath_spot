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
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

def get_ticker_financials(tsymbol, ticker, path):

    if (len(tsymbol) == 0):
        raise ValueError('Invalid symbol')

    MIN_DELAY_BETWEEN_BATCHES = 1
    MAX_DELAY_BETWEEN_BATCHES = 3

    qbs_dont_need_fetch = True
    qcf_dont_need_fetch = True
    qe_dont_need_fetch = True
    qf_dont_need_fetch = True
    reco_dont_need_fetch = True

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    try:
        file_exists = (path / f'{tsymbol}_qbs.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_qbs.csv')
            qbs_dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            qbs_dont_need_fetch = False
    except:
        print(f'\nQuarterly balance sheet for ticker {tsymbol} not found')

    try:
        file_exists = (path / f'{tsymbol}_qcf.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_qcf.csv')
            qcf_dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            qcf_dont_need_fetch = False
    except:
        qcf_dont_need_fetch = False

    try:
        file_exists = (path / f'{tsymbol}_qe.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_qe.csv')
            qe_dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            qe_dont_need_fetch = False
    except:
        qe_dont_need_fetch = False

    try:
        file_exists = (path / f'{tsymbol}_qf.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_qf.csv')
            qf_dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            qf_dont_need_fetch = False
    except:
        qf_dont_need_fetch = False

    try:

        file_exists = (path / f'{tsymbol}_reco.csv').exists()

        #Check if file exists and is it from another day
        if file_exists:
            fstat = os.stat(path / f'{tsymbol}_reco.csv')
            reco_dont_need_fetch = gut.check_if_same_day(fstat)
        else:
            reco_dont_need_fetch = False
    except:
        reco_dont_need_fetch = False


    if (qbs_dont_need_fetch and qcf_dont_need_fetch and qe_dont_need_fetch and qf_dont_need_fetch and reco_dont_need_fetch):
        return
    else:

        if not qbs_dont_need_fetch:
            try:
                stock_balance_sheet = ticker.quarterly_balancesheet
                if (len(stock_balance_sheet) > 0):
                    #Save the data for reference and processing
                    stock_balance_sheet.to_csv(path / f'{tsymbol}_qbs.csv')
            except:
                qbs_dont_need_fetch = True

        if not qcf_dont_need_fetch:
            try:
                stock_cash_flow = ticker.quarterly_cashflow
                if (len(stock_cash_flow) > 0):
                    #Save the data for reference and processing
                    stock_cash_flow.to_csv(path / f'{tsymbol}_qcf.csv')
            except:
                qcf_dont_need_fetch = True

        if not qe_dont_need_fetch:
            try:
                stock_earnings = ticker.quarterly_earnings
                #Save the data for reference and processing
                if (len(stock_earnings) > 0):
                    stock_earnings.to_csv(path / f'{tsymbol}_qe.csv')
            except:
                qe_dont_need_fetch = True

        if not qf_dont_need_fetch:
            try:
                stock_financials = ticker.quarterly_financials
                if (len(stock_financials) > 0):
                    #Save the data for reference and processing
                    stock_financials.to_csv(path / f'{tsymbol}_qf.csv')
            except:
                qf_dont_need_fetch = True

        if not reco_dont_need_fetch:
            try:
                stock_recommendations = ticker.recommendations
                if (len(stock_recommendations) > 0):
                    #Save the data for reference and processing
                    stock_recommendations.to_csv(path / f'{tsymbol}_reco.csv')
            except:
                reco_dont_need_fetch = True

    return
