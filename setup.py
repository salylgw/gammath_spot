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
__author__= 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021-Present, Salyl Bhagwat, Gammath Works'

from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='gammath_spot',
      version='12.0.3',
      description='Stock Price-Opining Tools',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=['Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Programming Language :: Python :: 3.8', 'Topic :: Office/Business :: Financial :: Investment'],
      url='https://github.com/salylgw/gammath_spot.git',
      author='Salyl Bhagwat',
      author_email='salylgw@gmail.com',
      packages=['gammath_spot'],
      install_requires=['numpy', 'pandas', 'pandas_datareader', 'yfinance', 'pykalman', 'statsmodels', 'matplotlib', 'scikit-learn', 'textblob', 'tensorflow', 'keras-tuner','gymnasium',],
      include_package_data=True,
      package_data={'gammath_spot': ['data/logo.png']},
      entry_points = {
          'console_scripts': ['gammath_scraper=gammath_spot.gammath_stocks_data_scraper:main','gammath_scorer=gammath_spot.gammath_stocks_analyzer_and_scorer:main','gammath_projector=gammath_spot.gammath_stocks_pep:main','gammath_estimator=gammath_spot.gammath_rnn_predictor:main','gammath_historian=gammath_spot.gammath_stocks_gscores_historian:main','gammath_backtester=gammath_spot.gammath_stocks_backtesting:main','gammath_screener=gammath_spot.gammath_stocks_screener:main','gammath_trading_simulator=gammath_spot.gammath_spot_rl_gym_env:main','gammath_spot_gui=gammath_spot.gammath_gui_app:main'],
      },
      zip_safe=False)

