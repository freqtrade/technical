# Technical

![Technical CI](https://github.com/freqtrade/technical/actions/workflows/ci.yml/badge.svg)
![Documentation CI](https://github.com/freqtrade/technical/actions/workflows/deploy-docs.yml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/technical)](https://pypi.org/project/technical/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Technical is a companion project for Freqtrade.
It includes technical indicators, as well as helpful utilities (e.g. timeframe resampling) aimed to assist in strategy development for Freqtrade.

## What does it do for you

Technical provides easy to use indicators, collected from all over github, as well as custom methods.
Over time we plan to provide a simple API wrapper around TA-Lib, PyTi and others, as we find them. So you have one place, to find 100s of indicators.

### Custom indicators

* Consensus - an indicator which is based on a consensus model, across several indicators
you can easily customize these. It is based on the [TradingView](https://www.tradingview.com/symbols/BTCUSD/technicals/)
buy/sell graph. - MovingAverage Consensus - Oscillator Consensus - Summary Consensus
* [vfi](https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/) - a modified version of On-Balance Volume (OBV) created by Markos Katsanos that gives better interpretation of current market trend.
* [mmar](https://www.tradingview.com/script/1JKqmEKy-Madrid-Moving-Average-Ribbon/) - an indicator that uses multiple MAs of different length to categorize the market trend into 4 different categories
* [madrid_sqz](https://www.tradingview.com/script/9bUUSzM3-Madrid-Trend-Squeeze/) - an indicator that uses multiple MAs to categorize the market trend into 6 different categories and to spot a squeeze
* [stc](https://www.investopedia.com/articles/forex/10/schaff-trend-cycle-indicator.asp)
* [ichimoku cloud](http://stockcharts.com/school/doku.php?id=chart_school:trading_strategies:ichimoku_cloud)
* [volume weighted moving average](https://trendspider.com/learning-center/what-is-the-volume-weighted-moving-average-vwma/) - a variation of the Simple Moving Average (SMA) that taking into account both price and volume
* [laguerre](https://www.tradingview.com/script/iUl3zTql-Ehlers-Laguerre-Relative-Strength-Index-CC/) - an indicator developed by John Ehlers as a way to minimize both the noise and lag of the regular RSI
* [vpci](https://www.tradingview.com/script/lmTqKOsa-Indicator-Volume-Price-Confirmation-Indicator-VPCI/)
* [trendlines](https://en.wikipedia.org/wiki/Trend_line_(technical_analysis)) - 2 different algorithms to calculate trendlines
* [fibonacci_retracements](https://www.investopedia.com/terms/f/fibonacciretracement.asp) - an indicator showing the fibonacci level which each candle exceeds
* [pivots points](https://www.tradingview.com/support/solutions/43000521824-pivot-points-standard/)
* [TKE Indicator](https://www.tradingview.com/script/Pcbvo0zG/) - Arithmetical mean of 7 oscilators
* [Volume Weighted MACD](https://www.tradingview.com/script/wVe6AfGA) - Volume Weighted MACD indicator
* [RMI](https://www.marketvolume.com/technicalanalysis/relativemomentumindex.asp) - Relative Momentum indicator
* [VIDYA](https://www.tradingview.com/script/64ynXU2e/) - Variable Index Dynamic Average
* [MADR](https://www.tradingview.com/script/25KCgL9H/) - Moving Average Deviation Rate
* [SSL](https://www.tradingview.com/script/xzIoaIJC-SSL-channel/) - SSL Channel
* [PMAX](https://www.tradingview.com/script/sU9molfV/) - PMAX indicator
* [ALMA](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.alma) - Arnaud Legoux Moving Average

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
* [williams percent](https://www.investopedia.com/terms/w/williamsr.asp)
* momentum oscillator
* [hull moving average](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/hull-moving-average)
* ultimate oscillator
* [sma](https://www.investopedia.com/terms/s/sma.asp)
* [ema](https://www.investopedia.com/terms/e/ema.asp)
* [tema](https://www.investopedia.com/terms/t/triple-exponential-moving-average.asp)

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

and then import the required packages

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
Just clone this repository and implement your favorite indicator to use with Freqtrade and create a Pull Request.

Please run both `ruff check .` and `ruff format .` before creating a PR to avoid unnecessary failures in CI.

Have fun!
