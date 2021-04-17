# Technical

[![Technical CI](https://github.com/freqtrade/technical/actions/workflows/ci.yml/badge.svg)](https://github.com/freqtrade/technical/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/technical)](https://pypi.org/project/technical/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This is a collection of technical indicators collected or developed for Freqtrade as well as utilities such as timeframe resampling.

## What does it do for you

We basically provide you with easy to use indicators, collected from all over github and custom methods. Over time we plan to provide a simple API wrapper around TA-Lib, PyTi and others, as we find them. So you have one place, to find 100s of indicators.

### Custom indicators

* Consensus - an indicator which is based on a consensus model, across several indicators
you can easily customize these. It is based on the [TradingView](https://www.tradingview.com/symbols/BTCUSD/technicals/)
buy/sell graph. - MovingAverage Consensus - Oscillator Consensus - Summary Consensus
* [vfi](https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/)
* [mmar](https://www.tradingview.com/script/1JKqmEKy-Madrid-Moving-Average-Ribbon/)
* [madrid_sqz](https://www.tradingview.com/script/9bUUSzM3-Madrid-Trend-Squeeze/)
* [stc](https://www.investopedia.com/articles/forex/10/schaff-trend-cycle-indicator.asp)
* [ichimoku cloud](http://stockcharts.com/school/doku.php?id=chart_school:trading_strategies:ichimoku_cloud)
* volume weighted moving average
* laguerre
* [vpci](https://www.tradingview.com/script/lmTqKOsa-Indicator-Volume-Price-Confirmation-Indicator-VPCI/)
* [trendlines](https://en.wikipedia.org/wiki/Trend_line_(technical_analysis)), 2 different algorithms to calculate trendlines
* fibonacci retracements
* pivots points
* [TKE Indicator](https://www.tradingview.com/script/Pcbvo0zG/) - Arithmetical mean of 7 oscilators
* [Volume Weighted MACD](https://www.tradingview.com/script/wVe6AfGA) - Volume Weighted MACD indicator
* [RMI](https://www.marketvolume.com/technicalanalysis/relativemomentumindex.asp) - Relative Momentum indicator
* [VIDYA](https://www.tradingview.com/script/64ynXU2e/) - Variable Index Dynamic Average
* [MADR](https://www.tradingview.com/script/25KCgL9H/) - Moving Average Deviation Rate
* [SSL](https://www.tradingview.com/script/xzIoaIJC-SSL-channel/) - SSL Channel
* [PMAX](https://www.tradingview.com/script/sU9molfV/) - PMAX indicator

### Utilities

* resample - easily resample your dataframe to a larger interval
* merge - merge your resampled dataframe into your original dataframe, so you can build triggers on more than 1 interval!

### Wrapped Indicators

The following indicators are available and have been 'wrapped' to be used on a dataframe with the standard open/close/high/low/volume columns:

* [chaikin_money_flow](https://www.tradingview.com/wiki/Chaikin_Money_Flow_(CMF)) - Chaikin Money Flow, requires dataframe and period
* [accumulation_distribution](https://www.investopedia.com/terms/a/accumulationdistribution.asp) - requires a dataframe
* osc - requires a dataframe and the periods
* [atr](https://www.investopedia.com/terms/a/atr.asp) - dataframe, period, field
* [atr_percent](https://www.investopedia.com/terms/a/atr.asp) - dataframe, period, field
* [bollinger_bands](https://www.investopedia.com/terms/b/bollingerbands.asp) - dataframe, period, stdv, field, prefix
* [cmo](https://www.investopedia.com/terms/c/chandemomentumoscillator.asp) - dataframe, period, field
* [cci](https://www.investopedia.com/terms/c/commoditychannelindex.asp) - dataframe, period
* williams percent
* momentum oscilator
* hull moving average
* ultimate oscillator
* sma
* ema
* tema

We will try to add more and more wrappers as we get to it, but please be patient or help out with PR's! It's super easy, but also super boring work.

### Usage

to use the library, please install it with pip

```bash
pip install technical
```

To get the latest version, install directly from github:

```bash
pip install git+https://github.com/freqtrade/technical
```

and than import the required packages

```python
from technical.indicators import accumulation_distribution, ...
from technical.util import resample_to_interval, resampled_merge

# Assuming 1h dataframe -resampling to 4h:
dataframe_long = resample_to_interval(dataframe, 240)  # 240 = 4 * 60 = 4h

dataframe_long['rsi'] = ta.RSI(dataframe_long)
# Combine the 2 dataframes
dataframe = resampled_merge(dataframe, dataframe_long, fill_na=True)

"""
The resulting dataframe will have 5 resampled columns in addition to the regular columns,
following the template resample_<interval_in_minutes>_<orig_column_name>.
So in the above example:
['resample_240_open', 'resample_240_high', 'resample_240_low','resample_240_close', 'resample_240_rsi']
"""

```

### Contributions

We will happily add your custom indicators to this repo!
Just clone this repository and implement your favorite indicator to use with Freqtrade.

Have fun!
