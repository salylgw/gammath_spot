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

try:
    from gammath_spot.gammath_pdp import get_price_dir_probability
    from gammath_spot.gammath_lgstic_signals import get_lgstic_signals
except:
    from gammath_pdp import get_price_dir_probability
    from gammath_lgstic_signals import get_lgstic_signals

def get_probabilty_signals(tsymbol, df, path):
    """
    Generate score based on empirical next day probability,
    and 1-month trend probability
    """
    _, pdp_log = get_price_dir_probability(df)
    after_month_p, lgstic_log = get_lgstic_signals(tsymbol, df, path)

    if (after_month_p < 0.4):
        probability_score = -1.0
    elif (after_month_p < 0.5):
        probability_score = -0.5
    elif (after_month_p > 0.7):
        probability_score = 1.0
    elif (after_month_p > 0.6):
        probability_score = 0.5
    elif (after_month_p > 0.5):
        probability_score = 0.25
    else:
        probability_score = 0.0

    prob_max_score = 10
    probability_score = round(probability_score*10)
    prob_string = f'Probabilities score: {probability_score}/{prob_max_score}'

    probability_log = f'{prob_string}\n{pdp_log}\n{lgstic_log}'

    return probability_score, prob_max_score, probability_log

