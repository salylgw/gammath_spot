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
        self.total_transactions_so_far = 0
        self.reset()

    def reset(self, seed=None):
        #step 0
        self.step = 0
        self.start_buy_index = -1
        #Use random starting point
        self.random_start_index = np.random.randint(low=0, high=(len(self.SPOT_vals)-self.max_trading_days))

        #Zero-init trade transaction info for all steps
        for i in range(self.total_transactions_so_far):
            self.trading_transactions.loc[i, "Date"] = ''
            self.trading_transactions.loc[i, "Action"] = ''
            self.trading_transactions.loc[i, "Price"] = 0.0
            self.trading_transactions.loc[i, "Quantity"] = 0

        self.total_transactions_so_far = 0
        obs, done = self.take_obs_step()
        return obs, done

    def take_obs_step(self):
        #New observation
        obs = self.SPOT_vals.iloc[self.random_start_index + self.step].values
        self.step += 1
        done = (self.step > (self.steps - 1))
        return obs, done

    def take_trade_action_step(self, action):
        reward = 0
        trade_step = (self.random_start_index + self.step - 1)

        #Save the action (exclude saving hold actions)
        #Calculate reward for the action
        if (self.action_types[action] == 'Sell'): #Only check reward when selling
            if (self.start_buy_index >= 0):
                quantity, reward = self.get_rewards(trade_step)
                self.trading_transactions.loc[self.total_transactions_so_far, "Date"] = self.Dates[trade_step]
                self.trading_transactions.loc[self.total_transactions_so_far, "Action"] = self.action_types[action]
                self.trading_transactions.loc[self.total_transactions_so_far, "Price"] = round(self.prices[trade_step], 3)
                self.trading_transactions.loc[self.total_transactions_so_far, "Quantity"] = quantity
                self.total_transactions_so_far += 1
                self.start_buy_index = -1
        else:
            if (self.action_types[action] == 'Buy'):
                #Buy side bookkeeping
                if (self.start_buy_index < 0):
                    self.start_buy_index = self.total_transactions_so_far

                self.trading_transactions.loc[self.total_transactions_so_far, "Action"] = self.action_types[action]
                self.trading_transactions.loc[self.total_transactions_so_far, "Date"] = self.Dates[trade_step]
                self.trading_transactions.loc[self.total_transactions_so_far, "Price"] = round(self.prices[trade_step], 3)
                self.trading_transactions.loc[self.total_transactions_so_far, "Quantity"] = 1
                self.total_transactions_so_far += 1

        #Get new observation
        obs, done = self.take_obs_step()

        if (done and (reward == 0) and (self.start_buy_index >= 0)):
            #Did not have a corresponding sale for buy(s) at the end of the episode
            #Last observation step
            trade_step = (self.random_start_index + self.step - 1)

            #Get the incomplete reward
            quantity, reward = self.get_rewards(trade_step)

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
        #Get the dates for testing
        self.Dates = df.Date
        #Need min/max for gymnasium
        self.SPOT_vals_mins = np.array(self.SPOT_vals.min())
        self.SPOT_vals_maxs = np.array(self.SPOT_vals.max())

        #Basic action types
        self.action_types = ('Buy', 'Hold', 'Sell')

        #Trade transactions
        self.trading_transactions = pd.DataFrame(columns=gut.get_trading_bt_columns(), index=range(self.steps))

    def get_action_types(self):
        #Need to know the type of actions for logging agent transactions
        return self.action_types

    def get_rewards(self, trade_step):
        reward = 0
        cost = self.trading_transactions.loc[self.start_buy_index:self.total_transactions_so_far, "Price"].sum()
        quantity = self.trading_transactions.loc[self.start_buy_index:self.total_transactions_so_far, "Quantity"].sum()
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

    def save_state_transitions(self, curr_state, action, reward, next_state, done):
        self.saved_experience.append((curr_state, action, reward, next_state, done))
        return

    def replay_experience(self):
        #Barely tested
        saved_experience_len = len(self.saved_experience)
        if (saved_experience_len > self.batch_size):
            #Get iterator for corresponding iterables
            curr_batch = map(np.array, zip(*sample(self.saved_experience, self.batch_size)))
            curr_state, action, reward, next_state, not_done = curr_batch

            #Use double deep q-learning (DDQN) algorithm
            #We want to decouple the estimation of action values from selection of actions

            #Estimate next q values in learning network
            ln_next_q_values = self.q_learner_network.predict_on_batch(next_state)

            #Select max values in learning network
            ln_max_q_values = np.argmax(ln_next_q_values, axis=1).squeeze()

            #Estimate next q values in target network
            tn_next_q_values = self.q_target_network.predict_on_batch(next_state)

            indices = tf.range(self.batch_size)

            #Select target network's predicted q values for learner network's max q values
            temporal_diff_target_vals = tf.gather_nd(tn_next_q_values, tf.stack((indices, tf.cast(ln_max_q_values, tf.int32)), axis=1))

            #gamma and temporal diff not relevant if it is done
            target_vals = (reward + (self.gamma*temporal_diff_target_vals*not_done))

            ln_q_values = self.q_learner_network.predict_on_batch(curr_state)
            ln_q_values[indices, action] = target_vals

            #Check loss value for debugging
            loss = self.q_learner_network.train_on_batch(x=curr_state, y=ln_q_values)

        #Update target network weights at regular intervals
        if (not (self.steps % self.target_networks_update_interval_steps)):
            self.update_qtn_weights_from_qln_weights()
        return

    def update_epsilon(self):
        self.epsilon -= self.epsilon_decay

    def default_policy(self, state):
        q = self.q_learner_network.predict(state)
        #Get max q value index
        action = np.argmax(q, axis=1).squeeze()
        return action

    def epsilon_greedy_policy(self, state):
        #This can be updated to use backtesting profiles
        if (self.epsilon > np.random.rand()):
            #Pick a random action;
            if self.bought:
                max_actions = self.max_actions
            else:
                #Only buy or hold are valid actions
                #If there is sell before buy then there won't be any reward
                max_actions = (self.max_actions-1)

            action = np.random.choice(max_actions)
        else:
            #this will still be arbitrary initially
            action = self.default_policy(state)

        #Set the flag for choosing valid action
        if (self.action_types[action] == 'Buy'):
            self.bought = True
        elif (self.action_types[action] == 'Sell'):
            self.bought = False

        #Update steps completed
        self.steps += 1

        return action

