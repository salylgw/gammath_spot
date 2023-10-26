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

try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

#This is experimental, Work-In-Progress and barely tested. Lot will change before it is usable
#The purpose of this function is to generate data for lookahead number of timesteps
#Generally, more time steps into the future compounds the errors so it is preferred
#to use smaller number of lookahead timesteps. Ideal lookahead_time_steps=1.
#Predictions are likely to reflect a trend (increasing or decreasing).
#This function can be called again with new augmented data to retrain and do further lookahead
def do_rnn_lstm_lookahead(data, lookahead_time_steps, need_scaling):
    #re-arrange data in 63-time steps and output
    ar_size = 63

    #Align data based on AR input size
    start_offset = (len(data)%ar_size)
    data = data[start_offset:]

    #Make it 2D
    data = np.array(data).reshape(-1, 1)

    if (need_scaling):
        scaler = MinMaxScaler()
        #Scale data between 0 and 1
        scaled_data = scaler.fit_transform(data)
    else:
        #Already scaled input
        scaled_data = data

    y = scaled_data[ar_size:]
    n = scaled_data.shape[0]
    x = np.hstack(tuple([scaled_data[i: n-j, :] for i, j in enumerate(range(ar_size, 0, -1))]))

    #convert x to 3D for LSTM-RNN
    x = x.reshape(-1, ar_size, 1)

    x_len = len(x)
    y_len = len(y)

    #Use last one year for test set
    x_test_offset = (x_len-252)
    y_test_offset = (y_len-252)

    x_train = x[:x_test_offset]
    y_train = y[:y_test_offset]
    x_test = x[x_test_offset:]
    y_test = y[y_test_offset:]

    #Using GPU is much faster but there are some portability issues to be resolved
    #Until then, use CPU for this

    #TBD: Tune hyperparameters with keras_tuner

    #Run some experiments for single feature regression
    if (need_scaling):
        #Scaled using minmax scaler between 0 and 1
        model = Sequential([LSTM(units=32, input_shape=(ar_size, 1), name='LSTM', return_sequences=False), Dense(1, name='Output')])
    else:
        #Already scaled data (in this case SH_gScore is between -0.75 and +0.75)
        model = Sequential([LSTM(units=32, activation='tanh', input_shape=(ar_size, 1), name='LSTM', return_sequences=False), Dense(1, activation='tanh', name='Output')])

    #Compile the model with popular optimizer and MSE for regression
    model.compile(optimizer='adam', loss='mean_squared_error')

    #Use early stopping
    early_stopping = EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)

    #Train the model with training set
    lstm_training = model.fit(x_train, y_train, epochs=100, validation_data=(x_test, y_test), callbacks=[early_stopping], verbose=1)

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
        predicted_values = scaler.inverse_transform(np.array(predicted_values).reshape(-1, 1))
        predicted_values = predicted_values.flatten()

    #return values predicted for lookahead_time_steps
    return predicted_values