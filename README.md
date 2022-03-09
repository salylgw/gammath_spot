# Gammath™ SPOT
**S**tock **P**rice-**O**pining **T**ool is a DIY stock technical analysis tool used to analyze stocks and compute gScore that indicates the degree at which a stock is trading at a perceived discount or a perceived premium. The gScore is then used like an indicator in making buy. sell or hold decision on the stock.

# How does it do that? It does this in two parts:
1. It provides a `gammath_stocks_data_scraper.py` app that scrapes the web to obtain stock information necessary to run its gScore computing algorithm.
2. It provides a `gammath_stocks_analyzer_and_scorer.py` app that analyzes the stock data saved on the local storage from step 1 and computes scores using its algorithm to indicate perceived discount or perceived premium.
3. The gScores range between -1 and +1. gScores towards -1 indicates that the tool perceives the stock price to be at a premium while gScore towards +1 indicates that the tool preceives the stock price to be at a discount.
4. Both the above apps take a watchlist as an input. A sample watch list is provided in [sample_watchlist.csv](https://github.com/salylgw/gammath_spot/blob/main/gammath_spot/sample_watchlist.csv) that can be used and updated for your watchlist.

# External dependencies
This project uses following free tools that need to be installed (you can use pip install) to be able to use this tool:

1. numpy
1. pandas
1. ta-lib (Install using miniconda in case you run into problem: `conda install -c conda-forge ta-lib`)
1. yfinance
1. pykalman
1. statsmodels
1. matplotlib


# WHERE to get source code without installing
Get source code from GIT repo [https://github.com/salylgw/gammath_spot.git]

# HOWTO install
`pip install gammath-spot`

In case you run into problem while installing ta-lib then you can install it using miniconda: `conda install -c conda-forge ta-lib`

# HOWTO build docker image
 1. Get Docker desktop (for MAC or Windows) or Docker Engine (for Linux) from [here](https://docs.docker.com/get-docker).
 2. Run it
 3. Open terminal or command prompt
 4. Use this [Dockerfile](https://github.com/salylgw/gammath_spot/blob/main/Dockerfile) in the directory where you want to build the image
 5. Run `docker build --no-cache=true --tag=gammath_spot .`

# HOWTO to run containerized Gammath™ SPOT
 1. Run docker desktop/engine that you installed
 2. Open terminal or command prompt
 3. Run `docker run -i -t -e TZ="America/Los_Angeles" --mount type=volume,source=gammath_spot_vol,target=/gammath_spot/gammath_spot gammath_spot /bin/bash`
 4. Note: You can replace the value for TZ to match your timezone

# HOWTO use these apps
1. If you installed this software then run: `gammath_scraper sample_watchlist.csv > log_scraper.txt`
1. If not installed but just obtained the code then go to the directory gammath_spot/gammath_spot where all the source files are and run: `python gammath_stocks_data_scraper.py sample_watchlist.csv > log_scraper.txt`
1. Above step will save the scraper log in `log_scraper.txt`, creates a `tickers/` sub-directory where it saves scraped data for stocks in the watch list
1. If you installed this software then run: `gammath_scorer sample_watchlist.csv > log_scorer.txt`
1. If not installed but just obtained the code then go to the directory `gammath_spot/gammath_spot/` where all the source files are and run: `python gammath_stocks_analyzer_and_scorer.py sample_watchlist.csv > log_scorer.txt`
1. Above step will save the scorer log in `log_scorer.txt`, analyze the stock data and computes the gScore using Gammath's algorithm.
1. Go to `ticker/` sub-directory and open `overall_gscores.csv` in your favorite spreadsheet program or a text editor.
1. In `overall_gscores.csv`, you should see stocks from your watchlist arrange in ascending order of gScores. Lower values (towards -1) indicate that the tool perceives the respective stock to be trading at a premium while higher values (towards +1) indicate that the tool perceives the respective stock to be trading at a doscount. There is a lot of useful information stored in `tickers/*symbol*` dir that can be checked for details. `signal.txt` shows details of the analysis results and `*symbol*_charts.png` shows the plotted charts

# Investment blog
If you want to see a real example of how output of this tool is being used then checkout [DIY Investment blog](https://www.gammathworks.com/diy-investment-blog).
 
# Report Issues
If you run into any problem then please contact us using the <https://www.gammathworks.com> contact page. You can also purchase technical support at <https://www.gammathworks.com/plans-pricing>.


# Happy SPOTing!
*Note: This version of Gammath SPOT is free and open source. If you would like to contribute to this project through your expertise in Python and/or world of finance then please contact us using the <https://www.gammathworks.com> contact page indicating your area of interest and expertise</u><u></u>*
