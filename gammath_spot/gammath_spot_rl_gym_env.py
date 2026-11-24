# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-Present, Salyl Bhagwat, Gammath Works
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
__copyright__ = 'Copyright (c) 2021-Present, Salyl Bhagwat, Gammath Works'

import argparse
import os
import sys
import pandas as pd
import numpy as np
from collections import deque
from random import sample
import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register
#Tensorflow shows default messages depending on GPU that may not exist on the system
#Need to disable those logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
#Specifying input_shape in first layer is resulting in warning so using Input object to specify input shape explicitly
from tensorflow.keras import Input
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut


#This is a work-in-progress. A lot will change before it is usable
#Default values to cover broadest variety of stocks.
#Should be fine tuned for specific characteristics
mtdpy, _ = gut.get_min_trading_days()
MIN_PREMIUM_LEVEL = -0.5
NEUTRAL_LEVEL = 0.0
MIN_DISCOUNT_LEVEL = 0.5
MAX_TRADING_DAYS = (mtdpy << 1)
#Trading profiles (similar to backtesting except the term)
trading_profiles = ('medium_risk', 'high_risk')

def build_rules(prices, weighted_gscores):
    n = len(weighted_gscores)
    buy_zone = np.zeros(n, dtype=bool)
    sell_zone = np.zeros(n, dtype=bool)
    trading_at_discount_array = np.zeros(n, dtype=bool)
    trading_at_premium_array = np.zeros(n, dtype=bool)

    trading_at_discount = False
    trading_at_premium = False

    for time_step in range(mtdpy, n):
        weighted_gscore = weighted_gscores[time_step]
        if (weighted_gscore >= MIN_DISCOUNT_LEVEL):
            trading_at_discount = True
        elif (weighted_gscore <= NEUTRAL_LEVEL):
            trading_at_discount = False

        if (weighted_gscore <= MIN_PREMIUM_LEVEL):
            trading_at_premium = True
        elif (weighted_gscore >= NEUTRAL_LEVEL):
            trading_at_premium = False

        if (time_step > mtdpy):
            price_rising = (prices[time_step] >= prices[time_step-1])
            price_falling = (prices[time_step] < prices[time_step-1])
        else:
            price_rising = False
            price_falling = False

        trading_at_discount_array[time_step] = trading_at_discount
        trading_at_premium_array[time_step] = trading_at_premium

        buy_zone[time_step] = (trading_at_discount and (weighted_gscore < MIN_DISCOUNT_LEVEL) and price_rising)
        sell_zone[time_step] = (trading_at_premium and (weighted_gscore > MIN_PREMIUM_LEVEL) and price_falling)

    return buy_zone, sell_zone, trading_at_discount_array, trading_at_premium_array

