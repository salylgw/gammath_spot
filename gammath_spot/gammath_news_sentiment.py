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
from textblob import TextBlob

#Using default sentiment analyzer (Pattern Analyzer)
#NaiveBayesAnalyzer doesn't seem to be doing better in bare minimum tests
#Besides, it needs downloading of textblob.download_corpora
#So, will add this later if it does seem to show better results
def get_news_hl_sentiment_score(tsymbol, path):

    news_hl_sentiment_score_mean = 0

    #Get the news headlines from existing file
    if ((path / f'{tsymbol}_news_headlines.csv').exists()):
        #Get the latest options expiry date
        news_headlines = pd.read_csv(path / f'{tsymbol}_news_headlines.csv', index_col='Unnamed: 0')
        num_of_headlines = len(news_headlines)
        total_news_hl_sentiment_score = 0
        for i in range(num_of_headlines):
            #If it shows better results then at some point,
            #I might use sentiment.subjectivity as a filtering criteria
            try:
                #Get +/- sentiment score
                news_hl_sentiment_score = (TextBlob(news_headlines['title'][i]).sentiment.polarity)
                total_news_hl_sentiment_score += news_hl_sentiment_score
                #News source seems to limit to last 100 news headlines
                #This is mean score of news headlines
                news_hl_sentiment_score_mean = (total_news_hl_sentiment_score/num_of_headlines)
                news_hl_sentiment_score_mean = round(news_hl_sentiment_score_mean, 5)
            except:
                print(f'There was an error while during {tsymbol} news headline sentiment analysis')

    else:
        print(f'News headlines for {tsymbol} not found')

    return news_hl_sentiment_score_mean
