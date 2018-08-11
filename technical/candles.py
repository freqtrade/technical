import pandas as pd
import numpy as np
from scipy.ndimage import shift


def heikinashi(bars):
    bars = bars.copy()
    bars['ha_close'] = (bars['open'] + bars['high'] +
                        bars['low'] + bars['close']) / 4

    bars['ha_open'] = (bars['open'].shift(1) + bars['close'].shift(1)) / 2
    bars.loc[:1, 'ha_open'] = bars['open'].values[0]
    for x in range(2):
        bars.loc[1:, 'ha_open'] = (
                                          (bars['ha_open'].shift(1) + bars['ha_close'].shift(1)) / 2)[1:]

    bars['ha_high'] = bars.loc[:, ['high', 'ha_open', 'ha_close']].max(axis=1)
    bars['ha_low'] = bars.loc[:, ['low', 'ha_open', 'ha_close']].min(axis=1)

    result = pd.DataFrame(
        index=bars.index,
        data={
            'open': bars['ha_open'],
            'high': bars['ha_high'],
            'low': bars['ha_low'],
            'close': bars['ha_close']})

    # usefull little helpers
    result['flat_bottom'] = np.vectorize(_flat_bottom)(result['close'], result['low'], result['open'], result['high'])
    result['flat_top'] = np.vectorize(_flat_top)(result['close'], result['low'], result['open'], result['high'])
    result['small_body'] = np.vectorize(_small_body)(result['close'], result['low'], result['open'], result['high'])
    result['candle'] = np.vectorize(_candle_type)(result['open'], result['close'])
    result['reversal'] = np.vectorize(_reversal)(result['candle'], shift(result['candle'], 1, cval=np.NAN))
    return result


def _reversal(current, prior):
    """
    do we observe a reversal
    :param current:
    :param prior:
    :return:
         1 if red to green
         0 if none
        -1 if green to red
    """
    if current == 1 and prior == -1:
        return 1
    elif current == -1 and prior == 1:
        return -1
    else:
        return 0


def _candle_type(open, close):
    """

    :param open:
    :param close:
    :return: 1 on green, -1 on red
    """
    if open < close:
        return 1
    else:
        return -1


def _small_body(close, low, open, high):
    """
    do we have a small body in relation to the wicks
    :param close:
    :param low:
    :param open:
    :param high:
    :return:
      0 if no
      1 if yes (wicks are longer than body)

    """
    size = abs(close - open)

    if close > open:
        top_wick = high - close
        bottom_wick = open - low

    else:
        top_wick = high - open
        bottom_wick = close - low

    wick_size = top_wick + bottom_wick

    if wick_size > size:
        return 1
    else:
        return 0


def _flat_top(close, low, open, high):
    """
    do we have a flat top

    :param close:
    :param low:
    :param open:
    :param high:
    :return: 1 if flat and green candle
             0 if no flat top
            -1 of flat top and red candle

    """
    if high == close:
        return 1
    elif high == open:
        return -1
    else:
        return 0


def _flat_bottom(close, low, open, high):
    """
    do we have a flat bottom
    :param close:
    :param low:
    :param open:
    :param high:
    :return:
        1 flat and green
       -1 flat and red
        0 not flat
    """
    if open == low:
        return 1
    elif close == low:
        return -1
    else:
        return 0


def _body_size(open, close):
    return abs(open - close)
