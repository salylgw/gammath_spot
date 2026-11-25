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
MAX_DOLLARS_PER_STOCK = 10000

#Trading profiles (similar to backtesting except the term)
trading_profiles = ('medium_risk', 'high_risk')

def build_rules(df, weighted_gscores, risk_appetite):
    prices = np.asarray(df.Close, dtype=float)
    lsr = np.asarray(df.LSR, dtype=float)
    cecs = np.asarray(df.CECS, dtype=float)
    w_gscores = np.asarray(weighted_gscores, dtype=float)
    n = len(weighted_gscores)
    buy_signal = np.zeros(n, dtype=bool)
    sell_signal = np.zeros(n, dtype=bool)
    buy_cycle = np.zeros(n, dtype=bool)
    sell_cycle = np.zeros(n, dtype=bool)

    high_risk = (risk_appetite == 'high_risk')

    marked_for_buy = False
    marked_for_sell = False

    for time_step in range(mtdpy+2, n):
        weighted_gscore = w_gscores[time_step]
        if (weighted_gscore >= MIN_DISCOUNT_LEVEL) or (marked_for_buy and (weighted_gscore >= NEUTRAL_LEVEL)):
            marked_for_buy = True
            marked_for_sell = False
        else:
            marked_for_buy = False

        if (weighted_gscore <= MIN_PREMIUM_LEVEL):
            marked_for_sell = True

        buy_cycle[time_step] = marked_for_buy
        sell_cycle[time_step] = marked_for_sell

        single_day_rising = (prices[time_step] > prices[time_step-1])
        consec_two_days_rising = (single_day_rising and (prices[time_step-1] > prices[time_step-2]))
        single_day_falling = (prices[time_step] < prices[time_step-1])
        consec_two_days_falling = (single_day_falling and (prices[time_step-1] < prices[time_step-2]))

        buy_signal[time_step] = (marked_for_buy and ((single_day_rising and high_risk) or (consec_two_days_rising and (not high_risk))) and (cecs[time_step] >= 0.5))
        sell_signal[time_step] = (marked_for_sell and ((lsr[time_step] <= -0.5) or (cecs[time_step] <= -0.5)) and ((single_day_falling and (not high_risk)) or (consec_two_days_falling and high_risk)))

    return buy_signal, sell_signal, buy_cycle, sell_cycle

