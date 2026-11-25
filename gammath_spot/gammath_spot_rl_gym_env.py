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
import json
import os
import sys
import time
import pandas as pd
import numpy as np
from collections import deque
from random import sample
import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register, registry
#Tensorflow shows default messages depending on GPU that may not exist on the system
#Need to disable those logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
#Specifying input_shape in first layer is resulting in warning so using Input object to specify input shape explicitly
from tensorflow.keras import Input
from tensorflow.keras.models import Sequential, load_model
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
#Most recent ~1 year is held out for testing (out-of-sample); everything before it is used for training
TEST_TRADING_DAYS = mtdpy
MAX_TRAINING_EPISODES = 1000
#Discount horizon in trading days (~3 months); effective horizon is 1/(1-GAMMA)
#Longer horizons (e.g. ~1 year) make DQN training less stable without additional stabilizers
GAMMA_HORIZON_DAYS = 63
GAMMA = 1 - (1/GAMMA_HORIZON_DAYS)   #~0.984
#Bump this when observation features, rules or network architecture change so saved models get retrained
RL_MODEL_VERSION = 1

#Trading profiles (similar to backtesting except the term)
trading_profiles = ('medium_risk', 'high_risk')

#Selling is allowed only at a profit, so a position may still be open at the end of a run
INCOMPLETE_NOTE = 'Sell not completed: no profitable sell signal by end of period (news/business conditions may not have allowed completion)'
#Fewer swings than this in gScores history makes swing timing statistics unreliable
MIN_RELIABLE_SWINGS = 3

