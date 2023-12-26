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

        #Save the action
        self.trading_transactions['Action'][trade_step] = self.action_types[action]
        #Calculate reward for the action
        if (self.action_types[action] == 'Sell'): #Only check reward when selling
            if (self.start_buy_index >= 0):
                cost = self.trading_transactions['Price'][self.start_buy_index:(self.end_buy_index+1)].sum()
                quantity = self.trading_transactions['Quantity'][self.start_buy_index:(self.end_buy_index+1)].sum()
                sell_amount = quantity*self.prices[trade_step]
                profit_pct = 0
                if (cost > 0):
                    #Profit percentage
                    profit_pct = (((sell_amount - cost)*100)/cost)

                #Keep the reward under +/- 1 with ample room to grow in either direction
                reward = profit_pct/1000
                self.trading_transactions['Price'][trade_step] = round(self.prices[trade_step], 3)
                self.trading_transactions['Quantity'][trade_step] = quantity
                self.start_buy_index = -1
                self.end_buy_index = -1
        else:
            if (self.action_types[action] == 'Buy'):
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
        self.action_types = ['Buy', 'Hold', 'Sell']

#SPOT RL trading agent that interacts with SPOT trading
class SPOT_agent():
    def __init__(self, max_episodes, obs_dim, max_actions):
        self.gamma = 0.98
        self.epsilon = 1.0
        self.epsilon_decay = self.epsilon/max_episodes
        self.max_actions = max_actions
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
        self.model = Sequential([Dense(units=32, activation='tanh', input_shape=self.obs_dim, name='Dense_input'), Dense(units=32, activation='tanh', name='Dense_itermediate'), Dense(units=self.max_actions, name='Output')])

        #Compile the model with popular optimizer and MSE for regression
        self.model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        return self.model

    def update_qtn_weights_from_qln_weights(self):
        self.q_target_network.set_weights(self.q_learner_network.get_weights())

    def save_state_transitions(self, curr_state, action, reward, next_state, done):
        self.saved_experience.append((curr_state, action, reward, next_state, done))
        return

    def replay_experience(self):
        #Not tested yet
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
                #If there sell before buy then there won't be any reward
                max_actions = (self.max_actions-1)

            action = np.random.choice(max_actions)
        else:
            #this will still be arbitrary initially
            action = self.default_policy(state)

        #Set the flag for choosing valid action
        if (action == 0):
            self.bought = True
        elif (action == 2):
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
    register(id='SPOT_trading', entry_point='gammath_spot_rl_gym_env:SPOT_environment', max_episode_steps=None)

    spot_trading_env = gym.make('SPOT_trading', tsymbol=tsymbol, max_trading_days=max_trading_days)

    max_episodes = 1000
    obs_dim = obs_dim=spot_trading_env.env.unwrapped.observation_space.shape
    max_actions=spot_trading_env.env.unwrapped.action_space.n
    spot_trading_agent = SPOT_agent(max_episodes=max_episodes, obs_dim=obs_dim, max_actions=max_actions)
    rewards_per_episode = []

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

            #Replay experience
            spot_trading_agent.replay_experience()

            curr_state = next_state

        #Save rewards per episode for later reference (adjust back to show percentage gain/loss)
        rewards_per_episode.append(curr_episode_rewards*1000)

        #Update epsilone for next episode
        spot_trading_agent.update_epsilon()

    #Create a data frame to save the rewards and useful info to measure the performance of the strategy
    df_episodes_info = pd.DataFrame(data=rewards_per_episode, columns=['Rewards'], index=range(max_episodes))

    #Save for later reference
    df_episodes_info.to_csv(path / f'{tsymbol}/{tsymbol}_rl_episodes_info.csv')

if __name__ == '__main__':
    main()