def main():
    tsymbol = sys.argv[1]
    mtdpy, mtd5y = gut.get_min_trading_days()

    try:
        max_trading_days = int(sys.argv[2])
        if ((max_trading_days <= 0) or (max_trading_days >= mtd5y)):
            print(f'Max trading days must be between 1 and {mtd5y-1}. Exiting')
            return
    except:
        print(f'Max trading days not specified. Setting it to approximately 4 years')
        max_trading_days = (mtd5y - mtdpy)

    path = gut.get_tickers_dir()
    register(id='SPOT_trading', entry_point=f'{__name__}:SPOT_environment', max_episode_steps=None)

    spot_trading_env = gym.make('SPOT_trading', tsymbol=tsymbol, max_trading_days=max_trading_days)

    max_episodes = 1000
    obs_dim = spot_trading_env.env.unwrapped.observation_space.shape
    action_types = spot_trading_env.env.unwrapped.get_action_types()
    spot_trading_agent = SPOT_agent(max_episodes=max_episodes, obs_dim=obs_dim, actions=action_types)

    #Create dataframe to save trade transactions across all episodes
    columns = list(gut.get_trading_bt_columns())
    columns.append('episode_num')
    columns.append('episode_reward')
    df_episodes_trade_transactions = pd.DataFrame(columns=columns, index=range(max_episodes*max_trading_days))
    total_trade_transaction_count = 0

    #Force eager execution (as opposed to graph execution) until the code is ready for optimization
    tf.data.experimental.enable_debug_mode()
    tf.config.run_functions_eagerly(True)

    #Training loop
    for episode_num in range(max_episodes):
        #Reset environment for new episodes and get initial state
        curr_state, done = spot_trading_env.env.unwrapped.reset()
        curr_episode_rewards = 0

        while not done:
            #Get action based on policy.
            action = spot_trading_agent.epsilon_greedy_policy(curr_state.reshape(-1, obs_dim[0]))

            #Get reward and observation of next state
            next_state, reward, done = spot_trading_env.env.unwrapped.take_trade_action_step(action)

            #Accumulate rewards per step
            curr_episode_rewards += reward

            #Save transition
            spot_trading_agent.save_state_transitions(curr_state, action, reward, next_state, (0.0 if done else 1.0))

            if done:
                #Get the trade transaction from this episode
                episode_trade_transactions = spot_trading_env.env.unwrapped.get_episode_trade_transactions()

                for i in range(len(episode_trade_transactions)):
                    #Same episode num for each transaction in this loop
                    df_episodes_trade_transactions.loc[total_trade_transaction_count, "episode_num"] = episode_num
                    df_episodes_trade_transactions.loc[total_trade_transaction_count, "Date"] = episode_trade_transactions.Date[i]
                    df_episodes_trade_transactions.loc[total_trade_transaction_count, "Action"] = episode_trade_transactions.Action[i]
                    df_episodes_trade_transactions.loc[total_trade_transaction_count, "Price"] = episode_trade_transactions.Price[i]
                    df_episodes_trade_transactions.loc[total_trade_transaction_count, "Quantity"] = episode_trade_transactions.Quantity[i]
                    total_trade_transaction_count += 1

            #Replay experience
            spot_trading_agent.replay_experience()

            curr_state = next_state

        #Save rewards per episode for later reference (adjust back to show percentage gain/loss)
        df_episodes_trade_transactions.loc[total_trade_transaction_count-1, "episode_reward"] = round((curr_episode_rewards*1000), 3) #round it off to take less display space in CSV file

        #Update epsilon for next episode
        spot_trading_agent.update_epsilon()

    #Save episodes trade transactions and reward information for later reference, testing and debugging
    df_episodes_trade_transactions.iloc[:total_trade_transaction_count].to_csv(path / f'{tsymbol}/{tsymbol}_rl_episodes_info.csv')

if __name__ == '__main__':
    main()
