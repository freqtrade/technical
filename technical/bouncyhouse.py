"""
helper file for calculating touches and bounces of or under supports and resistances
"""
import numpy as np
from pandas import DataFrame


def _touch(high, low, level, open, close):
    """
    was the given level touched
    :param high:
    :param low:
    :param level:
    :return:
    """
    if high > level and low < level:
        if open >= close:
            return -1
        else:
            return 1
    else:
        return 0


def _bounce(open, close, level, previous_touch):
    """
    did we bounce above the given level
    :param open:
    :param close:
    :param level:
    :param previous_touch
    :return:
    """

    if previous_touch == 1 and open > level and close > level:
        return 1
    elif previous_touch == 1 and open < level and close < level:
        return -1
    else:
        return 0


def bounce(dataframe: DataFrame, level):
    """

    :param dataframe:
    :param level:
    :return:
      1 if it bounces up
      0 if no bounce
     -1 if it bounces below
    """

    from scipy.ndimage.interpolation import shift
    open = dataframe['open']
    close = dataframe['close']
    touch = shift(touches(dataframe, level), 1, cval=np.NAN)

    return np.vectorize(_bounce)(open, close, level, touch)


def touches(dataframe: DataFrame, level):
    """
        :param dataframe: our incomming dataframe
        :param level: where do we want to calculate the touches
        returns all the touches of the dataframe on the given level

        :returns
         1 if it touches and closes above
         0 if it does'nt touch
        -1 if it touches and closes below
    """

    open = dataframe['open']
    close = dataframe['close']
    high = dataframe['high']
    low = dataframe['low']

    return np.vectorize(_touch)(high, low, level, open, close)
