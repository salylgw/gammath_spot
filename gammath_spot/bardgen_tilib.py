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

import pandas as pd

def compute_macd(prices, slow=26, fast=12, signal=9):
    ema12 = prices.ewm(span=fast, min_periods=fast-1).mean()
    ema26 = prices.ewm(span=slow, min_periods=slow-1).mean()

    macd = ema12 - ema26

    signal_line = macd.ewm(span=signal, min_periods=signal-1).mean()
    macd_hist = macd - signal_line

    return macd, signal_line, macd_hist


def compute_stochastic_slow(high, low, close, slow_k_period=3, slow_d_period=3, fastk_period=14):
    #Get lowest low and highest high over fast k period
    lowest_low = low.rolling(window=fastk_period).min()
    highest_high = high.rolling(window=fastk_period).max()

    fast_k = (close - lowest_low) / (highest_high - lowest_low)*100
    fast_k = pd.Series(fast_k, index=close.index)

    #Get slow K and slow D
    slow_k = fast_k.rolling(window=slow_k_period).mean()
    slow_d = slow_k.rolling(window=slow_d_period).mean()
    return slow_k, slow_d
