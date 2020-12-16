"""
Volatility indicator functoins
"""
from numpy.core.records import ndarray
from technical.vendor.qtpylib.indicators import atr  # noqa: F401

########################################
#
# Volatility Indicator Functions
#

# ATR                  Average True Range
# Imported from qtpylib, which is a fast implementation.


def atr_percent(dataframe, period: int = 14) -> ndarray:
    """

    :param dataframe: Dataframe containing candle data
    :param period: Period to use for ATR calculation (defaults to 14)
    :return: Series containing ATR_percent calculation
    """
    return (atr(dataframe, period) / dataframe['close']) * 100


# NATR                 Normalized Average True Range
# TRANGE               True Range
