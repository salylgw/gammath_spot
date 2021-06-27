# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import pandas as pd
from pykalman import KalmanFilter

def get_kf_means_covariance(df):

    kf  = KalmanFilter()

    state_means, state_covariance = kf.filter(df.Close)
    
    return state_means, state_covariance
