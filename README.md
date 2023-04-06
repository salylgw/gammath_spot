
![Alt text](https://raw.githubusercontent.com/salylgw/gammath_spot/main/gammath_spot/data/logo.png)

# Gammath SPOT
**S**tock **P**rice-**O**pining **T**oolset is a DIY stock technical analysis software that supports Graphical User Interface (GUI) and Command Line Interface (CLI). It is used to analyze stocks and compute a stock analysis score --- I'm calling it gScore (pronounced as "*ga Score*") --- to represent Gammath Works' stock analysis score. It indicates the degree to which a stock is trading at a perceived discount or at a perceived premium. SPOT also provides tools to generate price projection, support and resistance lines, gScore-history, backtesting and stock screening. Together, these can help in making your own stock-specific buy, sell, hold decisions.

# How does it do that? It does this in six parts:
1. It provides a `gammath_stocks_data_scraper.py` app that scrapes the web to obtain stock information necessary for algorithmic analysis and scoring.
2. It provides a `gammath_stocks_analyzer_and_scorer.py` app that analyzes the stock data saved on the local storage from step 1 and computes analysis scores using its algorithm to indicate a degree to which the stock is trading at a perceived discount or perceived premium. The Gammath Scores (gScores) range between -1 and +1. gScores closer to -1 indicate that the software perceives the stock to be trading at a premium while gScore closer to +1 indicates that the software preceives the stock to be trading at a discount. In addition, it also estimates current moving support and resistance lines for the stock price.
3. It provides a `gammath_stocks_pep.py` app that estimates and projects price for an approximately five (5) years time frame.
4. It provides a `gammath_stocks_gscores_historian.py` app that generates gScore and micro-gScores history for correlation and backtesting.
5. It provides a `gammath_stocks_backtesting.py` app that tests an implemented strategy and generates data to see how respective strategy did. It also generates "today's actions" summary for default strategy. This way the entire stock analysis and decision-making process is fully automated.
6. All the above apps take a watchlist as an input. A sample watch list is provided in [sample_watchlist.csv](https://github.com/salylgw/gammath_spot/blob/main/gammath_spot/sample_watchlist.csv) that can be used and updated for your watchlist.
7. It provides a `gammath_stocks_screener.py` app that helps screen stocks based on micro-gScores.
8. In addition to all the above tools, it also provides a `gammath_gui_app.py` -- an "all-in-one" application -- that provides a graphical user interface to the toolset.


# External dependencies
This project uses following free tools that need to be installed (you can use pip install) to be able to use this tool:

1. numpy
1. pandas
1. pandas_datareader
1. ta-lib (Install ta-lib using miniconda in case you run into problem: `conda install -c conda-forge ta-lib`)
1. yfinance
1. pykalman
1. statsmodels (Install statsmodels using miniconda in case you run into problems: `conda install statsmodels`)
1. scikit-learn
1. matplotlib (Install matplotlib using miniconda in case you run into problem: `conda install matplotlib`)
1. backtesting


# HOWTO install

If you want to use the GUI, it is <u>recommended to install miniconda</u> and then use following commands in your miniconda shell for installing gammath-spot:

 1. `conda install -c conda-forge ta-lib`
 2. `conda install statsmodels`
 3. `conda install matplotlib`
 4. `pip install gammath-spot`

If you want to use CLI and use prebuilt docker image. Please see the the instruction videos [here](https://youtube.com/playlist?list=PLck0jfgap9AT3Qd1mcNgr5KguIXrW9BD4).


# WHERE to get source code without installing
Get source code from GIT repo `git clone https://github.com/salylgw/gammath_spot.git`.


# HOWTO build docker image to use CLI
 1. Get Docker desktop (for MAC or Windows) or Docker Engine (for Linux) from [here](https://docs.docker.com/get-docker).
 2. Run it.
 3. Open terminal (MAC/Linux) or Power Shell (Windows)
 4. Use this [Dockerfile](https://github.com/salylgw/gammath_spot/blob/main/Dockerfile) in the directory where you want to build the image.
 5. Run `docker build --no-cache=true --tag=gammathworks/gammath_spot .`.


# HOWTO get prebuilt Gammath SPOT docker image to use CLI
 1. Repeat first three steps above.
 2. Run `docker pull gammathworks/gammath_spot`.

# HOWTO to run containerized Gammath SPOT with CLI
 1. Run docker desktop/engine that you installed.
 2. Open terminal or command prompt.
 3. Run `docker run -i -t -e TZ="America/Los_Angeles" --mount type=volume,source=gammath_spot_vol,target=/gammath_spot/gammath_spot gammathworks/gammath_spot /bin/bash`.
 4. Note: You can replace the value for TZ to match your timezone.


# HOWTO run these apps
1. If you installed this software to use it with the GUI then run: `gammath_spot_gui > log_gui.txt`. If not installed but just obtained the source code then go to the directory gammath_spot/gammath_spot where all the source files are and run: `python gammath_gui_app.py > log_gui.txt`. `log_gui.txt` should contain the GUI app's log. The GUI is self-explanatory to run the tools, watchlists operations, screeners, get results info etc. It is still under development and is made available as it enhances the ease-of-use. When using the GUI, the user need not use the commands in following instructions. However, the information about path information on where data and results are saved is still relevant. User can use that information to directly browse and view the data and results using native apps on the machine such as file explorer, spreadsheet viewer, PDF viewer etc.
1. If you want to use the CLI and installed this software then run: `gammath_scraper sample_watchlist.csv > log_scraper.txt`. See  [sample_watchlist.csv](https://github.com/salylgw/gammath_spot/blob/main/gammath_spot/sample_watchlist.csv). If not installed but just obtained the source code then go to the directory gammath_spot/gammath_spot where all the source files are and run: `python gammath_stocks_data_scraper.py sample_watchlist.csv > log_scraper.txt`.
1. Above step will save the scraper log in `log_scraper.txt` and save the scraped, formatted data in `tickers` sub-directory. Running the data scraper is essential to be able to use rest of the tools.
1. If you want to use the CLI and installed this software then run: `gammath_scorer sample_watchlist.csv > log_scorer.txt`. If not installed but just obtained the source code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_analyzer_and_scorer.py sample_watchlist.csv > log_scorer.txt`.
1. Above step will save the scorer log in `log_scorer.txt` and all of the Gammath SPOT's analysis and scoring data in `tickers` and `tickers/<ticker-symbol>` sub-directories. Go to `tickers/` sub-directory and open `<watchlist_name>_overall_gscores.csv` (e.g.: `sample_watchlist_overall_gscores.csv`) in your favorite spreadsheet program or a text editor. In `<watchlist_name>_overall_gscores.csv`, you should see stocks from your watchlist arranged in ascending order of gScores. In this file, you'll also see sh_gscore (stock history based gscore) and sci_gscore (current info based gacore) that make up the overall/final gscore. If you are not interested in backtesting or sub-component score then you can ignore it. There is a lot of useful information stored in `tickers/<ticker-symbol>` dir that can be checked for details. `<ticker-symbol>_signal.txt` shows details of the analysis results and `<ticker-symbol>_charts.pdf` shows the plotted charts. This tool also generates current moving estimated support and resistance lines for the stock and saves `<ticker-symbol>_tc.pdf` in `tickers/<ticker-symbol>` dir.
1. If you want to use the CLI and want to generate estimated price projection and have installed this software then run: `gammath_projector sample_watchlist.csv > log_projector.txt`. If not installed but just obtained the source code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_pep.py sample_watchlist.csv > log_projector.txt`.
1. Price projection chart and projections are saved in `tickers/<ticker-symbol>` dir. Chart and projection for S&P500 are saved in `tickers` dir. `<ticker-symbol>_pep.pdf` shows the chart and `<ticker-symbol>_pp.csv` shows the projected values. A sorted list of moving estimated projected 5Y returns are saved in `tickers/MPEP.csv`.
1. If you want to use the CLI and you want to generate historical gscores (for correlation, past performance, backtesting etc.) then you can do so by using the gScores historian tool. Please note that this tool takes a long time to run so limit the watchlist for this tool to few selected stocks that you want to zoom into. If you installed this software then run: `gammath_historian sample_watchlist.csv > log_historian.txt`. If not installed but just obtained the source code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_gscores_historian.py sample_watchlist.csv > log_historian.txt`.
1. You can check the `tickers/<ticker-symbol>/<ticker-symbol>_micro_gscores.csv` (for stock history based micro-gScores and corresponding total gScore) and `tickers/<ticker-symbol>/<ticker-symbol>_gscores_charts.pdf` that shows the plotted charts of price, overall stock history based gScore and micro-gScores.
1. You can do backtesting on provided watchlist. If you want to use the CLI and if you installed this software then run: `gammath_backtester sample_watchlist.csv > log_backtester.txt`. If not installed but just obtained the source code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_backtesting.py sample_watchlist.csv > log_backtester.txt`. You can update the function locally for implementing your own strategy.
1. For each stock, it processes (based on a strategy you implement/use) the data collected by scraper app and processes the stock history based gScore/micro-gScores for approximately last 5 years (that were saved from the gscore historian) and saves the backtesting stats in `tickers/<ticker_symbol>/<ticker_symbol>_gtrades_stats.csv`. You can check the backtesting stats to understand if the strategy you use worked historically and then decide whether to use that strategy or not. A sorted list of "Today's Actions" summary associated with default backtested strategy is saved in `tickers/Todays_Actions.csv`.
1. If you want to use the CLI and want to screen stocks based on micro-gScores and have installed this software then run: `gammath_screener screener.csv > log_screener.txt`. If not installed but just obtained the source code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_screener.py screener.csv > log_screener.txt`. Note that the filtering criteria (micro-gScores values) is specified in `screener.csv` and the results can be found in `tickers/screened_watchlist.csv`.


# HOWTO to get Gammath SPOT data from Docker desktop to your PC/MAC
1. Run docker desktop
1. Click on "Volumes"
1. Click on the Volume name
1. Click on Data
1. Scroll down to see tickers directory
1. Move the cursor to tickers. Notice the three dots on the right. Click on it
1. Click on "Save as"
1. Click on Save
1. Unzip the tickers.zip file
1. You should be able to view files using your favorite programs (e.g. Excel, Acrobat etc)


# Investment blog
If you want to see a free example of how output of this software is being used in decision-making then checkout [DIY Investment blog](https://www.gammathworks.com/diy-investment-blog).


# Questions
If you have any questions, then please contact me using this [form](https://www.gammathworks.com/contact).


# Happy SPOTing!
*Note: This version of Gammath SPOT is free and open source. If you would like to contribute to this project through your expertise in Python and/or world of finance then please contact me using this [form](https://www.gammathworks.com/contact) indicating your area of interest and expertise</u><u></u>*

*Gammth and SPOT are registered trade/service marks*.