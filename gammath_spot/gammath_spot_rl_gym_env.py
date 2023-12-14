# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
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

__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works'

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import gymnasium as gym
from gymnasium import spaces
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

#This is a work-in-progress. A lot will change before it is usable

#Environment that is compatible with Gymnasium
class SPOT_environment(gym.Env):
    metadata = {'render_modes': []}

    def __init__(self, tsymbol):
        self.ticker = tsymbol
        self.step = 0
        self.init_SPOT_RL_env_data(tsymbol)
        self.action_space = spaces.Discrete(len(self.action_types))
        self.observation_space = spaces.Box(self.SPOT_vals_mins, self.SPOT_vals_maxs)
        self.reset()

    def reset(self):
        #step 0
        self.step = 0
        #Get initial value reading
        obs = self.SPOT_vals.iloc[self.step].values
        done = False
        #info might need to be returned. TBD
        return obs, done

    def take_obs_step(self):
        obs = self.SPOT_vals.iloc[self.step].values
        self.step += 1
        done = self.step > self.steps
        return obs, done

    def take_trade_action_step(self, action):
        #TBD
        reward = 0
        info = {}

        return reward, info

    def render(self):
        #action not required
        pass

    def init_SPOT_RL_env_data(self, tsymbol):
        #Get gscores history
        df = pd.read_csv(f'tickers/{tsymbol}/{tsymbol}_micro_gscores.csv', index_col='Unnamed: 0')

        #Filter out parts not needed for RL
        self.SPOT_vals = df.drop(['Date', 'Close', 'TPC5Y', 'CSL', 'CRL', 'PDSL', 'PDRL', 'DDBTP', 'DPSTP'], axis=1)

        #Price history corresponding to steps
        self.prices = df.Close
        self.steps = len(self.SPOT_vals)
        #Need min/max for gymnasium
        self.SPOT_vals_mins = np.array(self.SPOT_vals.min())
        self.SPOT_vals_maxs = np.array(self.SPOT_vals.max())

        #Basic action types
        self.action_types = ['Sell', 'Hold', 'Buy']

        self.actions = np.zeros(self.steps)
        trading_transactions = pd.DataFrame(columns=gut.get_trading_bt_columns(), index=range(self.steps))
