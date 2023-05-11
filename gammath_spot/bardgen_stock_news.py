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

#The source code in file is generated using Bard
#I've (Salyl Bhagwat) only made minor modifications (for compatibility and to make it work with Gammath SPOT)
#Please note that is experimental, barely tested and work-in-progress.

from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_stock_news_headlines(tsymbol, path, start_date='', end_date=''):

    # Make a request to the Google News API
    url = "https://news.google.com/news/feeds?q={}&output=rss&start_date={}&end_date={}".format(tsymbol, start_date, end_date)

    response = requests.get(url)

    # Parse the RSS feed
    soup = BeautifulSoup(response.content, features="lxml-xml")

    # Extract the news articles
    articles = soup.find_all("item")

    # Create a list to store the news articles
    news_articles = []

    # Iterate over the news articles
    for article in articles:

        # Get the title
        title = article.find("title").text

        # Get the description
        #description = article.find("description").text

        # Get the date
        date = article.find("pubDate").text

        # Get the link
        link = article.find("link").text

        # Create a dictionary to store the news article
        news_article = {
            "title": title,
            #"description": description,
            "date": date,
            "link": link
        }

        # Add the news article to the list
        news_articles.append(news_article)

    #Create a dataframe for news article summary
    df = pd.DataFrame(news_articles)

    #Save the news headlines in a CSV file for later sentiments analysis
    df.to_csv(path / f'{tsymbol}_news_headlines.csv')
