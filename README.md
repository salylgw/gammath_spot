# Gammath™ SPOT
**S**tock **P**rice-**O**pining **T**ool is a DIY stock technical analysis toolset used to analyze stocks and compute gScore that indicates the degree at which a stock is trading at a perceived discount or a perceived premium. The gScore is then used like an indicator in making buy, sell or hold decision on the stock. It also provides a tool to generate price projection, a tool to generate gScore-history for correlation and a tool for backtesting strategy.

# How does it do that? It does this in five parts:
1. It provides a `gammath_stocks_data_scraper.py` app that scrapes the web to obtain stock information necessary to run its gScore computing algorithm.
2. It provides a `gammath_stocks_analyzer_and_scorer.py` app that analyzes the stock data saved on the local storage from step 1 and computes scores using its algorithm to indicate perceived discount or perceived premium.
3. The gScores range between -1 and +1. gScores towards -1 indicates that the tool perceives the stock price to be at a premium while gScore towards +1 indicates that the tool preceives the stock price to be at a discount.
4. It provides a `gammath_stocks_pep.py` app that projects estimated price for an approximately five (5) years time frame.
5. It provides a `gammath_stocks_gscores_historian.py` app that generates gScore and micro-gScores history for correlation. Learnings from this step can be applied in a backtesting strategy
6. It provides a `gammath_stocks_backtesting.py` app that tests an implemented strategy and generates data to see how respective strategy did
7. All the above apps take a watchlist as an input. A sample watch list is provided in [sample_watchlist.csv](https://github.com/salylgw/gammath_spot/blob/main/gammath_spot/sample_watchlist.csv) that can be used and updated for your watchlist.

# External dependencies
This project uses following free tools that need to be installed (you can use pip install) to be able to use this tool:

1. numpy
1. pandas
1. pandas_datareader
1. ta-lib (Install ta-lib using miniconda in case you run into problem: `conda install -c conda-forge ta-lib`)
1. yfinance
1. pykalman
1. statsmodels
1. sklearn
1. matplotlib (Install matplotlib using miniconda in case you run into problem: `conda install matplotlib`)
1. backtesting

# WHERE to get source code without installing
Get source code from GIT repo `git clone https://github.com/salylgw/gammath_spot.git`

# HOWTO install
`pip install gammath-spot`

In case you run into problem while installing ta-lib then you can install it using miniconda: `conda install -c conda-forge ta-lib` then run `pip install gammath-spot`

# HOWTO build docker image
 1. Get Docker desktop (for MAC or Windows) or Docker Engine (for Linux) from [here](https://docs.docker.com/get-docker).
 2. Run it
 3. Open terminal (MAC/Linux) or Power Shell (Windows)
 4. Use this [Dockerfile](https://github.com/salylgw/gammath_spot/blob/main/Dockerfile) in the directory where you want to build the image
 5. Run `docker build --no-cache=true --tag=gammathworks/gammath_spot .`


# HOWTO get prebuilt Gammath™ SPOT docker image
 1. Repeat first three steps above
 2. Run `docker pull gammathworks/gammath_spot`

# HOWTO to run containerized Gammath™ SPOT
 1. Run docker desktop/engine that you installed
 2. Open terminal or command prompt
 3. Run `docker run -i -t -e TZ="America/Los_Angeles" --mount type=volume,source=gammath_spot_vol,target=/gammath_spot/gammath_spot gammathworks/gammath_spot /bin/bash`
 4. Note: You can replace the value for TZ to match your timezone

# HOWTO use these apps
1. If you installed this software then run: `gammath_scraper sample_watchlist.csv > log_scraper.txt`
1. If not installed but just obtained the code then go to the directory gammath_spot/gammath_spot where all the source files are and run: `python gammath_stocks_data_scraper.py sample_watchlist.csv > log_scraper.txt`
1. Above step will save the scraper log in `log_scraper.txt`, creates a `tickers/` sub-directory where it saves scraped data for stocks in the watch list. Running the data scraper is essential before using the scorer and historian
1. If you installed this software then run: `gammath_scorer sample_watchlist.csv > log_scorer.txt`
1. If not installed but just obtained the code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_analyzer_and_scorer.py sample_watchlist.csv > log_scorer.txt`
1. Above step will save the scorer log in `log_scorer.txt`, analyze the stock data and computes the gScore using Gammath's algorithm.
1. Go to `ticker/` sub-directory and open `overall_gscores.csv` in your favorite spreadsheet program or a text editor.
1. In `overall_gscores.csv`, you should see stocks from your watchlist arrange in ascending order of gScores. Lower values (towards -1) indicate that the tool perceives the respective stock to be trading at a premium while higher values (towards +1) indicate that the tool perceives the respective stock to be trading at a doscount. In this file, you'll also see sh_gscore (stock history based gscore) and sci_gscore (current info based gacore) that make up the overall gscore. If you are not interested in backtesting or sub-component score then you can ignore it There is a lot of useful information stored in `tickers/*symbol*` dir that can be checked for details. `*symbol*_signal.txt` shows details of the analysis results and `*symbol*_charts.png` shows the plotted charts
1. If you want to generate estimated price projection and have installed this software then run: `gammath_projector sample_watchlist.csv > log_projector.txt`
1. If not installed but just obtained the code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_pep.py sample_watchlist.csv > log_projector.txt`
1. Price projection chart and projections are saved in `tickers/*symbol*` dir. `*symbol*_pep.png` shows the chart and `*symbol*_pp.csv` shows the projected values
1. In case you want to collect historical gscores (for correlation, past performance etc.) then you can do so by using the gScores historian tool. Please note that this tool is slow at the moment so limit the watchlist for this tool to few selected stocks that you have want to zoom into
1. If you installed this software then run: `gammath_historian sample_watchlist.csv > log_historian.txt`
1. If not installed but just obtained the code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_gscores_historian.py sample_watchlist.csv > log_historian.txt`
1. You can check the `tickers/"ticker_symbol"/"ticker_symbol"_micro_gscores.csv` (for stock history based micro-gScores and corresponding total gScore) and `tickers/"ticker_symbol"/`"ticker_symbol"_gscores_charts.png` that shows the plotted charts of price, overall stock history based gScore and micro-gScores
1. You can do backtesting on provided watchlist. If you installed this software then run: `gammath_backtester sample_watchlist.csv > log_backtester.txt`
1. If not installed but just obtained the code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_backtesting.py sample_watchlist.csv > log_backtester.txt`. You can update the function locally for implementing your own strategy
1. For each stock, it processes (based on a strategy you implement/use) the data collected by scraper app and processes the stock history based gScore/micro-gScores for approximately last 5 years (that were saved from the gscore historian) and saves the backtesting stats in `tickers/<ticker_symbol>/<ticker_symbol>_gtrades_stats.csv`
1. You can check the backtesting stats to understand if the strategy you use worked historically and then decide whether to use that strategy or not

# Investment blog
If you want to see a real example of how output of this tool is being used then checkout [DIY Investment blog](https://www.gammathworks.com/diy-investment-blog).
 
# Report Issues
If you run into any problem then please contact us using the <https://www.gammathworks.com> contact page. You can also purchase technical support at <https://www.gammathworks.com/plans-pricing>.


# Happy SPOTing!
*Note: This version of Gammath SPOT is free and open source. If you would like to contribute to this project through your expertise in Python and/or world of finance then please contact us using the <https://www.gammathworks.com> contact page indicating your area of interest and expertise</u><u></u>*
