# Gammath™ SPOT

Stock Price-Opining Tool is a DIY stock technical analysis tool used to analyze stocks and compute gScore that indicates the degree at which a stock is trading at a perceived discount or a perceived premium. The gScore is then used like an indicator in making buy, sell or hold decision on the stock.

# How does it do that? It does this in two parts:

1. It provides a `gammath_stocks_data_scraper.py` app that scrapes the web to obtain stock information necessary to run its gScore computing algorithm
2. It provides a `gammath_stocks_analyzer_and_scorer.py` app that analyzes the stock data saved on the local storage from step 1 and computes gscores using its algorithm to indicate perceived discount or perceived premium
3. The gScores range between -1 and +1. gScores towards -1 indicates that the tool perceives the stock price to be at a premium while score towards +1 indicates that the tool preceives the stock price to be at a discount
4. Both the above apps take a watchlist as an input. A sample watch list is provided in `sample_watchlist.csv` [https://github.com/salylgw/gammath_spot.git] that can be used and updated for your watchlist

# External dependencies

This project uses following free tools that need to be installed (you can use pip install) to be able to use this tool:

1. numpy
2. pandas
3. ta-lib (Install ta-lib using miniconda in case you run into problem: `conda install -c conda-forge ta-lib`)
4. yfinance
5. pykalman
6. statsmodels
7. sklearn
8. matplotlib


# WHERE to get source code without installing

Get source code from GIT repo `git clone https://github.com/salylgw/gammath_spot.git`

# HOWTO install

`pip install gammath-spot`

In case you have trouble installing ta-lib then you can install miniconda and use `conda install -c conda-forge ta-lib` then run `pip install gammath-spot`



# HOWTO use these apps

1. If you installed this software then run:
    `gammath_scraper sample_watchlist.csv > log_scraper.txt`
2. If not installed but just obtained the code then go to the directory `gammath_spot/gammath_spot` where all the source files are and run:
    `python gammath_stocks_data_scraper.py sample_watchlist.csv > log_scraper.txt`
3. Above step will save the scraper log in `log_scraper.txt`, creates a `tickers` sub-directory where it saves scraped data for stocks in the watch list
4. If you installed this software then run:
    'gammath_scorer sample_watchlist.csv > log_scorer.txt`
5. If not installed but just obtained the code then go to the directory `gammath_spot/gammath_spot` where all the source files are and run:
    `python gammath_stocks_analyzer_and_scorer.py sample_watchlist.csv > log_scorer.txt`
6. Above step will save the scorer log in `log_scorer.txt`, analyze the stock data and computes the gScore using Gammath Works' algorithm
7. Go to `ticker` sub-directory and open `overall_gscores.csv` in your favorite spreadsheet program or a text editor
8. In `overall_gscores.csv`, you should see stocks from your watchlist arranged in ascending order of gScores. Lower values (towards -1) indicate that the tool perceives the respective stock to be trading at a premium while higher values (towards +1) indicate that the tool perceives the respective stock to be trading at a doscount. There is a lot of useful information stored in `tickers/"ticker_symbol"` dir that can be checked for details. `signal.txt` shows details of the analysis results and `"ticker_symbol"_charts.png` shows the plotted charts

# Investment blog

If you want to see a real example of how the ouput of this tool is used then checkout https://www.gammathworks.com/diy-investment-blog.

# Report Issues

If you run into any problem then please contact us using the contact page on https://www.gammathworks.com. You can also purchase technical support at https://www.gammathworks.com/plans-pricing.


# Happy SPOTing!

Note: This version of Gammath SPOT is free and open source. If you would like to contribute to this project through your expertise in Python and/or world of finance then please contact gammathworks.com indicating your area of interest and expertise
