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
import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

#Tensorflow shows default messages depending on GPU that may not exist on the system
#Need to disable those logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import optimizers
import keras_tuner as tuner

try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

#This is experimental, Work-In-Progress and barely tested. Lot will change before it is usable
class GRNN:
    def __init__(self):
        #Use ~3 months for autoregressive input/output
        self.ar_size = 63

    def init_model_tuning_params(self):
        self.hp = tuner.HyperParameters()
        self.hp_units = self.hp.Int('units', min_value=4, max_value=64, step=10)
        self.hp_activations = self.hp.Choice('activations', ['linear', 'relu', 'tanh'])
        self.hp_optimizers = self.hp.Choice('optimizer', ['sgd', 'rmsprop', 'adam'])
        self.hp_learning_rate = self.hp.Choice('learning_rate', [1e-4, 1e-3, 1e-2])
        return self.hp

    def build_model(self, hp):
        self.model = Sequential([LSTM(units=self.hp_units, activation=self.hp_activations, input_shape=(self.ar_size, 1), name='LSTM', return_sequences=False), Dense(1, activation=self.hp_activations, name='Output')])

        #Compile the model with popular optimizer and MSE for regression
        self.model.compile(optimizer=self.hp_optimizers, loss='mean_squared_error')
        return self.model

    def prepare_data_for_rnn_lstm(self, data, need_scaling):
        input_data_len  = len(data)
        if (input_data_len < self.ar_size):
            return

        #Align data based on AR input size
        start_offset = (input_data_len%self.ar_size)
        data = data[start_offset:]

        #Make it 2D
        data = np.array(data).reshape(-1, 1)

        if (need_scaling):
            self.scaler = MinMaxScaler()
            #Scale data between 0 and 1
            scaled_data = self.scaler.fit_transform(data)
        else:
            #Already scaled input
            scaled_data = data

        y = scaled_data[self.ar_size:]
        n = scaled_data.shape[0]
        x = np.hstack(tuple([scaled_data[i: n-j, :] for i, j in enumerate(range(self.ar_size, 0, -1))]))

        #convert x to 3D for LSTM-RNN
        x = x.reshape(-1, self.ar_size, 1)

        x_len = len(x)
        y_len = len(y)

        #Use last one year for test set
        x_test_offset = (x_len-252)
        y_test_offset = (y_len-252)

        x_train = x[:x_test_offset]
        y_train = y[:y_test_offset]
        x_test = x[x_test_offset:]
        y_test = y[y_test_offset:]

        return x_train, x_test, y_train, y_test

    def get_best_tuned_model_hyperparams(self, tsymbol, data_type, x_train, x_test, y_train, y_test):

        path = Path(f'tickers/{tsymbol}')

        #init search space
        hp = self.init_model_tuning_params()

        #Use Hyperband algo
        tuner_hb = tuner.Hyperband(self.build_model, objective='val_loss', max_epochs=20, hyperparameters=hp, directory=path, project_name=f'{data_type}_rnn_lstm_hp_tuning')

        #Use early stopping
        early_stopping = EarlyStopping(monitor='val_loss', patience=5)

        #Run search for best hyperparameters
        tuner_hb.search(x_train, y_train, validation_data=(x_test, y_test), batch_size=self.train_batch_size, callbacks=[early_stopping], shuffle=False, verbose=1)
        best_hyperparams = tuner_hb.get_best_hyperparameters()[0]

        #Save for later use
        self.best_num_of_units = best_hyperparams.get('units')
        self.best_activation = best_hyperparams.get('activations')
        self.best_optimizer = best_hyperparams.get('optimizer')
        self.best_learning_rate = best_hyperparams.get('learning_rate')
        return best_hyperparams


    #The purpose of this function is to generate data for lookahead number of timesteps
    #Generally, more time steps into the future compounds the errors so it is preferred
    #to use smaller number of lookahead timesteps. Ideal lookahead_time_steps=1.
    #Predictions are likely to reflect a trend (increasing or decreasing).
    #This function can be called again with new augmented data to retrain and do further lookahead
    def do_rnn_lstm_lookahead(self, tsymbol, data, lookahead_time_steps, data_type):

        if (data_type == 'SH_gScore'):
            need_scaling = False
        else:
            need_scaling = True

        #Prep data
        x_train, x_test, y_train, y_test = self.prepare_data_for_rnn_lstm(data, need_scaling)

        #Batch size
        self.train_batch_size = int(len(x_train)/self.ar_size)

        #Using GPU is much faster but there are some portability issues to be resolved
        #Until then, use CPU for this

        #Tune hyperparameters with keras_tuner
        best_hyperparams = self.get_best_tuned_model_hyperparams(tsymbol, data_type, x_train, x_test, y_train, y_test)

        #Create LSTM RNN for single feature using best tuned hyperparameters
        model = Sequential([LSTM(units=self.best_num_of_units, activation=self.best_activation, input_shape=(self.ar_size, 1), name='LSTM', return_sequences=False), Dense(1, activation=self.best_activation, name='Output')])

        if (self.best_optimizer == 'sgd'):
            best_optimizer = optimizers.SGD(learning_rate = self.best_learning_rate)
        elif (self.best_optimizer == 'rmsprop'):
            best_optimizer = optimizers.RMSprop(learning_rate = self.best_learning_rate)
        elif (self.best_optimizer == 'adam'):
            best_optimizer = optimizers.Adam(learning_rate = self.best_learning_rate)

        #Compile the model with popular optimizer and MSE for regression
        model.compile(optimizer=best_optimizer, loss='mean_squared_error')

        #Use early stopping
        early_stopping = EarlyStopping(monitor='val_loss', patience=40, restore_best_weights=True)

        #Train the model with training set
        lstm_training = model.fit(x_train, y_train, epochs=400, batch_size=self.train_batch_size, validation_data=(x_test, y_test), callbacks=[early_stopping], shuffle=False, verbose=1)

        #Get the evaluation results for debugging
        evaluation = model.evaluate(x_test, y_test)

        predicted_values = []

        for i in range(lookahead_time_steps):
            #Predict (eventually in a loop to predict t+k steps into the future)
            y_predict = model.predict(x_test)
            y_predict_len = len(y_predict)
            predicted_values.append(y_predict[y_predict_len-1][0])
            #Rearrange current predicted value into x_test and loop
            new_row = np.concatenate([x_test[x_test.shape[0]-1:, 1:, :], y_predict[None, (y_predict_len-1):, :]], axis=1)
            x_test = np.concatenate([x_test[1:, :, :], new_row[:, :, :]])

        if (need_scaling):
            #Unscale the values (need to do this for predicted_values also
            predicted_values = self.scaler.inverse_transform(np.array(predicted_values).reshape(-1, 1))
            predicted_values = predicted_values.flatten()

        #return values predicted for lookahead_time_steps
        return predicted_values


