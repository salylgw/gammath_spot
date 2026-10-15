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

import pandas as pd
import numpy as np
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

def local_logistic_regression(x, y, max_iter=100, tol=1e-8):
    """Minimal logistic trend and estimate next interval"""

    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()

    n = len(y)

    if n == 0:
        raise ValueError("No data for logistic regression")

    if not np.all(np.isin(y, [0, 1])):
        raise ValueError("Only 0 and 1 allowed")

    #Standardize time
    x_mean = np.mean(x)
    x_std = np.std(x)

    z = (x - x_mean) / x_std if x_std > 0 else np.zeros(n)
    next_z = (n - x_mean) / x_std if x_std > 0 else 0.0

    #one class only history
    if np.all(y == y[0]):
        next_p = (np.sum(y) + 0.5) / (n+1)
        accuracy = 1.0
        return next_p, accuracy

    #Intercept and time slope
    X = np.column_stack((np.ones(n), z))
    beta = np.zeros(2)

    #L2 regularization on slope only
    penalty = np.diag([0.0, 1.0])

    def objective(b):
        logits = X @ b
        return (np.sum(np.logaddexp(0.0, logits) - y * logits) + 0.5 * b @ penalty @ b)

    for _ in range(max_iter):
        logits = X @ beta

        #Numerically stable sigmoid
        p = np.empty_like(logits)
        positive = logits >= 0
        p[positive] = 1.0 / (1.0 + np.exp(-logits[positive]))

        e = np.exp(logits[~positive])
        p[~positive] = e / (1.0 + e)

        gradient = X.T @ (p - y) + penalty @ beta
        weights = p * (1.0 - p)

        hessian = (X.T * weights) @ X + penalty
        hessian += np.eye(2) * 1e-10

        step = np.linalg.solve(hessian, gradient)
        old_objective = objective(beta)

        #Backtracking ensures that each step does not increase the loss
        scale = 1.0
        while scale > 1e-8:
            candidate = beta - scale * step
            if objective(candidate) <= old_objective:
                break
            scale *= 0.5

        if scale <= 1e-8:
            break

        beta = candidate

        if np.max(np.abs(scale * step)) < tol:
            break

    #In-sample accuracy, using a 0.5 classifiction threshold
    logits = X @ beta
    probabilities = 1.0 / (1.0 + np.exp(-np.clip(logits, -500, 500)))
    accuracy = round(np.mean((probabilities >= 0.5).astype(int) == y), 3)

    #Estimate the next interval
    next_logit = beta[0] + beta[1] * next_z
    next_p = 1.0 / (1.0 + np.exp(-np.clip(next_logit, -500, 500)))

    return next_p, accuracy

#Get UP/DOWN probabilities after approximately a month
def get_lgstic_signals(tsymbol, df, path):

    lgstic_signals = ''

    prices_len = len(df.Close)
    lp = df.Close[prices_len-1]
    prices = df.Close

    #Get price sigmoid (approx. 1-month interval)
    sigmoid_vals_20d = gut.get_price_sigmoid(prices, 20)

    y_vals_20d = np.array(sigmoid_vals_20d).ravel()
    x_vals_20d = np.arange(len(y_vals_20d), dtype=float)

    #Fit logistic trend
    next_20d_p, accuracy_score_20d = local_logistic_regression(x_vals_20d, y_vals_20d)

    a20dup = round(next_20d_p, 3)

    #Log output for quick reference
    lgstic_log = f'Probability after approx. a month: UP:{a20dup}, DOWN: {round((1-a20dup), 3)},accu_score:{accuracy_score_20d}'

    return a20dup, lgstic_log
