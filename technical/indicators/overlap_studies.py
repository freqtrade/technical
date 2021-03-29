"""
Overlap studies
"""

from numpy.core.records import ndarray
from pandas import DataFrame, Series


########################################
#
# Overlap Studies Functions
#

# BBANDS               Bollinger Bands
def bollinger_bands(dataframe: DataFrame, period: int = 21, stdv: int = 2,
                    field: str = 'close', colum_prefix: str = "bb") -> DataFrame:
    """
    Bollinger bands, using SMA.
    Modifies original dataframe and returns dataframe with the following 3 columns
        <column_prefix>_lower, <column_prefix>_middle, and <column_prefix>_upper,
    """
    rolling_mean = dataframe[field].rolling(window=period).mean()
    rolling_std = dataframe[field].rolling(window=period).std(ddof=0)
    dataframe[f"{colum_prefix}_lower"] = rolling_mean - (rolling_std * stdv)
    dataframe[f"{colum_prefix}_middle"] = rolling_mean
    dataframe[f"{colum_prefix}_upper"] = rolling_mean + (rolling_std * stdv)

    return dataframe


# DEMA                 Double Exponential Moving Average

# EMA                  Exponential Moving Average
def ema(dataframe: DataFrame, period: int, field='close') -> Series:
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
def sma(dataframe, period, field='close'):
    import talib.abstract as ta
    return ta.SMA(dataframe, timeperiod=period, price=field)


# T3                   Triple Exponential Moving Average (T3)

# TEMA                 Triple Exponential Moving Average
def tema(dataframe, period, field='close'):
    import talib.abstract as ta
    return ta.TEMA(dataframe, timeperiod=period, price=field)


# TRIMA                Triangular Moving Average
# WMA                  Weighted Moving Average

# Other Overlap Studies Functions
def hull_moving_average(dataframe, period, field='close') -> ndarray:
    # TODO: Remove this helper method, it's a 1:1 call to qtpylib's HMA.
    from technical.qtpylib import hma
    return hma(dataframe[field], period)


def vwma(df, window):
    return (df['close'] * df['volume']).rolling(window).sum() / df.volume.rolling(window).sum()


def zema(dataframe, period, field='close'):
    """
    zero lag ema
    :param dataframe:
    :param period:
    :param field:
    :return:
    """
    dataframe = dataframe.copy()
    dataframe['ema1'] = ema(dataframe, period, field)
    dataframe['ema2'] = ema(dataframe, period, 'ema1')
    dataframe['d'] = dataframe['ema1'] - dataframe['ema2']
    dataframe['zema'] = dataframe['ema1'] + dataframe['d']
    return dataframe['zema']
