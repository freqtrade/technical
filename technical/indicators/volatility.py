"""
Volatility indicator functoins
"""
from numpy.core.records import ndarray


########################################
#
# Volatility Indicator Functions
#

# ATR                  Average True Range
def atr(dataframe, period, field='close') -> ndarray:
    from pyti.average_true_range import average_true_range
    return average_true_range(dataframe[field], period)


def atr_percent(dataframe, period, field='close') -> ndarray:
    from pyti.average_true_range_percent import average_true_range_percent
    return average_true_range_percent(dataframe[field], period)


# NATR                 Normalized Average True Range
# TRANGE               True Range
