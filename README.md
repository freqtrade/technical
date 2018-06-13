# technical

Welcome to Technical, where things are, well technical. This is a simple collection of indicators and utils to make the day to day operation
of working with the freqtrade trading bot easier and more powerful!

## What does it due for you

We basically provide you with easy to use indicators, collected from all over github and custom methods. Over time we plan to provide a simple API wrapper
around TA-Lib, PyTi and others, as we find them. So you have one place, to find 100s of indicators.

### Custom indicators

We will happily add your custom indicators to this repo!

### Utilities

1. resample - easily resample your dataframe to a larger interval
2. merge - merge your resampled dataframe into your original dataframe, so you can build triggers on more than 1 interval!

### Wrapped Indicators

this following indicators are available and have been 'wrapped' to just utilize a dataframe with the standard
open/close/high/low/volume columns

1. [cmf](https://www.tradingview.com/wiki/Chaikin_Money_Flow_(CMF)) - chaikow money flow, requires dataframe and period
2. [accumulation_distribtuion](https://www.investopedia.com/terms/a/accumulationdistribution.asp) - requires a dataframe
3. osc - requires a dataframe and the periods
4. [aroon_up](https://www.investopedia.com/terms/a/aroon.asp) - dataframe, period, field
5. [aroon_down](https://www.investopedia.com/terms/a/aroon.asp) - dataframe, period, field
6. [atr](https://www.investopedia.com/terms/a/atr.asp) - dataframe, period, field
7. [atr_percent](https://www.investopedia.com/terms/a/atr.asp) - dataframe, period, field
8. [bollinger_bands](https://www.investopedia.com/terms/b/bollingerbands.asp) - dataframe, period, stdv, field, prefix
9.
10.
11.
12
13.
14.
15.
16.
17.
18.
19.
20.

We will try to add more and more wrappers as we get to it, but please be patient or help out with PR's! It's super easy, but
also super boring work.


### Usage

to use the library, please install it with pip

```bash
pip install git+https://github.com/berlinguyinca/technical
```

and than import the required packages

```python
from technical.indicators import accumulation_distribution, ...
from technical.util import resample_to_interval, resampled_merge
```

have fun!


p.s. writing these super boring wrapper takes a lot of Beer to do, please send me some IPA's to (btc): 1AoyvVpGSg9TatyCNZbTgkQveFHZXssutW

