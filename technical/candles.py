import pandas as pd
import numpy as np
from scipy.ndimage import shift


def heikinashi(bars):
    """
    Heikin Ashi calculation: https://school.stockcharts.com/doku.php?id=chart_analysis:heikin_ashi

    ha_open calculation based on: https://stackoverflow.com/a/55110393
    ha_open = [ calculate first record ][ append remaining records with list comprehension method ]
    list comprehension method is significantly faster as a for loop

    result:
    ha_open[0] =  (bars.open[0] + bars.close[0]) / 2
    ha_open[1] = (ha_open[0] + ha_close[0]) / 2
    ...
    ha_open[last] = ha_open[len(bars)-1] + ha_close[len(bars)-1]) / 2
    """

    bars = bars.copy()

    bars.loc[:, 'ha_close'] = bars.loc[:, ['open', 'high', 'low', 'close']].mean(axis=1)

    ha_open = [ (bars.open[0] + bars.close[0]) / 2 ]
    [ ha_open.append((ha_open[x] + bars.ha_close[x]) / 2) for x in range(0, len(bars)-1) ]
    bars['ha_open'] = ha_open

    bars.loc[:, 'ha_high'] = bars.loc[:, ['high', 'ha_open', 'ha_close']].max(axis=1)
    bars.loc[:, 'ha_low'] = bars.loc[:, ['low', 'ha_open', 'ha_close']].min(axis=1)

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

    result['lower_wick'] = np.vectorize(_wick_length)(result['close'], result['low'], result['open'], result['high'],
                                                      False)
    result['upper_wick'] = np.vectorize(_wick_length)(result['close'], result['low'], result['open'], result['high'],
                                                      True)
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


def _wick_length(close, low, open, high, upper):
    """
    :param close:
    :param low:
    :param open:
    :param high:
    :return:

    """

    if close > open:
        top_wick = high - close
        bottom_wick = open - low

    else:
        top_wick = high - open
        bottom_wick = close - low

    if upper:
        return top_wick
    else:
        return bottom_wick


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


def doji(dataframe, exact=False):
    """
    computes the dojis (near by default) or absolute
    :param dataframe:
    :param exact:
    :return:
    """
    if exact:
        result = dataframe['open'] == dataframe['close']
    else:
        result = (dataframe['open'] - dataframe['close']).abs() <= ((dataframe['high'] - dataframe['close']) * 0.1)

    return result.apply(lambda x: 1 if x else 0)