#Environment that is compatible with Gymnasium
class SPOT_environment(gym.Env):
    metadata = {'render_modes': []}

    def __init__(self, tsymbol, risk_appetite):
        if (risk_appetite not in trading_profiles):
            raise ValueError(f'Unsupported trading profile: {risk_appetite}')

        self.risk_appetite = risk_appetite
        self.ticker = tsymbol
        self.min_start_index, _ = gut.get_min_trading_days()
        self.max_trading_days = MAX_TRADING_DAYS #2 years to give room for gScore cycles
        self.steps = self.max_trading_days
        self.random_start_index = 0
        self.self_buy_index = -1
        self.init_SPOT_RL_env_data(tsymbol)
        self.action_space = spaces.Discrete(len(self.action_types))
        self.observation_space = spaces.Box(self.SPOT_vals_mins, self.SPOT_vals_maxs, dtype=np.float32)
        self.total_transactions_so_far = 0
        self.reset()

    def reset(self, seed=None, options=None):
        #step 0
        self.curr_step = 0
        self.start_buy_index = -1
        #Use random starting point
        self.random_start_index = np.random.randint(low=self.min_start_index, high=(len(self.SPOT_vals)-self.max_trading_days))

        #reset trade transactions for episode
        self.trading_transactions = []

        obs, _ = self.take_obs_step()
        info = {'valid_actions': self.get_valid_actions()}
        return obs, info

    def take_obs_step(self):
        #New observation
        new_obs = self.SPOT_vals.iloc[self.random_start_index + self.curr_step].values
        have_bought = 1.0 if (self.start_buy_index >= 0) else 0.0
        obs = np.append(new_obs, have_bought).astype(np.float32)
        self.curr_step += 1
        done = (self.curr_step > (self.steps - 1))
        return obs, done

    def get_valid_actions(self):
        idx = (self.random_start_index + self.curr_step - 1)
        buy_valid = bool(self.buy_zone[idx])
        sell_valid = bool(self.sell_zone[idx] and (self.start_buy_index >= 0))
        #Buy valid, Hold valid, Sell valid
        return np.array([buy_valid, True, sell_valid], dtype=bool)


    def step(self, action):
        reward = 0
        trade_step = (self.random_start_index + self.curr_step - 1)

        #Rule based action
        if (not self.get_valid_actions()[action]):
            action = self.action_types.index('Hold')

        #Save the action (exclude saving hold actions)
        #Calculate reward for the action
        if (self.action_types[action] == 'Sell'): #Only check reward when selling
            if (self.start_buy_index >= 0):
                quantity, reward = self.get_rewards(trade_step)
                self.trading_transactions.append({'Date': self.Dates[trade_step], 'Action': self.action_types[action], 'Price': round(self.prices[trade_step], 3), 'Quantity': quantity})
                self.start_buy_index = -1
        else:
            if (self.action_types[action] == 'Buy'):
                #Buy side bookkeeping
                if (self.start_buy_index < 0):
                    self.start_buy_index = self.total_transactions_so_far

                self.trading_transactions.append({'Action': self.action_types[action], 'Date': self.Dates[trade_step], 'Price': round(self.prices[trade_step], 3), 'Quantity': 1})
        #Get new observation
        obs, done = self.take_obs_step()

        if (done and (reward == 0) and (self.start_buy_index >= 0)):
            #Did not have a corresponding sale for buy(s) at the end of the episode
            #Last observation step
            trade_step = (self.random_start_index + self.curr_step - 1)

            #Get the incomplete reward
            quantity, reward = self.get_rewards(trade_step)

        info = {'valid_actions': self.get_valid_actions(), 'episode_trade_transactions': self.trading_transactions if done else []}
        return obs, reward, done, False, info

    def render(self):
        #action not required
        pass

    def init_SPOT_RL_env_data(self, tsymbol):
        try:
            #Get gscores history
            df = pd.read_csv(f'tickers/{tsymbol}/{tsymbol}_micro_gscores.csv', index_col='Unnamed: 0')
        except:
            print(f'Micro gScores not found for {tsymbol}. Please run gScore historian tool before using this tool')
            exit(-1)

        try:
            #overall gScore using PCA
            weighted_gscore = pd.read_csv(f'tickers/{tsymbol}/{tsymbol}_weighted_gscores.csv', index_col='Unnamed: 0')
        except:
            print(f'Weighted gScores not found for {tsymbol}. Please run gScore historian tool before using this tool')
            exit(-1)

        #Filter out parts not needed for RL
        self.SPOT_vals = df.drop(['Date', 'Close', 'TPC5Y'], axis=1)

        if ((len(self.SPOT_vals) - self.max_trading_days) <= self.min_start_index):
            print(f'Insufficent history for {tsymbol} for {self.max_trading_days} since there are {self.min_start_index} warmup days')
            exit(-1)

        #Precompute rules
        self.buy_zone, self.sell_zone, self.trading_at_discount_array, self.trading_at_premium_array = build_rules(df.Close, weighted_gscore.Weighted_gScores)

        #Price history corresponding to steps
        self.prices = df.Close
        #Get the dates for testing
        self.Dates = df.Date
        #Need min/max for gymnasium
        self.SPOT_vals_mins = np.append(np.array(self.SPOT_vals.min()), 0.0).astype(np.float32)
        self.SPOT_vals_maxs = np.append(np.array(self.SPOT_vals.max()), 1.0).astype(np.float32)

        #Basic action types
        self.action_types = ('Buy', 'Hold', 'Sell')

        #Trade transactions
        self.trading_transactions = []

    def get_action_types(self):
        #Need to know the type of actions for logging agent transactions
        return self.action_types

    def get_rewards(self, trade_step):
        reward = 0
        current_trades = self.trading_transactions[self.start_buy_index:]
        cost = sum(float(t['Price']) for t in current_trades)
        quantity = sum(float(t['Quantity']) for t in current_trades)
        sell_amount = quantity*self.prices[trade_step]
        if (cost > 0):
            #Profit percentage
            profit_pct = (((sell_amount - cost)*100)/cost)

            #Keep the reward under +/- 1 with ample room to grow in either direction
            reward = profit_pct/1000

        return quantity, reward

    def get_episode_trade_transactions(self):
        return self.trading_transactions[:self.total_transactions_so_far]

