"""
This file contains a collection of common indicators, which are based on third party or custom libraries

"""
from numpy.core.records import ndarray
from pandas import Series, DataFrame
from math import log


def aroon(dataframe, period=25, field='close', colum_prefix="aroon") -> DataFrame:
    from pyti.aroon import aroon_up as up
    from pyti.aroon import aroon_down as down
    dataframe["{}_up".format(colum_prefix)] = up(dataframe[field], period)
    dataframe["{}_down".format(colum_prefix)] = down(dataframe[field], period)
    return dataframe


def atr(dataframe, period, field='close') -> ndarray:
    from pyti.average_true_range import average_true_range
    return average_true_range(dataframe[field], period)


def atr_percent(dataframe, period, field='close') -> ndarray:
    from pyti.average_true_range_percent import average_true_range_percent
    return average_true_range_percent(dataframe[field], period)


def bollinger_bands(dataframe, period=21, stdv=2, field='close', colum_prefix="bb") -> DataFrame:
    from pyti.bollinger_bands import lower_bollinger_band, middle_bollinger_band, upper_bollinger_band
    dataframe["{}_lower".format(colum_prefix)] = lower_bollinger_band(dataframe[field], period, stdv)
    dataframe["{}_middle".format(colum_prefix)] = middle_bollinger_band(dataframe[field], period, stdv)
    dataframe["{}_upper".format(colum_prefix)] = upper_bollinger_band(dataframe[field], period, stdv)

    return dataframe


def cmf(dataframe, period=14) -> ndarray:
    from pyti.chaikin_money_flow import chaikin_money_flow

    return chaikin_money_flow(dataframe['close'], dataframe['high'], dataframe['low'], dataframe['volume'], period)


def accumulation_distribution(dataframe) -> ndarray:
    from pyti.accumulation_distribution import accumulation_distribution as acd

    return acd(dataframe['close'], dataframe['high'], dataframe['low'], dataframe['volume'])


def osc(dataframe, periods=14) -> ndarray:
    """
    1. Calculating DM (i).
        If HIGH (i) > HIGH (i - 1), DM (i) = HIGH (i) - HIGH (i - 1), otherwise DM (i) = 0.
    2. Calculating DMn (i).
        If LOW (i) < LOW (i - 1), DMn (i) = LOW (i - 1) - LOW (i), otherwise DMn (i) = 0.
    3. Calculating value of OSC:
        OSC (i) = SMA (DM, N) / (SMA (DM, N) + SMA (DMn, N)).

    :param dataframe:
    :param periods:
    :return:
    """
    df = dataframe
    df['DM'] = (df['high'] - df['high'].shift()).apply(lambda x: max(x, 0))
    df['DMn'] = (df['low'].shift() - df['low']).apply(lambda x: max(x, 0))
    return Series.rolling_mean(df.DM, periods) / (
            Series.rolling_mean(df.DM, periods) + Series.rolling_mean(df.DMn, periods))


def cmo(dataframe, period, field='close') -> ndarray:
    from pyti.chande_momentum_oscillator import chande_momentum_oscillator
    return chande_momentum_oscillator(dataframe[field], period)


def cci(dataframe, period) -> ndarray:
    from pyti.commodity_channel_index import commodity_channel_index

    return commodity_channel_index(dataframe['close'], dataframe['high'], dataframe['low'], period)


