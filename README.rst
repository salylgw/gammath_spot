# Gammath™ SPOT

Stock Price-Opining Tool is a DIY stock technical analysis toolset used to analyze stocks and compute gScore that indicates the degree at which a stock is trading at a perceived discount or a perceived premium. The gScore is then used like an indicator in making buy, sell or hold decision on the stock. It also provides a tool to generate price projection, a tool to generate gScore-history for correlation and a tool for backtesting strategy.

# How does it do that? It does this in five parts:

1. It provides a `gammath_stocks_data_scraper.py` app that scrapes the web to obtain stock information necessary to run its gScore computing algorithm
2. It provides a `gammath_stocks_analyzer_and_scorer.py` app that analyzes the stock data saved on the local storage from step 1 and computes gscores using its algorithm to indicate perceived discount or perceived premium
3. The gScores range between -1 and +1. gScores towards -1 indicates that the tool perceives the stock price to be at a premium while score towards +1 indicates that the tool preceives the stock price to be at a discount
4. It provides a `gammath_stocks_pep.py` app that projects estimated price for an approximately five (5) years time frame.
5. It provides a `gammath_stocks_gscores_historian.py` app that generates gScore and micro-gScores history for correlation. Learnings from this step can be applied in a backtesting strategy
6. It provides a `gammath_stocks_backtesting.py` app that tests an implemented strategy and generates data to see how respective strategy did. It also generates "today's actions" summary for default strategy
7. All the above apps take a watchlist as an input. A sample watch list is provided in `sample_watchlist.csv` [https://github.com/salylgw/gammath_spot.git] that can be used and updated for your watchlist

# External dependencies

This project uses following free tools that need to be installed (you can use pip install) to be able to use this tool:

1. numpy
2. pandas
3. pandas_datareader
4. ta-lib (Install ta-lib using miniconda in case you run into problem: `conda install -c conda-forge ta-lib`)
5. yfinance
6. pykalman
7. statsmodels
8. sklearn
9. matplotlib (Install matplotlib using miniconda in case you run into problem: `conda install matplotlib`)
10. backtesting


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
3. Above step will save the scraper log in `log_scraper.txt`, creates a `tickers` sub-directory where it saves scraped data for stocks in the watch list. Running the data scraper is essential before using the scorer and historian
4. If you installed this software then run:
    'gammath_scorer sample_watchlist.csv > log_scorer.txt`
5. If not installed but just obtained the code then go to the directory `gammath_spot/gammath_spot` where all the source files are and run:
    `python gammath_stocks_analyzer_and_scorer.py sample_watchlist.csv > log_scorer.txt`
6. Above step will save the scorer log in `log_scorer.txt`, analyze the stock data and computes the gScore using Gammath Works' algorithm
7. Go to `tickers` sub-directory and open `overall_gscores.csv` in your favorite spreadsheet program or a text editor
8. In `overall_gscores.csv`, you should see stocks from your watchlist arranged in ascending order of gScores. Lower values (towards -1) indicate that the tool perceives the respective stock to be trading at a premium while higher values (towards +1) indicate that the tool perceives the respective stock to be trading at a doscount. In this file, you'll also see sh_gscore (stock history based gscore) and sci_gscore (current info based gacore) that make up the overall gscore. If you are not interested in backtesting or sub-component score then you can ignore it These are the sub-components There is a lot of useful information stored in `tickers/"ticker_symbol"` dir that can be checked for details. `"ticker_symbol"_signal.txt` shows details of the analysis results and `"ticker_symbol"_charts.png` shows the plotted charts
9. If you want to generate estimated price projection and have installed this software then run: `gammath_projector sample_watchlist.csv > log_projector.txt`
10. If not installed but just obtained the code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_pep.py sample_watchlist.csv > log_projector.txt`
11. Price projection chart and projections are saved in `tickers/*symbol*` dir.
12. Chart and projection for S&P500 are saved in `tickers` dir. `*symbol*_pep.png` shows the chart and `*symbol*_pp.csv` shows the projected values. A sorted list of moving estimated projected 5Y returns are saved in `tickers/MPEP.csv`. `*symbol*_pep.png` shows the chart and `*symbol*_pp.csv` shows the projected values. A sorted list of moving estimated projected 5Y returns are saved in `tickers/MPEP.csv`
13. In case you want to collect historical gscores (for correlation, past performance etc.) then you can do so by using the gScores historian tool. Please note that this tool is slow at the moment so limit the watchlist for this tool to few selected stocks that you have want to zoom into
14. If you installed this software then run: `gammath_historian sample_watchlist.csv > log_historian.txt`
15. If not installed but just obtained the code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_gscores_historian.py sample_watchlist.csv > log_historian.txt`
16. You can check the `tickers/"ticker_symbol"/"ticker_symbol"_micro_gscores.csv` (for stock history based micro-gScores and corresponding total gScore) and `tickers/"ticker_symbol"/`"ticker_symbol"_gscores_charts.png` that shows the plotted charts of price, overall stock history based gScore and micro-gScores
17. You can do backtesting on provided watchlist. If you installed this software then run: `gammath_backtester sample_watchlist.csv > log_backtester.txt`
18. If not installed but just obtained the code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_backtesting.py sample_watchlist.csv > log_backtester.txt`. You can update the function locally for implementing your own strategy
19. For each stock, it processes (based on a strategy you implement/use) the data collected by scraper app and processes the stock history based gScore/micro-gScores for approximately last 5 years (that were saved from the gscore historian) and saves the backtesting stats in `tickers/<ticker_symbol>/<ticker_symbol>_gtrades_stats.csv`
20. You can check the backtesting stats to understand if the strategy you use worked historically and then decide whether to use that strategy or not
21. A sorted list of "Today's Actions" summary associated with default backtested strategy is saved in `tickers/Todays_Actions.csv`



# Investment blog

If you want to see a real example of how the ouput of this tool is used then checkout https://www.gammathworks.com/diy-investment-blog.

# Report Issues

If you run into any problem then please contact us using the contact page on https://www.gammathworks.com. You can also purchase technical support at https://www.gammathworks.com/plans-pricing.


# Happy SPOTing!

Note: This version of Gammath SPOT is free and open source. If you would like to contribute to this project through your expertise in Python and/or world of finance then please contact gammathworks.com indicating your area of interest and expertise
