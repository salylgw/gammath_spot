# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021, Salyl Bhagwat, Gammath Works'

import os
import time

def check_if_same_day(fstat):

    print(f'\nChecking if same day file')

    fct_time = time.ctime(fstat.st_ctime).split(' ')
    dt = time.strftime('%x').split('/')
    if (fct_time[2] == ''):
        fct_date_index = 3
    else:
        fct_date_index = 2

    fct_date = int(fct_time[fct_date_index])
    dt_date = int(dt[1])

    if (fct_date == dt_date):
        return True
    else:
        return False