class SPOTDataError(Exception):
    #Raised when a ticker's gScores data can't be used, so a watchlist run can skip it and continue
    pass

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

    def __init__(self, tsymbol, risk_appetite, max_cash=MAX_DOLLARS_PER_STOCK, train_end_date=None, test_days=TEST_TRADING_DAYS):
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
        self.init_train_test_split(train_end_date, test_days)
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
        if (options is not None) and ('start_index' in options):
            #Deterministic episode (testing/daily use) over [start_index, end_index)
            start_index = int(options['start_index'])
            end_index = int(options.get('end_index', len(self.SPOT_vals)))
            if ((start_index < self.min_start_index) or (end_index > len(self.SPOT_vals)) or ((end_index - start_index) < 2)):
                raise ValueError(f'Invalid episode range [{start_index}, {end_index}) for {self.ticker}')
            self.random_start_index = start_index
            self.steps = (end_index - start_index)
        else:
            #Training episode: random starting point such that the whole episode stays within training data
            self.random_start_index = int(self.np_random.integers(low=self.min_start_index, high=(self.train_end_index - self.max_trading_days + 1)))
            self.steps = self.max_trading_days

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

    def get_buy_quantity(self, idx):
        #Fibonacci based buy quantity (same as what step() would buy at idx)
        if (self.start_buy_index < 0):
            #First buy is fib(1)
            return 1

        buy_block_num = self.buy_block_num if self.buy_cycle[idx] else 1
        return min(gut.get_nth_fib(buy_block_num), (self.remaining_cash//self.prices[idx]))

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
        if (self.action_types[action] == 'Sell'):
            if (self.start_buy_index >= 0):
                #Gain was already rewarded day by day (mark-to-market) so selling itself has no extra reward
                quantity, avg_price, return_pct = self.get_position_return(trade_step)
                self.trading_transactions.append({'Date': self.Dates[trade_step], 'Action': self.action_types[action], 'Price': round(self.prices[trade_step], 3), 'Quantity': quantity, 'Avg_Price': round(avg_price, 3), 'Return_Pct': round(return_pct, 3), 'Profit': round(quantity*(self.prices[trade_step] - avg_price), 3), 'Days_Held': (trade_step - self.first_buy_step)})
                self.reset_position()
        else:
            if (self.action_types[action] == 'Buy'):
                #Buy side bookkeeping
                buy_q = self.get_buy_quantity(trade_step)
                if (self.start_buy_index < 0):
                    self.start_buy_index = len(self.trading_transactions)
                    self.first_buy_step = trade_step
                    #First buy is fib(1), so next buy uses fib(2)
                    self.buy_block_num = 2
                else:
                    self.buy_block_num += 1

                self.remaining_cash -= (buy_q*self.prices[trade_step])

                self.trading_transactions.append({'Action': self.action_types[action], 'Date': self.Dates[trade_step], 'Price': round(self.prices[trade_step], 3), 'Quantity': buy_q})

        #Get new observation
        obs, done = self.take_obs_step()

        #Mark-to-market reward: change in value of the position held into the next day
        next_step = (self.random_start_index + self.curr_step - 1)
        reward = self.get_mark_to_market_reward(trade_step, next_step)

        episode_trade_transactions = []
        if done:
            episode_trade_transactions = list(self.trading_transactions)
            if (self.start_buy_index >= 0):
                #No corresponding sale for buy(s) by the end of the episode: mark it incomplete with unrealized return
                quantity, avg_price, return_pct = self.get_position_return(next_step)
                episode_trade_transactions.append({'Date': self.Dates[next_step], 'Action': 'Incomplete', 'Price': round(self.prices[next_step], 3), 'Quantity': quantity, 'Avg_Price': round(avg_price, 3), 'Return_Pct': round(return_pct, 3), 'Profit': round(quantity*(self.prices[next_step] - avg_price), 3), 'Days_Held': (next_step - self.first_buy_step), 'Notes': INCOMPLETE_NOTE})

        info = {'valid_actions': self.get_valid_actions(), 'episode_trade_transactions': episode_trade_transactions}
        #Episode end is a time limit (data window), not a terminal state, so report it as truncated
        #so that learning keeps bootstrapping value beyond the last step
        return obs, reward, False, done, info

    def render(self):
        #action not required
        pass

    def init_SPOT_RL_env_data(self, tsymbol):
        path = gut.get_tickers_dir()
        try:
            #Get gscores history
            df = pd.read_csv(path / f'{tsymbol}/{tsymbol}_micro_gscores.csv', index_col='Unnamed: 0')
        except FileNotFoundError:
            raise SPOTDataError(f'Micro gScores not found for {tsymbol}. Please run gScore historian tool before using this tool')

        try:
            #overall gScore using PCA
            weighted_gscore = pd.read_csv(path / f'{tsymbol}/{tsymbol}_weighted_gscores.csv', index_col='Unnamed: 0')
        except FileNotFoundError:
            raise SPOTDataError(f'Weighted gScores not found for {tsymbol}. Please run gScore historian tool before using this tool')

        if (len(weighted_gscore) != len(df)):
            raise SPOTDataError(f'Micro and weighted gScores history lengths differ for {tsymbol}. Please rerun gScore historian tool')

        #Filter out parts not needed for RL
        self.SPOT_vals = df.drop(['Date', 'Close', 'TPC5Y'], axis=1)

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

    def init_train_test_split(self, train_end_date, test_days):
        n = len(self.SPOT_vals)
        if (train_end_date is None):
            #New split: hold out most recent test_days for testing
            self.train_end_index = (n - test_days)
        else:
            #gScores history is a rolling window so locate the split by date rather than index
            #Dates are in YYYY-MM-DD format so string ordering is chronological
            self.train_end_index = int(np.searchsorted(self.Dates, train_end_date, side='right'))

        if ((self.train_end_index <= self.min_start_index) or (self.train_end_index >= n)):
            raise SPOTDataError(f'Invalid train/test split for {self.ticker} (train end index {self.train_end_index}, history length {n})')

        #Last date used for training
        self.train_end_date = str(self.Dates[self.train_end_index-1])

    def has_sufficient_training_data(self):
        return ((self.train_end_index - self.min_start_index) >= self.max_trading_days)

    def get_feature_names(self):
        return list(self.SPOT_vals.columns) + ['have_bought']

    def get_action_types(self):
        #Need to know the type of actions for logging agent transactions
        return self.action_types

    def get_position_return(self, idx):
        #Quantity, average price and return percentage of current position at idx price
        if (self.start_buy_index < 0):
            return 0, 0.0, 0.0

        cost, quantity = self.get_position()
        if ((cost <= 0) or (quantity <= 0)):
            return 0, 0.0, 0.0

        return_pct = ((((quantity*self.prices[idx]) - cost)*100)/cost)
        return quantity, (cost/quantity), return_pct

    def get_mark_to_market_reward(self, curr_idx, next_idx):
        if (self.start_buy_index < 0):
            #In cash
            return 0.0

        cost, quantity = self.get_position()
        if (cost <= 0):
            return 0.0

        #Percentage change of position value relative to cost basis
        change_pct = ((quantity*(self.prices[next_idx] - self.prices[curr_idx])*100)/cost)

        #Same scale as profit_pct/1000 so that rewards over a buy->sell cycle add up to ~cycle profit_pct/1000
        #and stay under +/- 1 with ample room to grow in either direction
        return change_pct/1000

#SPOT RL trading agent that interacts with SPOT trading
class SPOT_agent():
    def __init__(self, max_episodes, obs_dim, actions, q_network=None):
        self.gamma = GAMMA
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
        #Use already trained network (inference) if provided
        self.q_learner_network = q_network if (q_network is not None) else self.build_model()
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

def get_model_paths(path, tsymbol, risk_appetite):
    model_file = path / f'{tsymbol}/{tsymbol}_spot_rl_{risk_appetite}.keras'
    meta_file = path / f'{tsymbol}/{tsymbol}_spot_rl_{risk_appetite}_meta.json'
    return model_file, meta_file

def make_env(tsymbol, risk_appetite, train_end_date=None, test_days=TEST_TRADING_DAYS):
    if ('SPOT_trading' not in registry):
        register(id='SPOT_trading', entry_point=f'{__name__}:SPOT_environment', max_episode_steps=None)
    return gym.make('SPOT_trading', tsymbol=tsymbol, risk_appetite=risk_appetite, train_end_date=train_end_date, test_days=test_days)

def load_saved_agent(tsymbol, path, risk_appetite, max_episodes=MAX_TRAINING_EPISODES, test_days=TEST_TRADING_DAYS):
    #Returns (agent, metadata) if a compatible saved model exists, else (None, None)
    model_file, meta_file = get_model_paths(path, tsymbol, risk_appetite)
    if ((not model_file.exists()) or (not meta_file.exists())):
        return None, None

    try:
        with open(meta_file) as f:
            meta = json.load(f)
    except (OSError, ValueError):
        print(f'{tsymbol}: Unreadable RL model metadata for {risk_appetite} profile; retraining')
        return None, None

    if (meta.get('model_version') != RL_MODEL_VERSION):
        print(f'{tsymbol}: Saved RL model for {risk_appetite} profile is from an older version; retraining')
        return None, None

    #Retrain if training settings changed since the saved model was trained
    if ((meta.get('max_episodes') != max_episodes) or (meta.get('test_days') != test_days)):
        print(f"{tsymbol}: Training settings changed for {risk_appetite} profile (episodes {meta.get('max_episodes')} -> {max_episodes}, test_days {meta.get('test_days')} -> {test_days}); retraining")
        return None, None

    #Make sure saved model is still compatible with current data (feature columns)
    spot_trading_env = make_env(tsymbol, risk_appetite, train_end_date=meta['train_end_date'])
    if (spot_trading_env.unwrapped.get_feature_names() != meta.get('features')):
        print(f'{tsymbol}: gScore features changed since RL model for {risk_appetite} profile was trained; retraining')
        return None, None

    #Inference only so optimizer state is not needed
    q_network = load_model(model_file, compile=False)
    obs_dim = spot_trading_env.unwrapped.observation_space.shape
    agent = SPOT_agent(max_episodes=1, obs_dim=obs_dim, actions=spot_trading_env.unwrapped.get_action_types(), q_network=q_network)
    #Inference only
    agent.epsilon = 0.0
    return agent, meta

def spot_agent_training(tsymbol, path, risk_appetite, max_episodes=MAX_TRAINING_EPISODES, test_days=TEST_TRADING_DAYS):

    spot_trading_env = make_env(tsymbol, risk_appetite, test_days=test_days)
    env = spot_trading_env.unwrapped

    if (not env.has_sufficient_training_data()):
        print(f'{tsymbol}: Insufficient history to train {risk_appetite} profile: need {env.max_trading_days} trading days after {env.min_start_index} warmup days before train end date {env.train_end_date}. Try a smaller --test_days')
        return None, None

    print(f'{tsymbol}: Training {risk_appetite} profile on data up to {env.train_end_date} ({max_episodes} episodes)')

    obs_dim = env.observation_space.shape
    action_types = env.get_action_types()
    spot_trading_agent = SPOT_agent(max_episodes=max_episodes, obs_dim=obs_dim, actions=action_types)

    #Create dataframe to save trade transactions across all episodes
    columns = list(gut.get_trading_bt_columns())
    columns.append('episode_num')
    columns.append('episode_reward')
    episodes_trade_transactions = []

    #Training loop (random episodes from training data only)
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
            next_state, reward, terminated, truncated, info = spot_trading_env.step(action)
            done = (terminated or truncated)

            #Rule based acions for next state
            next_valid_actions = info['valid_actions']
 
            #Accumulate rewards per step
            curr_episode_rewards += reward

            #Save transition
            #Only a true terminal state stops bootstrapping; time limit truncation still uses next state value
            spot_trading_agent.save_state_transitions(curr_state, action, reward, next_state, (0.0 if terminated else 1.0), next_valid_actions)

            if done:
                #Get the trade transaction from this episode
                for tx in info['episode_trade_transactions']:
                    episodes_trade_transactions.append({'episode_num': episode_num, 'Date': tx['Date'], 'Action': tx['Action'], 'Price': tx['Price'], 'Quantity': tx['Quantity'], 'Avg_Price': tx.get('Avg_Price', np.nan), 'Return_Pct': tx.get('Return_Pct', np.nan), 'Profit': tx.get('Profit', np.nan), 'Days_Held': tx.get('Days_Held', np.nan), 'Notes': tx.get('Notes', ''), 'episode_reward': np.nan})

            #Replay experience
            spot_trading_agent.replay_experience()

            curr_state = next_state
            curr_valid_actions = next_valid_actions

        #Save rewards per episode for later reference (adjust back to show approx. percentage gain/loss including unrealized)
        if (len(episodes_trade_transactions) > episode_first_row):
            episodes_trade_transactions[-1]['episode_reward'] = round((curr_episode_rewards*1000), 3) #round it off to take less display space in CSV file

        #Update epsilon for next episode
        spot_trading_agent.update_epsilon()

    #Save episodes trade transactions and reward information for later reference, testing and debugging
    df_episodes_trade_transactions = pd.DataFrame(episodes_trade_transactions, columns=columns)
    df_episodes_trade_transactions.to_csv(path / f'{tsymbol}/{tsymbol}_rl_episodes_info_{risk_appetite}_profile.csv')

    #Save trained model and metadata so subsequent runs don't need to retrain
    model_file, meta_file = get_model_paths(path, tsymbol, risk_appetite)
    spot_trading_agent.q_learner_network.save(model_file)
    meta = {'model_version': RL_MODEL_VERSION, 'ticker': tsymbol, 'risk_appetite': risk_appetite, 'train_end_date': env.train_end_date, 'max_episodes': max_episodes, 'test_days': test_days, 'features': env.get_feature_names(), 'trained_on': time.strftime('%Y-%m-%d %H:%M:%S')}
    with open(meta_file, 'w') as f:
        json.dump(meta, f, indent=2)

    print(f'{tsymbol}: Saved RL model for {risk_appetite} profile to {model_file}')

    #Inference only from here on
    spot_trading_agent.epsilon = 0.0
    return spot_trading_agent, meta

def measure_swings(buy_cycle, sell_cycle, start_index, end_index):
    #gScore swings have no fixed period (like an unaligned pendulum) so measure them from history.
    #Swing: first entry into buy cycle (discount zone) -> next entry into sell cycle (premium zone)
    swings = []
    swing_start = -1
    for t in range(max(start_index, 1), end_index):
        if (buy_cycle[t] and (not buy_cycle[t-1]) and (swing_start < 0)):
            swing_start = t
        if (sell_cycle[t] and (not sell_cycle[t-1]) and (swing_start >= 0)):
            swings.append(t - swing_start)
            swing_start = -1

    last = (end_index - 1)
    if buy_cycle[last]:
        current_cycle = 'Buy'
    elif sell_cycle[last]:
        current_cycle = 'Sell'
    else:
        current_cycle = 'Neutral'

    return {'Swings': len(swings),
            'Swing_Median_Days': (int(np.median(swings)) if swings else np.nan),
            'Swing_Min_Days': (min(swings) if swings else np.nan),
            'Swing_Max_Days': (max(swings) if swings else np.nan),
            'Swing_Sample': ('OK' if (len(swings) >= MIN_RELIABLE_SWINGS) else 'Low'),
            'Current_Cycle': current_cycle,
            #Days since current (not yet completed) swing started
            'Current_Swing_Days': ((last - swing_start) if (swing_start >= 0) else np.nan)}

def rules_only_policy(state, valid_actions):
    #Baseline without RL: act whenever the rules give a buy or sell signal (similar to backtester)
    if valid_actions[0]:
        return 0
    if valid_actions[2]:
        return 2
    return 1

def run_policy(spot_trading_env, start_index, end_index, policy, prefix):
    #Run a policy without learning over [start_index, end_index). The last day's action is not executed;
    #it is the suggestion for that day since the position on the last day depends on the preceding days.
    env = spot_trading_env.unwrapped
    curr_state, info = spot_trading_env.reset(options={'start_index': start_index, 'end_index': end_index})
    curr_valid_actions = info['valid_actions']
    done = False

    while not done:
        action = policy(curr_state, curr_valid_actions)
        curr_state, _, terminated, truncated, info = spot_trading_env.step(action)
        done = (terminated or truncated)
        curr_valid_actions = info['valid_actions']

    transactions = info['episode_trade_transactions']
    last_index = (end_index - 1)
    action_name = env.get_action_types()[policy(curr_state, curr_valid_actions)]
    quantity, avg_price, unrealized_pct = env.get_position_return(last_index)

    sells = [t for t in transactions if t['Action'] == 'Sell']
    incomplete = [t for t in transactions if t['Action'] == 'Incomplete']
    #Total profit in dollars (realized + unrealized) is used to compare policies since quantities differ
    total_profit = sum(t['Profit'] for t in (sells + incomplete))

    stats = {f'{prefix}_Action': action_name,
             f'{prefix}_Quantity': (env.get_buy_quantity(last_index) if action_name == 'Buy' else (quantity if action_name == 'Sell' else 0)),
             f'{prefix}_Trades': len(sells),
             f'{prefix}_Avg_Trade_Pct': (round(np.mean([t['Return_Pct'] for t in sells]), 3) if sells else np.nan),
             f'{prefix}_Avg_Days_Held': (round(np.mean([t['Days_Held'] for t in sells]), 1) if sells else np.nan),
             f'{prefix}_Realized_Pct': round(sum(t['Return_Pct'] for t in sells), 3),
             f'{prefix}_Position': ('Incomplete' if incomplete else 'None'),
             f'{prefix}_Position_Qty': quantity,
             f'{prefix}_Avg_Price': round(avg_price, 3),
             f'{prefix}_Unrealized_Pct': round(unrealized_pct, 3),
             f'{prefix}_Position_Days': (incomplete[0]['Days_Held'] if incomplete else np.nan),
             f'{prefix}_Profit': round(total_profit, 3)}

    return stats, [dict(t, Policy=prefix) for t in transactions]

def spot_agent_run(tsymbol, path, risk_appetite, agent, meta):
    #Out-of-sample test over all data after the training period for both the trained agent (greedy, no learning)
    #and the rules-only baseline. Also gives suggestions for the latest trading day.
    spot_trading_env = make_env(tsymbol, risk_appetite, train_end_date=meta['train_end_date'])
    env = spot_trading_env.unwrapped
    obs_dim = env.observation_space.shape
    start_index = env.train_end_index
    end_index = len(env.SPOT_vals)
    last_index = (end_index - 1)

    agent_policy = lambda state, valid_actions: agent.default_policy(state.reshape(-1, obs_dim[0]), valid_actions)
    agent_stats, agent_transactions = run_policy(spot_trading_env, start_index, end_index, agent_policy, 'Agent')
    rules_stats, rules_transactions = run_policy(spot_trading_env, start_index, end_index, rules_only_policy, 'Rules')

    profit_diff = (agent_stats['Agent_Profit'] - rules_stats['Rules_Profit'])
    if (abs(profit_diff) < 0.01):
        agent_vs_rules = 'Same'
    else:
        agent_vs_rules = 'Better' if (profit_diff > 0) else 'Worse'

    last_price = env.prices[last_index]
    buy_and_hold_pct = ((last_price - env.prices[start_index])*100/env.prices[start_index])

    #Swing timing over the whole usable history (descriptive only; not used for training)
    swing_stats = measure_swings(env.buy_cycle, env.sell_cycle, (mtdpy + 2), end_index)

    summary = {'Ticker': tsymbol, 'Profile': risk_appetite, 'Date': str(env.Dates[last_index]), 'Price': round(last_price, 3),
               'Agent_Action': agent_stats['Agent_Action'], 'Agent_Quantity': agent_stats['Agent_Quantity'],
               'Rules_Action': rules_stats['Rules_Action'], 'Rules_Quantity': rules_stats['Rules_Quantity'],
               'Agent_vs_Rules': agent_vs_rules}
    summary.update({k: v for k, v in agent_stats.items() if k not in summary})
    summary.update({k: v for k, v in rules_stats.items() if k not in summary})
    summary.update({'Buy_Hold_Pct': round(buy_and_hold_pct, 3)})
    summary.update(swing_stats)
    summary.update({'Test_Start': str(env.Dates[start_index]), 'Test_Days': (end_index - start_index), 'Train_End': meta['train_end_date']})

    pd.DataFrame(agent_transactions + rules_transactions, columns=['Policy', 'Date', 'Action', 'Price', 'Quantity', 'Avg_Price', 'Return_Pct', 'Profit', 'Days_Held', 'Notes']).to_csv(path / f'{tsymbol}/{tsymbol}_rl_test_transactions_{risk_appetite}_profile.csv')
    return summary

def format_policy_line(summary, prefix):
    s = summary
    line = f"{prefix}: {s[prefix+'_Trades']} trades"
    if s[prefix+'_Trades']:
        line += f", avg {s[prefix+'_Avg_Trade_Pct']}% in {s[prefix+'_Avg_Days_Held']} days, realized {s[prefix+'_Realized_Pct']}%"
    if (s[prefix+'_Position'] == 'Incomplete'):
        line += f" | incomplete {s[prefix+'_Position_Qty']} @ {s[prefix+'_Avg_Price']} ({s[prefix+'_Unrealized_Pct']}% unrealized, {s[prefix+'_Position_Days']} days)"
    line += f" | P&L ${s[prefix+'_Profit']}"
    return line

def format_action(summary, prefix):
    action = summary[prefix+'_Action']
    return action if (action == 'Hold') else f"{action} {summary[prefix+'_Quantity']}"

def print_summary(summary, print_swings):
    s = summary
    if print_swings:
        line = f"{s['Ticker']} swings in gScores history: {s['Swings']}"
        if s['Swings']:
            line += f" (median {s['Swing_Median_Days']} days, range {s['Swing_Min_Days']}-{s['Swing_Max_Days']})"
        if (s['Swing_Sample'] == 'Low'):
            line += ' [low sample]'
        line += f" | current: {s['Current_Cycle']} cycle"
        if not pd.isna(s['Current_Swing_Days']):
            line += f", swing in progress for {s['Current_Swing_Days']} days"
        print(line)

    print(f"{s['Ticker']} [{s['Profile']}] {s['Date']} @ {s['Price']}: agent {format_action(s, 'Agent')} | rules {format_action(s, 'Rules')}")
    print(f"  Test {s['Test_Start']}..{s['Date']} ({s['Test_Days']} days), agent vs rules: {s['Agent_vs_Rules']}, buy & hold {s['Buy_Hold_Pct']}%")
    print('  ' + format_policy_line(s, 'Agent'))
    print('  ' + format_policy_line(s, 'Rules'))

def main():
    parser = argparse.ArgumentParser(description='Gammath SPOT RL trading agent. For each stock in the watchlist, trains (once) on older gScores history, tests on the most recent held-out period and recommends an action for the latest trading day.')
    parser.add_argument("watchlist", help="A CSV file as watchlist. e.g. sample_watchlist.csv")
    parser.add_argument("--retrain", action='store_true', help="Force retraining even if a saved model exists")
    parser.add_argument("--episodes", type=int, default=MAX_TRAINING_EPISODES, help=f"Training episodes (default {MAX_TRAINING_EPISODES})")
    parser.add_argument("--test_days", type=int, default=TEST_TRADING_DAYS, help=f"Most recent trading days held out for testing when (re)training (default {TEST_TRADING_DAYS})")
    args = parser.parse_args()

    try:
        watch_list = pd.read_csv(args.watchlist)
        symbols = [str(sym).strip().upper() for sym in watch_list['Symbol'].dropna()]
    except (OSError, ValueError, KeyError):
        print('ERROR: Failed to read watchlist. See sample_watchlist.csv for example')
        sys.exit(-1)

    path = gut.get_tickers_dir()
    summaries = []

    print('\nStart Time: ', time.strftime('%x %X'), '\n')

    for tsymbol in symbols:
        ticker_summaries = []
        try:
            for risk_appetite in trading_profiles:
                agent, meta = (None, None) if args.retrain else load_saved_agent(tsymbol, path, risk_appetite, max_episodes=args.episodes, test_days=args.test_days)

                if (agent is None):
                    agent, meta = spot_agent_training(tsymbol, path, risk_appetite, max_episodes=args.episodes, test_days=args.test_days)
                    if (agent is None):
                        continue
                else:
                    print(f'{tsymbol}: Using saved RL model for {risk_appetite} profile (trained on data up to {meta["train_end_date"]})')

                summary = spot_agent_run(tsymbol, path, risk_appetite, agent, meta)
                #Swing timing doesn't depend on profile so print it once per ticker
                print_summary(summary, print_swings=(not ticker_summaries))
                ticker_summaries.append(summary)
        except SPOTDataError as e:
            print(f'{tsymbol}: Skipping. {e}')

        if ticker_summaries:
            pd.DataFrame(ticker_summaries).to_csv(path / f'{tsymbol}/{tsymbol}_rl_signals.csv', index=False)
            summaries.extend(ticker_summaries)

    #Watchlist level summary for daily review e.g. tickers/sample_watchlist_rl_signals.csv
    if summaries:
        watchlist_name = os.path.splitext(os.path.basename(args.watchlist))[0]
        pd.DataFrame(summaries).to_csv(path / f'{watchlist_name}_rl_signals.csv', index=False)

    print('\nEnd Time: ', time.strftime('%x %X'), '\n')

if __name__ == '__main__':
    main()
