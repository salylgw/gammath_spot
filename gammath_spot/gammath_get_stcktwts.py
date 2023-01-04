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
import urllib.request
import sys


def get_stocktwits_ticker_info(tsymbol, path):

    STOCKTWITS_TICKER_ADDR = 'https://stocktwits.com'

    url = f'{STOCKTWITS_TICKER_ADDR}/symbol/{tsymbol}'

    st_ticker_page_html = ''

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    try:
        with urllib.request.urlopen(url) as response:
            page = response.read()
            html_page = f'{page}'
            #Save the page for reference
            f = open(path / f'{tsymbol}_st_page.html', 'w')
            f.write(html_page)
            f.close()
    except:
        raise RuntimeError('stocktwits html page')

    return

