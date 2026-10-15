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
    1-week trend probability and 1-month trend probability
    """
    next_up_p, pdp_log = get_price_dir_probability(df)
    after_week_p, after_month_p, lgstic_log = get_lgstic_signals(tsymbol, df, path)

    after_day_up_p_score = 2.0*next_up_p - 1.0
    after_month_p_score = 2.0*after_month_p - 1.0

    if after_month_p > 0.6: #+ve long-term trend
        after_day_weight = 0.70
        after_month_weight = 0.30
    else: #not a conclusive +ve trend or could be -ve trend
        after_day_weight = 0.30
        after_month_weight = 0.70

    probability_score = (after_month_weight*after_month_p_score + after_day_weight*after_day_up_p_score)

    display_fraction = f'{round(probability_score*10):d}/10'
    probability_log = f'Probabilities score: {display_fraction}\n{pdp_log}\n{lgstic_log}'

    return probability_score, probability_log

