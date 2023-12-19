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
from gymnasium.envs.registration import register
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

#This is a work-in-progress. A lot will change before it is usable

#Environment that is compatible with Gymnasium
class SPOT_environment(gym.Env):
    metadata = {'render_modes': []}

    def __init__(self, tsymbol, max_trading_days):
        self.ticker = tsymbol
        self.max_trading_days = max_trading_days
        self.steps = max_trading_days
        self.random_start_index = 0
        self.init_SPOT_RL_env_data(tsymbol)
        self.action_space = spaces.Discrete(len(self.action_types))
        self.observation_space = spaces.Box(self.SPOT_vals_mins, self.SPOT_vals_maxs)
        self.reset()

    def reset(self, seed=None):
        #step 0
        self.step = 0
        self.start_buy_index = -1
        self.end_buy_index = -1
        #Use random starting point
        self.random_start_index = np.random.randint(low=0, high=(len(self.SPOT_vals)-self.max_trading_days))
        #Zero-init trade transaction info for all steps
        self.trading_transactions = pd.DataFrame(columns=gut.get_trading_bt_columns(), index=range(self.steps))
        obs, done = self.take_obs_step()
        return obs, {}

    def take_obs_step(self):
        #New observation
        obs = self.SPOT_vals.iloc[self.random_start_index + self.step].values
        self.step += 1
        done = self.step > self.steps
        return obs, done

    def take_trade_action_step(self, action):
        reward = 0
        trade_step = (self.random_start_index + self.step - 1)

        #Save the action
        self.trading_transactions['Action'][trade_step] = self.action_types[action]
        #Calculate reward for the action
        if (action == 0): #Only check reward when selling
            if (self.start_buy_index >= 0):
                cost = self.trading_transactions['Price'][self.start_buy_index:(self.end_buy_index+1)].sum()
                quantity = self.self.trading_transactions['Quantity'][self.start_buy_index:(self.end_buy_index+1)].sum()
                sell_amount = quantity*self.prices[trade_step]
                profit = (((sell_amount - cost)*100)/cost)
                reward = profit
                self.trading_transactions['Price'][trade_step] = round(self.prices[trade_step], 3)
                self.trading_transactions['Quantity'][trade_step] = quantity
                self.start_buy_index = -1
                self.end_buy_index = -1
        else:
            if (action == 2):
                #Buy side bookkeeping
                if (self.start_buy_index < 0):
                    self.start_buy_index = trade_step

                self.trading_transactions['Price'][trade_step] = round(self.prices[trade_step], 3)
                self.trading_transactions['Quantity'][trade_step] = 1
                self.end_buy_index = trade_step

        #Get new observation
        obs, done = self.take_obs_step()

        return obs, reward, done

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
        #Need min/max for gymnasium
        self.SPOT_vals_mins = np.array(self.SPOT_vals.min())
        self.SPOT_vals_maxs = np.array(self.SPOT_vals.max())

        #Basic action types
        self.action_types = ['Sell', 'Hold', 'Buy']

#SPOT RL trading agent that interacts with SPOT trading
class SPOT_agent():
    def __init__(self):
        self.gamma = 0.98
        self.epsilon_start = 0.98
        self.epsilon_end = 0.01

    def save_state_transitions(self, curr_state, action, reward, next_state, done):
        return

    def epsilon_greedy_policy(self, state):
        return

def main():
    tsymbol = sys.argv[1]
    try:
        max_trading_days = int(sys.argv[2])
    except:
        mtdpy, mtd5y = gut.get_min_trading_days()
        max_trading_days = (mtd5y - mtdpy)

    register(id='SPOT_trading', entry_point='gammath_spot_rl_gym_env:SPOT_environment', max_episode_steps=None)
    spot_trading_env = gym.make('SPOT_trading', tsymbol=tsymbol, max_trading_days=max_trading_days)
    spot_trading_agent = SPOT_agent()

    max_episodes = 1000

    #Training loop
    for episode_num in range(max_episodes):
        #Reset environment for new episodes
        spot_trading_env.env.unwrapped.reset()
        #Get initial state
        curr_state, done = spot_trading_env.env.unwrapped.take_obs_step()
        while not done:
            #Get action from policy. TBD
            action = 0
            #Get reward and observation of next state
            next_state, reward, done = spot_trading_env.env.unwrapped.take_trade_action_step(action)
            #Save transition TBD
            spot_trading_agent.save_state_transitions(curr_state, action, reward, next_state, done)
            curr_state = next_state

if __name__ == '__main__':
    main()
