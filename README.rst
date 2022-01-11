# Gammath™ SPOT
Stock Price-Opining Tool is used to estimate if a stock is trading at a perceived discount or a perceived premium.

# How does it do that? It does this in two parts:
1. It provides a gammath_stocks_data_scraper.py app that scrapes the web to obtain stock information necessary to run its gScore computing algorithm
2. It provides a gammath_stocks_analyzer_and_scorer.py app that analyzes the stock data saved on the local storage from step 1 and computes scores using its algorithm to indicate perceived discount or perceived premium
3. The scores range between -1 and +1. Scores towards -1 indicates that the tool perceives the stock price to be at a premium while score towards +1 indicates that the tool preceives the stock price to be at a discount
4. Both the above apps take a watchlist as an input. A sample watch list is provided in sample_watchlist.csv [https://github.com/salylgw/gammath_spot.git] that can be used and updated for your watchlist

# External dependencies
This project uses following free tools that need to be installed (you can use pip install) to be able to use this tool:

1. numpy
2. pandas
3. ta-lib
4. yfinance
5. pykalman
6. statsmodels
7. matplotlib


# WHERE to get source code without installing
Get source code from GIT repo [https://github.com/salylgw/gammath_spot.git]

# HOWTO install
pip install gammath-spot


# HOWTO use these apps
1. If you installed this software then run: gammath_scraper sample_watchlist.csv > log_scraper.txt
2. If not installed but just obrained the code then go to the directory gammath_spot/gammath_spot where all the source files are and run: python gammath_stocks_data_scraper.py sample_watchlist.csv > log_scraper.txt
3. Above step will save the scraper log in log_scraper.txt, creates a 'tickers' sub-directory where it saves scraped data for stocks in the watch list
4. If you installed this software then run: gammath_scorer sample_watchlist.csv > log_scorer.txt
5. If not installed but just obrained the code then go to the directory gammath_spot/gammath_spot where all the source files are and run: python gammath_stocks_analyzer_and_scorer.py sample_watchlist.csv > log_scorer.txt
6. Above step will save the scorer log in log_scorer.txt, analyze the stock data and computes the gScore using Gammath's algorithm
7. Go to ticker sub-directory and open overall_gscores.csv in your favorite spreadsheet program or a text editor
8. In overall_gscores.csv, you should see stocks from your watchlist arrange in ascending order of gScores. Lower values (towards -1) indicate that the tool perceives the respective stock to be trading at a premium while higher values (towards +1) indicate that the tool perceives the respective stock to be trading at a doscount. There is a lot of useful information stored in tickers/"ticker_symbol" dir that can be checked for details. signal.txt shows details of the analysis results and "ticker_symbol"_charts.png shows the plotted charts
 
# Report Issues
If you run into any problem then please contact us using the contact page on https://www.gammathworks.com. You can also purchase technical support at https://www.gammathworks.com/plans-pricing.


# Happy SPOTing!
Note: This version of Gammath SPOT is free and open sourced. If you would like to contribute to this project through your expertise in Python and/or world of finance then please contact gammathworks.com indicating your area of interest and expertise
