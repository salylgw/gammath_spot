from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='gammath_spot',
      version='1.0',
      description='Stock Price-Opining Tools',
      long_description=readme(),
      classifiers=['Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Programming Language :: Python :: 3.8', 'Topic :: Office/Business :: Financial :: Investment'],
      url='https://github.com/...',
      author='Salyl Bhagwat',
      author_email='salylgw@gmail.com'
      packages=['gammath_spot'],
      install_requires=['numpy', 'pandas', 'talib', 'yfinance', 'pykalman', 'statsmodels', 'matplotlib',],
      include_package_data=True,
      entry_points = {
          'console_scripts': ['gammath_scraper=gammath_spot.gammath_stocks_data_scaper:main','gammath_scorer=gammath_spot.gammath_stocks_analyzer_and_scorer:main'],
      }
      zip_safe=False)