#Environment that is compatible with Gymnasium
class SPOT_environment(gym.Env):
    metadata = {'render_modes': []}

    def __init__(self, tsymbol, risk_appetite, max_cash=MAX_DOLLARS_PER_STOCK):
        if (risk_appetite not in trading_profiles):
            raise ValueError(f'Unsupported trading profile: {risk_appetite}')

        self.risk_appetite = risk_appetite
        self.max_cash = max_cash
        self.remaining_cash = max_cash
        self.ticker = tsymbol
        self.min_start_index, _ = gut.get_min_trading_days()
        self.max_trading_days = MAX_TRADING_DAYS #2 years to give room for gScore cycles
        self.steps = self.max_trading_days
        self.random_start_index = 0
        self.init_SPOT_RL_env_data(tsymbol)
        self.action_space = spaces.Discrete(len(self.action_types))
        self.observation_space = spaces.Box(self.SPOT_vals_mins, self.SPOT_vals_maxs, dtype=np.float32)
        self.reset_position()

    def reset(self, seed=None, options=None):
        #Seed gymnasium's RNG (self.np_random) for reproducibility
        super().reset(seed=seed)

        #step 0
        self.curr_step = 0
        #Reset position, cash and buy block for new episode
        self.reset_position()
        #Use random starting point
        self.random_start_index = int(self.np_random.integers(low=self.min_start_index, high=(len(self.SPOT_vals)-self.max_trading_days)))

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

    def reset_position(self):
        self.start_buy_index = -1
        self.first_buy_step = -1
        self.buy_block_num = 1
        self.remaining_cash = self.max_cash

    def get_position(self):
        current_trades = self.trading_transactions[self.start_buy_index:]
        cost = sum(float(t['Price'])*float(t['Quantity']) for t in current_trades)
        quantity = sum(float(t['Quantity']) for t in current_trades)
        return cost, quantity

    def position_allows_sell(self, idx, cost, quantity):
        price = self.prices[idx]
        total_cash = (quantity*price)

        if (cost >= total_cash):
            return False
        else:
            return True

    def get_valid_actions(self):
        idx = (self.random_start_index + self.curr_step - 1)
        buy_valid = bool(self.buy_signal[idx] and (self.remaining_cash >= self.prices[idx]))
        sell_valid = False

        if (self.start_buy_index >= 0):
            cost, quantity = self.get_position()
            if (self.prices[idx] > (cost/quantity)):
                buy_valid = False

            sell_valid = bool(self.sell_signal[idx] and (self.position_allows_sell(idx, cost, quantity)))

        #Buy valid, Hold valid, Sell valid
        return np.array([buy_valid, True, sell_valid], dtype=bool)


    def step(self, action):
        reward = 0
        trade_step = (self.random_start_index + self.curr_step - 1)

        #Rule based action
        if (not self.get_valid_actions()[action]):
            action = self.action_types.index('Hold')

        if (not self.buy_cycle[trade_step]):
            self.buy_block_num = 1

        #Save the action (exclude saving hold actions)
        #Calculate reward for the action
        if (self.action_types[action] == 'Sell'): #Only check reward when selling
            if (self.start_buy_index >= 0):
                quantity, reward = self.get_rewards(trade_step)
                self.trading_transactions.append({'Date': self.Dates[trade_step], 'Action': self.action_types[action], 'Price': round(self.prices[trade_step], 3), 'Quantity': quantity})
                self.reset_position()
        else:
            if (self.action_types[action] == 'Buy'):
                #Buy side bookkeeping
                if (self.start_buy_index < 0):
                    self.start_buy_index = len(self.trading_transactions)
                    self.first_buy_step = trade_step
                    #First buy is fib(1), so next buy uses fib(2)
                    buy_q = 1
                    self.buy_block_num = 2
                else:
                    buy_q = min(gut.get_nth_fib(self.buy_block_num), (self.remaining_cash//self.prices[trade_step]))
                    self.buy_block_num += 1

                self.remaining_cash -= (buy_q*self.prices[trade_step])

                self.trading_transactions.append({'Action': self.action_types[action], 'Date': self.Dates[trade_step], 'Price': round(self.prices[trade_step], 3), 'Quantity': buy_q})

        #Get new observation
        obs, done = self.take_obs_step()

        if (done and (self.start_buy_index >= 0)):
            #Did not have a corresponding sale for buy(s) at the end of the episode
            #Last observation step
            trade_step = (self.random_start_index + self.curr_step - 1)

            #Get the incomplete (unrealized) reward
            _, reward = self.get_rewards(trade_step)

        info = {'valid_actions': self.get_valid_actions(), 'episode_trade_transactions': self.trading_transactions if done else []}
        return obs, reward, done, False, info

    def render(self):
        #action not required
        pass

    def init_SPOT_RL_env_data(self, tsymbol):
        path = gut.get_tickers_dir()
        try:
            #Get gscores history
            df = pd.read_csv(path / f'{tsymbol}/{tsymbol}_micro_gscores.csv', index_col='Unnamed: 0')
        except FileNotFoundError:
            print(f'Micro gScores not found for {tsymbol}. Please run gScore historian tool before using this tool')
            sys.exit(-1)

        try:
            #overall gScore using PCA
            weighted_gscore = pd.read_csv(path / f'{tsymbol}/{tsymbol}_weighted_gscores.csv', index_col='Unnamed: 0')
        except FileNotFoundError:
            print(f'Weighted gScores not found for {tsymbol}. Please run gScore historian tool before using this tool')
            sys.exit(-1)

        if (len(weighted_gscore) != len(df)):
            print(f'Micro and weighted gScores history lengths differ for {tsymbol}. Please rerun gScore historian tool')
            sys.exit(-1)

        #Filter out parts not needed for RL
        self.SPOT_vals = df.drop(['Date', 'Close', 'TPC5Y'], axis=1)

        if ((len(self.SPOT_vals) - self.max_trading_days) <= self.min_start_index):
            print(f'Insufficient history for {tsymbol} for {self.max_trading_days} trading days since there are {self.min_start_index} warmup days')
            sys.exit(-1)

        #Precompute rules
        self.buy_signal, self.sell_signal, self.buy_cycle, self.sell_cycle = build_rules(df, weighted_gscore.Weighted_gScores, self.risk_appetite)

        #Price history corresponding to steps
        self.prices = np.asarray(df.Close, dtype=float)
        #Get the dates for testing
        self.Dates = np.asarray(df.Date)
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
        cost, quantity = self.get_position()
        sell_amount = quantity*self.prices[trade_step]
        if (cost > 0):
            #Profit percentage
            profit_pct = (((sell_amount - cost)*100)/cost)

            #Keep the reward under +/- 1 with ample room to grow in either direction
            reward = profit_pct/1000

        return quantity, reward

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

            indices = np.arange(self.batch_size)

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
    obs_dim = spot_trading_env.unwrapped.observation_space.shape
    action_types = spot_trading_env.unwrapped.get_action_types()
    spot_trading_agent = SPOT_agent(max_episodes=max_episodes, obs_dim=obs_dim, actions=action_types)

    #Create dataframe to save trade transactions across all episodes
    columns = list(gut.get_trading_bt_columns())
    columns.append('episode_num')
    columns.append('episode_reward')
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
