# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import urllib.request
import sys


def get_stocktwits_ticker_info(tsymbol, path):

    STOCKTWITS_TICKER_ADDR = 'https://stocktwits.com'

    url = f'{STOCKTWITS_TICKER_ADDR}/symbol/{tsymbol}'
    print(url)

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
            print(f'\nStocktwits page saved for {tsymbol}')
    except:
        raise RuntimeError('stocktwits html page')

    return

