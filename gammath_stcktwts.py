# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

from pathlib import Path
import time
import re
import urllib.request

STOCKTWITS_TICKER_ADDR = 'https://stocktwits.com'

def get_stocktwits_ticker_info(tsymbol, path):

    st_buy_score = 0
    st_sell_score = 0
    st_max_score = 0
    sentiment_change = None
    volume_change = None

    print(f'\nGetting stocktwits signals for {tsymbol}')
    url = f'{STOCKTWITS_TICKER_ADDR}/symbol/{tsymbol}'
    print(url)

    pattern_for_sentiment_change = re.compile(r'("sentimentChange"):([-]*[0-9]*[.]*[0-9]*)')
    pattern_for_volume_change = re.compile(r'("volumeChange"):([-]*[0-9]*[.]*[0-9]*)')
    st_ticker_page_html = ''

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(url) as response:
        page = response.read()
        html_page = f'{page}'
        #Save the page for reference
        f = open(path / f'{tsymbol}_st_page.html', 'w')
        f.write(html_page)
        f.close()

        matched_string = pattern_for_sentiment_change.search(html_page)
        if (matched_string):
            kw, val = matched_string.groups()
            print('\nSentiment change data: ', kw, 'Val: ', val)
            sentiment_change = val
        else:
            print('\nSentiment change data NOT found for ticker ', tsymbol)

        matched_string = pattern_for_volume_change.search(html_page)
        if (matched_string):
            kw, val = matched_string.groups()
            print('\Volume change data: ', kw, 'Val: ', val)
            volume_change = val
        else:
            print('\nVolume change data NOT found for ticker ', tsymbol)

        sts_change = 0
        stv_change = 0
        st_buy_score = 0
        st_sell_score = 0
        st_max_score = 0

        if (sentiment_change is not None):
            sts_change = float(sentiment_change)
            st_tw_sentiment_change = f'sentiment_change: {sentiment_change}'

        if (volume_change is not None):
            stv_change = float(volume_change)
            st_tw_volume_change = f'volume_change: {volume_change}'

        if ((sts_change > 5.0) and (stv_change > 0)):
            st_buy_score += 1
        elif (sts_change < 0):
            st_sell_score += 1

        st_max_score += 1

    st_buy_rec = f'st_sv_buy_score:{st_buy_score}/{st_max_score}'
    st_sell_rec = f'st_sv_sell_score:{st_sell_score}/{st_max_score}'

    st_signals = f'{st_buy_rec},{st_sell_rec}'

    print(f'\nStocktwits signals extracted for {tsymbol}')
    return st_buy_score, st_sell_score, st_max_score, st_signals

