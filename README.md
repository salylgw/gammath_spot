# Gammath SPOT
Stock Price-Opining Tool is used to determine if a stock is trading at a perceived discount or a perceived premium.
How does it do that? It does this in two parts:
 1. It provides a gammath_stocks_data_scraper.py app that scrapes the web to obtain stock information necessary to run its gScore computing algorithm
 2. It provides a gammath_stocks_analyzer_and_scorer.py app that analyzes the stock data saved on the local storage from step 1 and computes scores using its algorithm to indicate perceived discount or perceived premium
 3. The scores range between -1 and +1. Scores towards -1 indicates that the tool perceives the stock price to be at a premium while score towards +1 indicates that the tool preceives the stock price to be at a discount
 4. Both the above apps take a watchlist as an input. A sample watch list is provided in sample_watchlist.csv that can be used and updated for your watchlist

# External dependencies
This project uses following free tools that need to be installed (you can use pip install) to be able to use this tool:
 1. numpy
 2. pandas
 3. ta-lib
 4. yfinance
 5. pykalman
 6. statsmodels
 7. matplotlib

# HOWTO use these apps
 1. Go to the directory gammath_spot/gammath_spot where all the source files are
 2. Run: python gammath_stocks_data_scraper.py sample_watchlist.csv > log_scraper.txt
 3. Above step will save the scraper log in log_scraper.txt, creates a 'tickers' sub-directory where it saves scraped data for stocks in the watch list
 4. Run: python gammath_stocks_analyzer_and_scorer.py sample_watchlist.csv > log_scorer.txt
 5. Above step will ave the scorer log in log_scorer.txt, analyze the stock data and computes the gScore using Gammath's algorithm
 6. Go to ticker sub-directory and open overall_gscores.csv in your favorite spreadsheet program or a text editor
 7. In overall_gscores.csv, you should see stocks from your watchlist arrange in ascending order of gScores. Lower values (towards -1) indicate that the tool perceives the respective stock to be trading at a premium while higher values (towards +1) indicate that the tool perceives the respective stock to be trading at a doscount
 8. There is a lot of useful information stored in tickers/*symvik* dir that can be checked for details. signal.txt shows details of the analysis results and *symbol*_charts.png shows the plotted charts
 
# Install with pip install
If you are looking to install this project locally and use this as a normal app that can be run from anywhere then please contact gammathworks.com to upload the package to PyPI



# Happy SPOTing!
*Note: This is a free and open source project. If you would like to contribute to this project through your expertise in Python and/or world of finance then please contact gammathworks.com indicating your area of interest and expertise</u><u></u>*
