"""
Overlap studies
"""

import talib.abstract as ta
from numpy.core.records import ndarray
from pandas import DataFrame, Series

########################################
#
# Overlap Studies Functions
#


# BBANDS               Bollinger Bands
def bollinger_bands(
    dataframe: DataFrame,
    period: int = 21,
    stdv: int = 2,
    field: str = "close",
    colum_prefix: str = "bb",
    ma_type: str = "sma",
) -> DataFrame:
    """
    Bollinger bands, using Moving Average.
    Copying original dataframe and returns dataframe with the following 3 columns
        <column_prefix>_lower, <column_prefix>_middle, and <column_prefix>_upper,
    """

    df = dataframe.copy()

    if ma_type.lower() == "sma":
        ma = ta.SMA(df[field], period)
    elif ma_type.lower() == "ema":
        ma = ta.EMA(df[field], period)
    elif ma_type.lower() == "dema":
        ma = ta.DEMA(df[field], period)
    elif ma_type.lower() == "tema":
        ma = ta.TEMA(df[field], period)
    else:
        ma = ta.SMA(df[field], period)

    std = df[field].rolling(period).std()
    upper = ma + (std * stdv)
    lower = ma - (std * stdv)

    df[f"{colum_prefix}_lower"] = lower
    df[f"{colum_prefix}_middle"] = ma
    df[f"{colum_prefix}_upper"] = upper

    return df


# DEMA                 Double Exponential Moving Average
def dema(dataframe, period, field="close"):
    import talib.abstract as ta

    return ta.DEMA(dataframe, timeperiod=period, price=field)


def zema(dataframe, period, field="close"):
    """
    Compatibility alias for Zema
    https://github.com/freqtrade/technical/pull/356 for details.
    Please migrate to dema instead.
    Raises a Future warning - will be removed in a future version.
    """
    import warnings

    warnings.warn("zema is deprecated, use dema instead", FutureWarning)

    return dema(dataframe, period, field)


# EMA                  Exponential Moving Average
def ema(dataframe: DataFrame, period: int, field="close") -> Series:
    """
    Wrapper around talib ema (using the abstract interface)
    """
    import talib.abstract as ta

    return ta.EMA(dataframe, timeperiod=period, price=field)


# HT_TRENDLINE         Hilbert Transform - Instantaneous Trendline
# KAMA                 Kaufman Adaptive Moving Average
# MA                   Moving average
# MAMA                 MESA Adaptive Moving Average
# MAVP                 Moving average with variable period
# MIDPOINT             MidPoint over period
# MIDPRICE             Midpoint Price over period
# SAR                  Parabolic SAR
# SAREXT               Parabolic SAR - Extended


# SMA                  Simple Moving Average
def sma(dataframe, period, field="close"):
    import talib.abstract as ta

    return ta.SMA(dataframe, timeperiod=period, price=field)


# T3                   Triple Exponential Moving Average (T3)


# TEMA                 Triple Exponential Moving Average
def tema(dataframe, period, field="close"):
    import talib.abstract as ta

    return ta.TEMA(dataframe, timeperiod=period, price=field)


# TRIMA                Triangular Moving Average
# WMA                  Weighted Moving Average


# Other Overlap Studies Functions
def hull_moving_average(dataframe, period, field="close") -> ndarray:
    # TODO: Remove this helper method, it's a 1:1 call to qtpylib's HMA.
    from technical.qtpylib import hma

    return hma(dataframe[field], period)


def vwma(df, window, price="close"):
    return (df[price] * df["volume"]).rolling(window).sum() / df.volume.rolling(window).sum()
