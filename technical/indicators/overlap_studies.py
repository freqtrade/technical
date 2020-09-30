"""
Overlap studies
"""

from numpy.core.records import ndarray
from pandas import DataFrame


########################################
#
# Overlap Studies Functions
#

# BBANDS               Bollinger Bands
def bollinger_bands(dataframe, period=21, stdv=2, field='close', colum_prefix="bb") -> DataFrame:
    from pyti.bollinger_bands import lower_bollinger_band, middle_bollinger_band, upper_bollinger_band
    dataframe["{}_lower".format(colum_prefix)] = lower_bollinger_band(dataframe[field], period, stdv)
    dataframe["{}_middle".format(colum_prefix)] = middle_bollinger_band(dataframe[field], period, stdv)
    dataframe["{}_upper".format(colum_prefix)] = upper_bollinger_band(dataframe[field], period, stdv)

    return dataframe


# DEMA                 Double Exponential Moving Average

# EMA                  Exponential Moving Average
def ema(dataframe, period, field='close'):
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
    from pyti.hull_moving_average import hull_moving_average as hma
    return hma(dataframe[field], period)


def vwma(df, window):
    return df.apply(lambda x: x.close * x.volume, axis=1).rolling(window).sum() / df.volume.rolling(window).sum()


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
