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

#This is experimental and a Work-In-Progress. Lot will change before it is usable
def do_rnn_lstm_prediction(ar_size, data, need_scaling):
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

    #single time-step for now
    output_sequence = False

    #Using GPU is much faster but there are some portability issues to be resolved
    #Until then, use CPU for this

    #Run some experiments for regression problem
    if (need_scaling):
        #Scaled using minmax scaler between 0 and 1
        model = Sequential([LSTM(units=128, input_shape=(ar_size, 1), name='LSTM', return_sequences=output_sequence), Dense(1, name='Output')])
    else:
        #Already scaled data (in this case SH_gScore i.e. between -1 and +1)
        model = Sequential([LSTM(units=128, activation='tanh', input_shape=(ar_size, 1), name='LSTM', return_sequences=output_sequence), Dense(64, activation='relu'),  Dense(1, activation='linear', name='Output')])

    #Compile the model with popular optimizer and MSE for regression
    model.compile(optimizer='adam', loss='mean_squared_error')

    #Batch size for training
    batch_size = round(len(x_train)//ar_size)

    #Use early stopping
    early_stopping = EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)

    #Train the model with training set
    lstm_training = model.fit(x_train, y_train, epochs=100, batch_size=batch_size, validation_data=(x_test, y_test), callbacks=[early_stopping], verbose=1)

    #Get the evaluation results for debugging
    evaluation = model.evaluate(x_test, y_test)

    #Predict
    y_predict = model.predict(x_test)

    if (need_scaling):
        #Unscale the values
        y_predict = scaler.inverse_transform(y_predict)

    return y_predict