#SPOT RL trading agent that interacts with SPOT trading
class SPOT_agent():
    def __init__(self, max_episodes, obs_dim, actions):
        #Long term focus
        self.gamma = 0.98
        #Start with exploration
        self.epsilon = 1.0
        #Linear decay for balancing exploitation
        self.epsilon_decay = self.epsilon/max_episodes
        self.max_actions = len(actions)
        self.action_types = actions
        self.bought = False
        self.saved_experience = deque(maxlen=5000000)
        self.batch_size = 1024
        self.obs_dim = obs_dim
        self.q_learner_network = self.build_model()
        self.q_target_network = self.build_model()
        self.q_target_network.trainable = False
        self.update_qtn_weights_from_qln_weights()
        self.steps = 0
        self.target_networks_update_interval_steps = 128

    def build_model(self):
        self.model = Sequential([Input(shape=self.obs_dim), Dense(units=32, activation='tanh', name='Dense_input'), Dense(units=32, activation='tanh', name='Dense_intermediate'), Dense(units=self.max_actions, name='Output')])

        #Compile the model with popular optimizer and MSE for regression
        self.model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        return self.model

    def update_qtn_weights_from_qln_weights(self):
        self.q_target_network.set_weights(self.q_learner_network.get_weights())

    def save_state_transitions(self, curr_state, action, reward, next_state, done, next_valid_actions):
        #next_valid_actions is rule based mask for next state
        self.saved_experience.append((curr_state, action, reward, next_state, done, next_valid_actions))
        return

    def replay_experience(self):
        #Barely tested
        saved_experience_len = len(self.saved_experience)
        if (saved_experience_len > self.batch_size):
            #Get iterator for corresponding iterables
            curr_batch = map(np.array, zip(*sample(self.saved_experience, self.batch_size)))
            curr_state, action, reward, next_state, not_done, next_valid_actions = curr_batch
            action = action.astype(int)
            next_valid_actions = next_valid_actions.astype(bool)

            #Use double deep q-learning (DDQN) algorithm
            #We want to decouple the estimation of action values from selection of actions

            #Estimate next q values in learning network
            ln_next_q_values = self.q_learner_network.predict_on_batch(next_state)

            #Rule based actions
            ln_next_q_values = np.where(next_valid_actions, ln_next_q_values, -np.inf)

            #Select best valid action in learning network
            ln_max_q_actions = np.argmax(ln_next_q_values, axis=1)

            #Estimate next q values in target network
            tn_next_q_values = self.q_target_network.predict_on_batch(next_state)

            indices = tf.range(self.batch_size)

            #Select target network's predicted q values for learner network's best valid actions
            temporal_diff_target_vals = tn_next_q_values[indices, ln_max_q_actions]

            #gamma and temporal diff not relevant if it is done
            target_vals = (reward + (self.gamma*temporal_diff_target_vals*not_done))

            ln_q_values = np.array(self.q_learner_network.predict_on_batch(curr_state))
            ln_q_values[indices, action] = target_vals

            #Check loss value for debugging
            loss = self.q_learner_network.train_on_batch(x=curr_state, y=ln_q_values)

        #Update target network weights at regular intervals
        if (not (self.steps % self.target_networks_update_interval_steps)):
            self.update_qtn_weights_from_qln_weights()
        return

    def update_epsilon(self):
        self.epsilon -= self.epsilon_decay

    def default_policy(self, state, valid_actions):
        q = np.array(self.q_learner_network(state, training=False))
        #enforce rule based actions
        q[:, ~valid_actions] = -np.inf

        #Get max q value index
        action = int(np.argmax(q, axis=1).squeeze())
        return action

    def epsilon_greedy_policy(self, state, valid_actions):
        #This can be updated to use backtesting profiles
        if (self.epsilon > np.random.rand()):
            #Pick a random action from valid actions only (rule based);
            action = int(np.random.choice(np.flatnonzero(valid_actions)))
        else:
            #this will still be arbitrary initially
            action = self.default_policy(state, valid_actions)

        #Update steps completed
        self.steps += 1

        return action

