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
import time
import re
import sys

STOCKTWITS_TICKER_ADDR = 'https://stocktwits.com'

def get_stocktwits_signals(tsymbol, path):

    st_gscore = 0
    st_max_score = 0
    sentiment_change = None
    volume_change = None

    #RE to extract sentiment change value
    pattern_for_sentiment_change = re.compile(r'("sentimentChange"):([-]*[0-9]*[.]*[0-9]*)')

    #RE to extract volume change value
    pattern_for_volume_change = re.compile(r'("volumeChange"):([-]*[0-9]*[.]*[0-9]*)')
    st_ticker_page_html = ''

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    try:
        #Read the saved page
        f = open(path / f'{tsymbol}_st_page.html')
        html_page = f.read()
        f.close()

        #Find the sentiment change score
        matched_string = pattern_for_sentiment_change.search(html_page)
        if (matched_string):
            kw, val = matched_string.groups()
            sentiment_change = val

        #Find the volume change score
        matched_string = pattern_for_volume_change.search(html_page)
        if (matched_string):
            kw, val = matched_string.groups()
            volume_change = val

        sts_change = 0
        stv_change = 0

        if (sentiment_change is not None):
            #Convert to the float type
            sts_change = float(sentiment_change)
            st_tw_sentiment_change = f'sentiment_change: {sentiment_change}'

        if (volume_change is not None):
            #Convert to the float type
            stv_change = float(volume_change)
            st_tw_volume_change = f'volume_change: {volume_change}'

        #Token score and information logging purpose
        if ((sts_change > 0) and (stv_change > 0)):
            st_gscore += 5
        elif (sts_change > 0):
            st_gscore += 2
        else:
            st_gscore -= 5

    except:
        raise RuntimeError('Stocktwits signal generation failed')

    st_max_score += 5

    st_grec = f'st_sv_gscore:{st_gscore}/{st_max_score}'

    st_signals = f'{st_grec}'

    return st_gscore, st_max_score, st_signals

