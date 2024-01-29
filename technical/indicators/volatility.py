"""
Volatility indicator functions
"""

import numpy as np
import pandas as pd
from numpy.core.records import ndarray

from technical.vendor.qtpylib.indicators import atr  # noqa: F401

########################################
#
# Volatility Indicator Functions
#

########################################
#
# ATR                  Average True Range
# Imported from qtpylib, which is a fast implementation.


def atr_percent(dataframe, period: int = 14) -> ndarray:
    """

    :param dataframe: Dataframe containing candle data
    :param period: Period to use for ATR calculation (defaults to 14)
    :return: Series containing ATR_percent calculation
    """
    return (atr(dataframe, period) / dataframe["close"]) * 100


# NATR                 Normalized Average True Range
# TRANGE               True Range

########################################


def chopiness(dataframe, period: int = 14):
    """
    Choppiness index
    theory https://www.tradingview.com/scripts/choppinessindex/
    slightly adapted from
    https://medium.com/codex/detecting-ranging-and-trending-markets-with-choppiness-index-in-python-1942e6450b58

    :param dataframe: Dataframe containing candle data
    :param period: Period to use for chopiness calculation (defaults to 14)
    :return: Series containing chopiness calculation :values 0 to +100
    """

    tr1 = dataframe["high"] - dataframe["low"]
    tr2 = abs(dataframe["high"] - dataframe["close"].shift(1))
    tr3 = abs(dataframe["low"] - dataframe["close"].shift(1))

    tr = pd.concat([tr1, tr2, tr3], axis=1, join="inner").dropna().max(axis=1)
    atr = tr.rolling(1).mean()
    highh = dataframe["high"].rolling(period).max()
    lowl = dataframe["low"].rolling(period).min()
    ci = 100 * np.log10((atr.rolling(period).sum()) / (highh - lowl)) / np.log10(period)
    return ci