def spot_agent_training(tsymbol, path, risk_appetite):

    spot_trading_env = gym.make('SPOT_trading', tsymbol=tsymbol, risk_appetite=risk_appetite)

    max_episodes = 1000
    obs_dim = spot_trading_env.env.unwrapped.observation_space.shape
    action_types = spot_trading_env.env.unwrapped.get_action_types()
    spot_trading_agent = SPOT_agent(max_episodes=max_episodes, obs_dim=obs_dim, actions=action_types)

    #Create dataframe to save trade transactions across all episodes
    columns = list(gut.get_trading_bt_columns())
    columns.append('episode_num')
    columns.append('episode_reward')
    df_episodes_trade_transactions = pd.DataFrame(columns=columns, index=range(max_episodes*MAX_TRADING_DAYS))
    episodes_trade_transactions = []

    #Training loop
    for episode_num in range(max_episodes):
        #Reset environment for new episodes and get initial state
        curr_state, info = spot_trading_env.reset()
        #Valid actions from rules
        curr_valid_actions = info['valid_actions']
        episode_first_row = len(episodes_trade_transactions)
        curr_episode_rewards = 0
        done = False

        while not done:
            #Get action based on policy.
            action = spot_trading_agent.epsilon_greedy_policy(curr_state.reshape(-1, obs_dim[0]), curr_valid_actions)

            #Get reward and observation of next state
            next_state, reward, done, _, info = spot_trading_env.step(action)

            #Rule based acions for next state
            next_valid_actions = info['valid_actions']
 
            #Accumulate rewards per step
            curr_episode_rewards += reward

            #Save transition
            spot_trading_agent.save_state_transitions(curr_state, action, reward, next_state, (0.0 if done else 1.0), next_valid_actions)

            if done:
                #Get the trade transaction from this episode
                for tx in info['episode_trade_transactions']:
                    episodes_trade_transactions.append({'episode_num': episode_num, 'Date': tx['Date'], 'Action': tx['Action'], 'Price': tx['Price'], 'Quantity': tx['Quantity'], 'episode_reward': np.nan})

            #Replay experience
            spot_trading_agent.replay_experience()

            curr_state = next_state
            curr_valid_actions = next_valid_actions

        #Save rewards per episode for later reference (adjust back to show percentage gain/loss)
        if (len(episodes_trade_transactions) > episode_first_row):
            episodes_trade_transactions[-1]['episode_reward'] = round((curr_episode_rewards*1000), 3) #round it off to take less display space in CSV file

        #Update epsilon for next episode
        spot_trading_agent.update_epsilon()

    #Save episodes trade transactions and reward information for later reference, testing and debugging
    df_episodes_trade_transactions = pd.DataFrame(episodes_trade_transactions, columns=columns)
    df_episodes_trade_transactions.to_csv(path / f'{tsymbol}/{tsymbol}_rl_episodes_info_{risk_appetite}_profile.csv')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", help="A ticker symbol e.g. AAPL")
    args = parser.parse_args()
    tsymbol = args.ticker

    path = gut.get_tickers_dir()
    register(id='SPOT_trading', entry_point=f'{__name__}:SPOT_environment', max_episode_steps=None)

    #Do training for each trading profile
    for risk_appetite in trading_profiles:
        print(f'{tsymbol}: SPOT RL agent training for {risk_appetite} profile')
        spot_agent_training(tsymbol, path, risk_appetite)

if __name__ == '__main__':
    main()