def vfi(dataframe, length=130, coef=0.2, vcoef=2.5, signalLength=5, smoothVFI=False):
    """
    Volume Flow Indicator conversion

    Author: creslinux, June 2018 - Python
    Original Author: Chris Moody, TradingView - Pinescript
    To return vfi, vfima and histogram

    A simplified interpretation of the VFI is:
    * Values above zero indicate a bullish state and the crossing of the zero line is the trigger or buy signal.
    * The strongest signal with all money flow indicators is of course divergence.
    * A crossover of vfi > vfima is uptrend
    * A crossunder of vfima > vfi is downtrend
    * smoothVFI can be set to smooth for a cleaner plot to ease false signals
    * histogram can be used against self -1 to check if upward or downward momentum


    Call from strategy to populate vfi, vfima, vfi_hist into dataframe

    Example how to call:
    # Volume Flow Index: Add VFI, VFIMA, Histogram to DF
    dataframe['vfi'], dataframe['vfima'], dataframe['vfi_hist'] =  \
        vfi(dataframe, length=130, coef=0.2, vcoef=2.5, signalLength=5, smoothVFI=False)

    :param dataframe:
    :param length: - VFI Length - 130 default
    :param coef:  - price coef  - 0.2 default
    :param vcoef: - volume coef  - 2.5 default
    :param signalLength: - 5 default
    :param smoothVFI:  bool - False detault
    :return: vfi, vfima, vfi_hist
    """

    """"
    Original Pinescript 
    From: https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/

    length = input(130, title="VFI length")
    coef = input(0.2)
    vcoef = input(2.5, title="Max. vol. cutoff")
    signalLength=input(5)
    smoothVFI=input(false, type=bool)

    #### Conversion summary to python 
      - ma(x,y) => smoothVFI ? sma(x,y) : x // Added as smoothVFI test on vfi

      - typical = hlc3  // Added to DF as HLC
      - inter = log(typical) - log(typical[1]) // Added to DF as inter
      - vinter = stdev(inter, 30) // Added to DF as vinter
      - cutoff = coef * vinter * close // Added to DF as cutoff
      - vave = sma(volume, length)[1] // Added to DF as vave
      - vmax = vave * vcoef // Added to Df as vmax
      - vc = iff(volume < vmax, volume, vmax) // Added np.where test, result in DF as vc
      - mf = typical - typical[1] // Added into DF as mf - typical is hlc3
      - vcp = iff(mf > cutoff, vc, iff(mf < -cutoff, -vc, 0)) // added in def vcp, in DF as vcp

      - vfi = ma(sum(vcp, length) / vave, 3) // Added as DF vfi. Will sma vfi 3 if smoothVFI flag set
      - vfima = ema(vfi, signalLength) // added to DF as vfima
      - d = vfi-vfima // Added to df as histogram

    ### Pinscript plotout - nothing to do here for freqtrade.
    plot(0, color=gray, style=3)
    showHisto=input(false, type=bool)
    plot(showHisto ? d : na, style=histogram, color=gray, linewidth=3, transp=50)
    plot( vfima , title="EMA of vfi", color=orange)
    plot( vfi, title="vfi", color=green,linewidth=2)
    """
    import talib as ta
    from math import log
    from pyti.simple_moving_average import simple_moving_average as sma
    from numpy import where

    length = length
    coef = coef
    vcoef = vcoef
    signalLength = signalLength
    smoothVFI = smoothVFI
    df = dataframe
    # Add hlc3 and populate inter to the dataframe
    df['hlc'] = ((df['high'] + df['low'] + df['close']) / 3).astype(float)
    df['inter'] = df['hlc'].map(log) - df['hlc'].shift(+1).map(log)
    df['vinter'] = df['inter'].rolling(30).std(ddof=0)
    df['cutoff'] = (coef * df['vinter'] * df['close'])
    # Vave is to be calculated on volume of the past bar
    df['vave'] = sma(df['volume'].shift(+1), length)
    df['vmax'] = df['vave'] * vcoef
    df['vc'] = where((df['volume'] < df['vmax']), df['volume'], df['vmax'])
    df['mf'] = df['hlc'] - df['hlc'].shift(+1)

    # more logic for vcp, so create a def and df.apply it
    def vcp(x):
        if x['mf'] > x['cutoff']:
            return x['vc']
        elif x['mf'] < -(x['cutoff']):
            return -(x['vc'])
        else:
            return 0

    df['vcp'] = df.apply(vcp, axis=1)
    # vfi has a smooth option passed over def call, sma if set
    df['vfi'] = (df['vcp'].rolling(length).sum()) / df['vave']
    if smoothVFI == True:
        df['vfi'] = sma(df['vfi'], 3)
    df['vfima'] = ta.EMA(df['vfi'], signalLength)
    df['vfi_hist'] = df['vfi'] - df['vfima']

    # clean up columns used vfi calculation but not needed for strat
    df.drop('hlc', axis=1, inplace=True)
    df.drop('inter', axis=1, inplace=True)
    df.drop('vinter', axis=1, inplace=True)
    df.drop('cutoff', axis=1, inplace=True)
    df.drop('vave', axis=1, inplace=True)
    df.drop('vmax', axis=1, inplace=True)
    df.drop('vc', axis=1, inplace=True)
    df.drop('mf', axis=1, inplace=True)
    df.drop('vcp', axis=1, inplace=True)

    return df['vfi'], df['vfima'], df['vfi_hist']