def main():
    """
    Main function to compute stock's SH_gScore, Price estimate.
    Work-In-Progress and barely tested
    """
    try:
        #Get the ticker symbol
        tsymbol = sys.argv[1]

        #'SH_gScore' or 'Price'
        type_to_estimate = sys.argv[2]
        if ((type_to_estimate != 'SH_gScore') and (type_to_estimate != 'Price')):
            print('ERROR: Invalid type to estaimte. Must be SH_gScore or Price')
            return

        #Get number of tradings days
        trading_days_to_estimate = int(sys.argv[3])

        path = Path(f'tickers/{tsymbol}')

        if (type_to_estimate == 'SH_gScore'):
            try:
                #Read micro-gScores
                gscores = pd.read_csv(path / f'{tsymbol}_micro_gscores.csv', index_col='Unnamed: 0')
                data = gscores.SH_gScore
            except:
                print('gScore not found. Please run gScore historian tool before using this tool')
                return
        elif (type_to_estimate == 'Price'):
            try:
                df = pd.read_csv(path / f'{tsymbol}_history.csv')
                df_len = len(df)
                mtdpy, mtd5y = gut.get_min_trading_days()
                data = df.Close.truncate(before=(df_len-mtd5y)).reset_index().drop('index', axis=1).Close
            except:
                print('Price history not found. Please run scraper tool before using this tool')

        #Instantiate gScore RNN class
        grnn = GRNN()

        #Get predictions
        y_predict = grnn.do_rnn_lstm_lookahead(tsymbol, data, trading_days_to_estimate, type_to_estimate)

        #Organize data in a data frame
        df_estimated_gscores = pd.DataFrame(y_predict, columns=[f'Estimated_{type_to_estimate}'])

        #Save gscores estiamtes
        df_estimated_gscores.to_csv(path / f'{tsymbol}_estimated_{type_to_estimate}.csv')

    except:
        print('ERROR: Need ticker symbol, type and number of trading days to estiamte')

if __name__ == '__main__':
    main()
