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

#The source code in file is generated using ChatGPT
#I've (Salyl Bhagwat) only made minor modifications for compatibility.

#Please note that is experimental and barely tested
#The reason for this file. Many users have expressed problem installing talib.
#Installing from conda-forge channel resolves it but there have been some users who don't prefer that way.
#There are other options but now that I have help from ChatGPT....

import pandas as pd
import numpy as np

def compute_bollinger_bands(prices, window=14, num_std=2):
    rolling_mean = prices.rolling(window=window).mean()
    rolling_std = prices.rolling(window=window).std()

    upper_band = rolling_mean + num_std * rolling_std
    lower_band = rolling_mean - num_std * rolling_std

    return upper_band, rolling_mean, lower_band


def compute_rsi(prices, window=14):
    deltas = np.diff(prices)
    seed = deltas[:window+1]
    up = seed[seed >= 0].sum() / window
    down = -seed[seed < 0].sum() / window
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:window] = 100. - 100. / (1. + rs)

    for i in range(window, len(prices)):
        delta = deltas[i - 1]  # delta refers to the price difference between two consecutive periods
        if delta > 0:
            upval = delta
            downval = 0.0
        else:
            upval = 0.0
            downval = -delta

        up = (up * (window - 1) + upval) / window
        down = (down * (window - 1) + downval) / window
        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    #Return in pandas series
    rsi = pd.Series(rsi)

    return rsi

def compute_mfi(high_prices, low_prices, close_prices, volumes, period=14):
    assert len(high_prices) == len(low_prices) == len(close_prices) == len(volumes), "Input lists must have the same length"

    typical_prices = [(high + low + close) / 3 for high, low, close in zip(high_prices, low_prices, close_prices)]
    raw_money_flows = [typical_price * volume for typical_price, volume in zip(typical_prices, volumes)]

    prices_len = len(typical_prices)
    positive_money_flows = []
    negative_money_flows = []

    for i in range(1, prices_len):
        if typical_prices[i] > typical_prices[i - 1]:
            positive_money_flows.append(raw_money_flows[i])
            negative_money_flows.append(0)
        elif typical_prices[i] < typical_prices[i - 1]:
            positive_money_flows.append(0)
            negative_money_flows.append(raw_money_flows[i])
        else:
            positive_money_flows.append(0)
            negative_money_flows.append(0)

    mfi_values = np.zeros(prices_len)

    for i in range(period - 1, prices_len):
        positive_money_flow_sum = sum(positive_money_flows[i - period + 1 : i + 1])
        negative_money_flow_sum = sum(negative_money_flows[i - period + 1 : i + 1])

        if negative_money_flow_sum == 0:
            mfi = 100
        else:
            money_flow_ratio = positive_money_flow_sum / negative_money_flow_sum
            mfi = 100 - (100 / (1 + money_flow_ratio))

        mfi_values[i] = mfi

    #Return in pandas series
    mfi = pd.Series(mfi_values)

    return mfi

def compute_macd(prices, slow_period=26, fast_period=12, signal_period=9):
    slow_ema = calculate_ema(prices, slow_period)
    fast_ema = calculate_ema(prices, fast_period)

    macd_line = fast_ema - slow_ema
    signal_line = calculate_ema(macd_line, signal_period)
    histogram = macd_line - signal_line

    macd_line = pd.Series(macd_line)
    signal_line = pd.Series(signal_line)
    histogram = pd.Series(histogram)

    return macd_line, signal_line, histogram

def calculate_ema(prices, period):
    ema = np.zeros_like(prices)
    ema[period-1] = np.mean(prices[:period])
    smoothing_factor = 2 / (period + 1)

    for i in range(period, len(prices)):
        ema[i] = (prices[i] - ema[i-1]) * smoothing_factor + ema[i-1]

    return ema

#I prefer talib's STOCH function. This implementation from ChatGPT could be a good starting point as an alternative
def compute_stoch(close_prices, low_prices, high_prices, k_period, d_period, slowing_period):

    highest_high = np.max(high_prices)
    lowest_low = np.min(low_prices)

    # Calculate %K line
    k_line = (close_prices - lowest_low) / (highest_high - lowest_low) * 100
    k_line = simple_moving_average(k_line, k_period)

    # Calculate %D line
    d_line = simple_moving_average(k_line, d_period)

    # Calculate slow %K line
    slow_k_line = simple_moving_average(k_line, slowing_period)

    # Calculate slow %D line using exponential moving average
    slow_d_line = exponential_moving_average(slow_k_line, slowing_period)

    #Return in pandas series
    slow_k_line = pd.Series(slow_k_line)
    slow_d_line = pd.Series(slow_d_line)

    return slow_k_line, slow_d_line

def simple_moving_average(values, n):

    sma = np.convolve(values, np.ones(n)/n, mode='valid')
    nan_padding = np.full(n-1, np.nan)

    return np.concatenate((nan_padding, sma), axis=0)

def exponential_moving_average(values, n):

    weights = np.exp(np.linspace(-1., 0., n))
    weights /= weights.sum()
    ema = np.convolve(values, weights, mode='valid')
    nan_padding = np.full(n-1, np.nan)

    return np.concatenate((nan_padding, ema), axis=0)
