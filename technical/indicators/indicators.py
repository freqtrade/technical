"""
This file contains a collection of common indicators,
which are based on third party or custom libraries
"""

import math

import numpy as np
from numpy.core.records import ndarray
from pandas import DataFrame, Series

from .overlap_studies import sma, vwma

########################################
#
# Pattern Recognition Functions
# Statistic Functions
# Math Transform Functions
# Math Operator Functions
#


########################################
#
# Ichimoku Cloud
#
def ichimoku(
    dataframe, conversion_line_period=9, base_line_periods=26, laggin_span=52, displacement=26
):
    """
    Ichimoku cloud indicator
    Note: Do not use chikou_span for backtesting.
        It looks into the future, is not printed by most charting platforms.
        It is only useful for visual analysis

    Usage:
        ichi = ichimoku(dataframe)
        dataframe['tenkan_sen'] = ichi['tenkan_sen']
        dataframe['kijun_sen'] = ichi['kijun_sen']
        dataframe['senkou_span_a'] = ichi['senkou_span_a']
        dataframe['senkou_span_b'] = ichi['senkou_span_b']
        dataframe['cloud_green'] = ichi['cloud_green']
        dataframe['cloud_red'] = ichi['cloud_red']

    :param dataframe: Dataframe containing OHLCV data
    :param conversion_line_period: Conversion line Period (defaults to 9)
    :param base_line_periods: Base line Periods (defaults to 26)
    :param laggin_span: Lagging span period
    :param displacement: Displacement (shift) - defaults to 26
    :return: Dict containing the following keys:
        tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, leading_senkou_span_a,
        leading_senkou_span_b, chikou_span, cloud_green, cloud_red
    """

    tenkan_sen = (
        dataframe["high"].rolling(window=conversion_line_period).max()
        + dataframe["low"].rolling(window=conversion_line_period).min()
    ) / 2

    kijun_sen = (
        dataframe["high"].rolling(window=base_line_periods).max()
        + dataframe["low"].rolling(window=base_line_periods).min()
    ) / 2

    leading_senkou_span_a = (tenkan_sen + kijun_sen) / 2

    leading_senkou_span_b = (
        dataframe["high"].rolling(window=laggin_span).max()
        + dataframe["low"].rolling(window=laggin_span).min()
    ) / 2

    senkou_span_a = leading_senkou_span_a.shift(displacement - 1)

    senkou_span_b = leading_senkou_span_b.shift(displacement - 1)

    chikou_span = dataframe["close"].shift(-displacement + 1)

    cloud_green = senkou_span_a > senkou_span_b
    cloud_red = senkou_span_b > senkou_span_a

    return {
        "tenkan_sen": tenkan_sen,
        "kijun_sen": kijun_sen,
        "senkou_span_a": senkou_span_a,
        "senkou_span_b": senkou_span_b,
        "leading_senkou_span_a": leading_senkou_span_a,
        "leading_senkou_span_b": leading_senkou_span_b,
        "chikou_span": chikou_span,
        "cloud_green": cloud_green,
        "cloud_red": cloud_red,
    }


########################################
#
# Laguerre RSI
#
def laguerre(dataframe, gamma=0.75, smooth=1, debug=False) -> Series:
    """
    laguerre RSI
    Author Creslin
    Original Author: John Ehlers 1979

    :param dataframe: df
    :param gamma: Between 0 and 1, default 0.75
    :param smooth: 1 is off. Valid values over 1 are alook back smooth for an ema
    :param debug: Bool, prints to console
    :return: Laguerre RSI:values 0 to +1
    """
    """
    Laguerra RSI
    How to trade lrsi:  (TL, DR) buy on the flat 0, sell on the drop from top,
    not when touch the top
    http://systemtradersuccess.com/testing-laguerre-rsi/

    http://www.davenewberg.com/Trading/TS_Code/Ehlers_Indicators/Laguerre_RSI.html
    """

    df = dataframe
    g = gamma
    smooth = smooth
    debug = debug
    if debug:
        from pandas import set_option

        set_option("display.max_rows", 2000)
        set_option("display.max_columns", 8)

    """
    Vectorised pandas or numpy calculations are not used
    in Laguerre as L0 is self referencing.
    Therefore we use an intertuples loop as next best option.
    """
    lrsi_l = []
    L0, L1, L2, L3 = 0.0, 0.0, 0.0, 0.0
    for row in df.itertuples(index=True, name="lrsi"):
        """
        Original Pine Logic  Block1
        p = close
        L0 = ((1 - g)*p)+(g*nz(L0[1]))
        L1 = (-g*L0)+nz(L0[1])+(g*nz(L1[1]))
        L2 = (-g*L1)+nz(L1[1])+(g*nz(L2[1]))
        L3 = (-g*L2)+nz(L2[1])+(g*nz(L3[1]))
        """
        # Feed back loop
        L0_1, L1_1, L2_1, L3_1 = L0, L1, L2, L3

        L0 = (1 - g) * row.close + g * L0_1
        L1 = -g * L0 + L0_1 + g * L1_1
        L2 = -g * L1 + L1_1 + g * L2_1
        L3 = -g * L2 + L2_1 + g * L3_1

        """ Original Pinescript Block 2
        cu=(L0 > L1? L0 - L1: 0) + (L1 > L2? L1 - L2: 0) + (L2 > L3? L2 - L3: 0)
        cd=(L0 < L1? L1 - L0: 0) + (L1 < L2? L2 - L1: 0) + (L2 < L3? L3 - L2: 0)
        """
        cu = 0.0
        cd = 0.0
        if L0 >= L1:
            cu = L0 - L1
        else:
            cd = L1 - L0

        if L1 >= L2:
            cu = cu + L1 - L2
        else:
            cd = cd + L2 - L1

        if L2 >= L3:
            cu = cu + L2 - L3
        else:
            cd = cd + L3 - L2

        """Original Pinescript  Block 3
        lrsi=ema((cu+cd==0? -1: cu+cd)==-1? 0: (cu/(cu+cd==0? -1: cu+cd)), smooth)
        """
        if (cu + cd) != 0:
            lrsi_l.append(cu / (cu + cd))
        else:
            lrsi_l.append(0)

    return Series(lrsi_l)


########################################
#
# Madrid Functions
#
def mmar(dataframe, matype="EMA", src="close", debug=False):  # noqa: C901
    """
    Madrid Moving Average Ribbon

    Returns: MMAR
    """
    """
    Author(Freqtrade): Creslinux
    Original Author(TrdingView): "Madrid"

    Pinescript from TV Source Code and Description
    //
    // Madrid : 17/OCT/2014 22:51M: Moving Average Ribbon : 2.0 : MMAR
    // http://madridjourneyonws.blogspot.com/
    //
    // This plots a moving average ribbon, either exponential or standard.
    // This study is best viewed with a dark background.  It provides an easy
    // and fast way to determine the trend direction and possible reversals.
    //
    // Lime : Uptrend. Long trading
    // Green : Reentry (buy the dip) or downtrend reversal warning
    // Red : Downtrend. Short trading
    // Maroon : Short Reentry (sell the peak) or uptrend reversal warning
    //
    // To best determine if this is a reentry point or a trend reversal
    // the MMARB (Madrid Moving Average Ribbon Bar) study is used.
    // This is the bar located at the bottom.  This bar signals when a
    // current trend reentry is found (partially filled with opposite dark color)
    // or when a trend reversal is ahead (completely filled with opposite dark color).
    //

    study(title="Madrid Moving Average Ribbon", shorttitle="MMAR", overlay=true)
    exponential = input(true, title="Exponential MA")

    src = close

    ma05 = exponential ? ema(src, 05) : sma(src, 05)
    ma10 = exponential ? ema(src, 10) : sma(src, 10)
    ma15 = exponential ? ema(src, 15) : sma(src, 15)
    ma20 = exponential ? ema(src, 20) : sma(src, 20)
    ma25 = exponential ? ema(src, 25) : sma(src, 25)
    ma30 = exponential ? ema(src, 30) : sma(src, 30)
    ma35 = exponential ? ema(src, 35) : sma(src, 35)
    ma40 = exponential ? ema(src, 40) : sma(src, 40)
    ma45 = exponential ? ema(src, 45) : sma(src, 45)
    ma50 = exponential ? ema(src, 50) : sma(src, 50)
    ma55 = exponential ? ema(src, 55) : sma(src, 55)
    ma60 = exponential ? ema(src, 60) : sma(src, 60)
    ma65 = exponential ? ema(src, 65) : sma(src, 65)
    ma70 = exponential ? ema(src, 70) : sma(src, 70)
    ma75 = exponential ? ema(src, 75) : sma(src, 75)
    ma80 = exponential ? ema(src, 80) : sma(src, 80)
    ma85 = exponential ? ema(src, 85) : sma(src, 85)
    ma90 = exponential ? ema(src, 90) : sma(src, 90)
    ma100 = exponential ? ema(src, 100) : sma(src, 100)

    leadMAColor = change(ma05)>=0 and ma05>ma100 ? lime
                : change(ma05)<0  and ma05>ma100 ? maroon
                : change(ma05)<=0 and ma05<ma100 ? red
                : change(ma05)>=0 and ma05<ma100 ? green
                : gray
    maColor(ma, maRef) =>
                  change(ma)>=0 and ma05>maRef ? lime
                : change(ma)<0  and ma05>maRef ? maroon
                : change(ma)<=0 and ma05<maRef ? red
                : change(ma)>=0 and ma05<maRef ? green
                : gray

    plot( ma05, color=leadMAColor, style=line, title="MMA05", linewidth=3)
    plot( ma10, color=maColor(ma10,ma100), style=line, title="MMA10", linewidth=1)
    plot( ma15, color=maColor(ma15,ma100), style=line, title="MMA15", linewidth=1)
    plot( ma20, color=maColor(ma20,ma100), style=line, title="MMA20", linewidth=1)
    plot( ma25, color=maColor(ma25,ma100), style=line, title="MMA25", linewidth=1)
    plot( ma30, color=maColor(ma30,ma100), style=line, title="MMA30", linewidth=1)
    plot( ma35, color=maColor(ma35,ma100), style=line, title="MMA35", linewidth=1)
    plot( ma40, color=maColor(ma40,ma100), style=line, title="MMA40", linewidth=1)
    plot( ma45, color=maColor(ma45,ma100), style=line, title="MMA45", linewidth=1)
    plot( ma50, color=maColor(ma50,ma100), style=line, title="MMA50", linewidth=1)
    plot( ma55, color=maColor(ma55,ma100), style=line, title="MMA55", linewidth=1)
    plot( ma60, color=maColor(ma60,ma100), style=line, title="MMA60", linewidth=1)
    plot( ma65, color=maColor(ma65,ma100), style=line, title="MMA65", linewidth=1)
    plot( ma70, color=maColor(ma70,ma100), style=line, title="MMA70", linewidth=1)
    plot( ma75, color=maColor(ma75,ma100), style=line, title="MMA75", linewidth=1)
    plot( ma80, color=maColor(ma80,ma100), style=line, title="MMA80", linewidth=1)
    plot( ma85, color=maColor(ma85,ma100), style=line, title="MMA85", linewidth=1)
    plot( ma90, color=maColor(ma90,ma100), style=line, title="MMA90", linewidth=3)
    :return:
    """
    import talib as ta

    matype = matype
    src = src
    df = dataframe
    debug = debug

    # Default to EMA, allow SMA if passed to def.
    if matype == "EMA" or matype == "ema":
        ma = ta.EMA
    elif matype == "SMA" or matype == "sma":
        ma = ta.SMA
    else:
        ma = ta.EMA

    # Get MAs, also last MA in own column to pass to def later
    df["ma05"] = ma(df[src], 5)
    df["ma05l"] = df["ma05"].shift()
    df["ma10"] = ma(df[src], 10)
    df["ma10l"] = df["ma10"].shift()
    df["ma20"] = ma(df[src], 20)
    df["ma20l"] = df["ma20"].shift()
    df["ma30"] = ma(df[src], 30)
    df["ma30l"] = df["ma30"].shift()
    df["ma40"] = ma(df[src], 40)
    df["ma40l"] = df["ma40"].shift()
    df["ma50"] = ma(df[src], 50)
    df["ma50l"] = df["ma50"].shift()
    df["ma60"] = ma(df[src], 60)
    df["ma60l"] = df["ma60"].shift()
    df["ma70"] = ma(df[src], 70)
    df["ma70l"] = df["ma70"].shift()
    df["ma80"] = ma(df[src], 80)
    df["ma80l"] = df["ma80"].shift()
    df["ma90"] = ma(df[src], 90)
    df["ma90l"] = df["ma90"].shift()
    df["ma100"] = ma(df[src], 100)
    df["ma100l"] = df["ma100"].shift()

    """ logic for LeadMA
    : change(ma05)>=0 and ma05>ma100 ? lime    +2
    : change(ma05)<0  and ma05>ma100 ? maroon  -1
    : change(ma05)<=0 and ma05<ma100 ? red     -2
    : change(ma05)>=0 and ma05<ma100 ? green   +1
    : gray
    """

    def leadMAc(x):
        if (x["ma05"] - x["ma05l"]) >= 0 and (x["ma05"] > x["ma100"]):
            # Lime: Uptrend.Long trading
            x["leadMA"] = "lime"
            return x["leadMA"]
        elif (x["ma05"] - x["ma05l"]) < 0 and (x["ma05"] > x["ma100"]):
            # Maroon : Short Reentry (sell the peak) or uptrend reversal warning
            x["leadMA"] = "maroon"
            return x["leadMA"]
        elif (x["ma05"] - x["ma05l"]) <= 0 and (x["ma05"] < x["ma100"]):
            # Red : Downtrend. Short trading
            x["leadMA"] = "red"
            return x["leadMA"]
        elif (x["ma05"] - x["ma05l"]) >= 0 and (x["ma05"] < x["ma100"]):
            # Green: Reentry(buy the dip) or downtrend reversal warning
            x["leadMA"] = "green"
            return x["leadMA"]
        else:
            # If its great it means not enough ticker data for lookback
            x["leadMA"] = "grey"
            return x["leadMA"]

    df["leadMA"] = df.apply(leadMAc, axis=1)

    """   Logic for MAs
    : change(ma)>=0 and ma>ma100 ? lime
    : change(ma)<0  and ma>ma100 ? maroon
    : change(ma)<=0 and ma<ma100 ? red
    : change(ma)>=0 and ma<ma100 ? green
    : gray
    """

    def maColor(x, ma):
        col_label = "_".join([ma, "c"])
        col_label_1 = "".join([ma, "l"])

        if (x[ma] - x[col_label_1]) >= 0 and (x[ma] > x["ma100"]):
            # Lime: Uptrend.Long trading
            x[col_label] = "lime"
            return x[col_label]
        elif (x[ma] - x[col_label_1]) < 0 and (x[ma] > x["ma100"]):
            # Maroon : Short Reentry (sell the peak) or uptrend reversal warning
            x[col_label] = "maroon"
            return x[col_label]

        elif (x[ma] - x[col_label_1]) <= 0 and (x[ma] < x["ma100"]):
            # Red : Downtrend. Short trading
            x[col_label] = "red"
            return x[col_label]

        elif (x[ma] - x[col_label_1]) >= 0 and (x[ma] < x["ma100"]):
            # Green: Reentry(buy the dip) or downtrend reversal warning
            x[col_label] = "green"
            return x[col_label]
        else:
            # If its great it means not enough ticker data for lookback
            x[col_label] = "grey"
            return x[col_label]

    df["ma10_c"] = df.apply(maColor, ma="ma10", axis=1)
    df["ma20_c"] = df.apply(maColor, ma="ma20", axis=1)
    df["ma30_c"] = df.apply(maColor, ma="ma30", axis=1)
    df["ma40_c"] = df.apply(maColor, ma="ma40", axis=1)
    df["ma50_c"] = df.apply(maColor, ma="ma50", axis=1)
    df["ma60_c"] = df.apply(maColor, ma="ma60", axis=1)
    df["ma70_c"] = df.apply(maColor, ma="ma70", axis=1)
    df["ma80_c"] = df.apply(maColor, ma="ma80", axis=1)
    df["ma90_c"] = df.apply(maColor, ma="ma90", axis=1)

    if debug:
        from pandas import set_option

        set_option("display.max_rows", 10)
        print(
            df[
                [
                    "date",
                    "ma05",
                    "ma05l",
                    "leadMA",
                    "ma10",
                    "ma10l",
                    "ma10_c",
                    # "ma20", "ma20l", "ma20_c",
                    # "ma30", "ma30l", "ma30_c",
                    # "ma40", "ma40l", "ma40_c",
                    # "ma50", "ma50l", "ma50_c",
                    # "ma60", "ma60l", "ma60_c",
                    # "ma70", "ma70l", "ma70_c",
                    # "ma80", "ma80l", "ma80_c",
                    "ma90",
                    "ma90l",
                    "ma90_c",
                    "ma100",
                ]
            ].tail(200)
        )

        print(
            df[
                [
                    "date",
                    "close",
                    "leadMA",
                    "ma10_c",
                    "ma20_c",
                    "ma30_c",
                    "ma40_c",
                    "ma50_c",
                    "ma60_c",
                    "ma70_c",
                    "ma80_c",
                    "ma90_c",
                ]
            ].tail(684)
        )

    return (
        df["leadMA"],
        df["ma10_c"],
        df["ma20_c"],
        df["ma30_c"],
        df["ma40_c"],
        df["ma50_c"],
        df["ma60_c"],
        df["ma70_c"],
        df["ma80_c"],
        df["ma90_c"],
    )


def madrid_sqz(datafame, length=34, src="close", ref=13, sqzLen=5):
    """
    Squeeze Madrid Indicator

    Author: Creslinux
    Original Author: Madrid - Tradingview
    https://www.tradingview.com/script/9bUUSzM3-Madrid-Trend-Squeeze/

    :param datafame:
    :param length: min 14 - default 34
    :param src: default close
    :param ref: default 13
    :param sqzLen: default 5
    :return: df['sqz_cma_c'], df['sqz_rma_c'], df['sqz_sma_c']


    There are seven colors used for the study

    Green : Uptrend in general
    Lime : Spots the current uptrend leg
    Aqua : The maximum profitability of the leg in a long trade
    The Squeeze happens when Green+Lime+Aqua are aligned (the larger the values the better)

    Maroon : Downtrend in general
    Red : Spots the current downtrend leg
    Fuchsia: The maximum profitability of the leg in a short trade
    The Squeeze happens when Maroon+Red+Fuchsia are aligned (the larger the values the better)

    Yellow : The trend has come to a pause and it is either a reversal warning or a continuation.
    These are the entry, re-entry or closing position points.
    """

    """
    Original Pinescript source code

    ma = ema(src, len)
    closema = close - ma
    refma = ema(src, ref) - ma
    sqzma = ema(src, sqzLen) - ma

    hline(0)
    plotcandle(0, closema, 0, closema, color=closema >= 0?aqua: fuchsia)
    plotcandle(0, sqzma, 0, sqzma, color=sqzma >= 0?lime: red)
    plotcandle(0, refma, 0, refma, color=(refma >= 0 and closema < refma) or (
                refma < 0 and closema > refma) ? yellow: refma >= 0 ? green: maroon)
    """
    import talib as ta

    len = length
    src = src
    ref = ref
    sqzLen = sqzLen
    df = datafame
    ema = ta.EMA

    """ Original code logic
    ma = ema(src, len)
    closema = close - ma
    refma = ema(src, ref) - ma
    sqzma = ema(src, sqzLen) - ma
    """
    df["sqz_ma"] = ema(df[src], len)
    df["sqz_cma"] = df["close"] - df["sqz_ma"]
    df["sqz_rma"] = ema(df[src], ref) - df["sqz_ma"]
    df["sqz_sma"] = ema(df[src], sqzLen) - df["sqz_ma"]

    """ Original code logic
    plotcandle(0, closema, 0, closema, color=closema >= 0?aqua: fuchsia)
    plotcandle(0, sqzma, 0, sqzma, color=sqzma >= 0?lime: red)

    plotcandle(0, refma, 0, refma, color=
    (refma >= 0 and closema < refma) or (refma < 0 and closema > refma) ? yellow:
    refma >= 0 ? green: maroon)
    """

    # print(df[['sqz_cma', 'sqz_rma', 'sqz_sma']])

    def sqz_cma_c(x):
        if x["sqz_cma"] >= 0:
            x["sqz_cma_c"] = "aqua"
            return x["sqz_cma_c"]
        else:
            x["sqz_cma_c"] = "fuchsia"
            return x["sqz_cma_c"]

    df["sqz_cma_c"] = df.apply(sqz_cma_c, axis=1)

    def sqz_sma_c(x):
        if x["sqz_sma"] >= 0:
            x["sqz_sma_c"] = "lime"
            return x["sqz_sma_c"]
        else:
            x["sqz_sma_c"] = "red"
            return x["sqz_sma_c"]

    df["sqz_sma_c"] = df.apply(sqz_sma_c, axis=1)

    def sqz_rma_c(x):
        if x["sqz_rma"] >= 0 and x["sqz_cma"] < x["sqz_rma"]:
            x["sqz_rma_c"] = "yellow"
            return x["sqz_rma_c"]
        elif x["sqz_rma"] < 0 and x["sqz_cma"] > x["sqz_rma"]:
            x["sqz_rma_c"] = "yellow"
            return x["sqz_rma_c"]
        elif x["sqz_rma"] >= 0:
            x["sqz_rma_c"] = "green"
            return x["sqz_rma_c"]
        else:
            x["sqz_rma_c"] = "maroon"
            return x["sqz_rma_c"]

    df["sqz_rma_c"] = df.apply(sqz_rma_c, axis=1)

    # print(df[['sqz_cma_c', 'sqz_rma_c', 'sqz_sma_c']])
    return df["sqz_cma_c"], df["sqz_rma_c"], df["sqz_sma_c"]


########################################
#
# Other Indicator Functions / Unsorted
#
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
    df["DM"] = (df["high"] - df["high"].shift()).apply(lambda x: max(x, 0))
    df["DMn"] = (df["low"].shift() - df["low"]).apply(lambda x: max(x, 0))
    return Series.rolling_mean(df.DM, periods) / (
        Series.rolling_mean(df.DM, periods) + Series.rolling_mean(df.DMn, periods)
    )


def vfi(dataframe, length=130, coef=0.2, vcoef=2.5, signalLength=5, smoothVFI=False):
    """
    Volume Flow Indicator conversion

    Author: creslinux, June 2018 - Python
    Original Author: Chris Moody, TradingView - Pinescript
    To return vfi, vfima and histogram

    A simplified interpretation of the VFI is:
    * Values above zero indicate a bullish state and the crossing of the zero line is the trigger
        or buy signal.
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
    :param smoothVFI:  bool - False default
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

      - vfi = ma(sum(vcp, length) / vave, 3) // Added as DF vfi.
            Will sma vfi 3 if smoothVFI flag set
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
    from numpy import where

    length = length
    coef = coef
    vcoef = vcoef
    signalLength = signalLength
    smoothVFI = smoothVFI
    df = dataframe
    # Add hlc3 and populate inter to the dataframe
    df["hlc"] = ((df["high"] + df["low"] + df["close"]) / 3).astype(float)
    df["inter"] = df["hlc"].map(math.log) - df["hlc"].shift(+1).map(math.log)
    df["vinter"] = df["inter"].rolling(30).std(ddof=0)
    df["cutoff"] = coef * df["vinter"] * df["close"]
    # Vave is to be calculated on volume of the past bar
    df["vave"] = ta.SMA(df["volume"].shift(+1), timeperiod=length)
    df["vmax"] = df["vave"] * vcoef
    df["vc"] = where((df["volume"] < df["vmax"]), df["volume"], df["vmax"])
    df["mf"] = df["hlc"] - df["hlc"].shift(+1)

    # more logic for vcp, so create a def and df.apply it
    def vcp(x):
        if x["mf"] > x["cutoff"]:
            return x["vc"]
        elif x["mf"] < -(x["cutoff"]):
            return -(x["vc"])
        else:
            return 0

    df["vcp"] = df.apply(vcp, axis=1)
    # vfi has a smooth option passed over def call, sma if set
    df["vfi"] = (df["vcp"].rolling(length).sum()) / df["vave"]
    if smoothVFI is True:
        df["vfi"] = ta.SMA(df["vfi"], timeperiod=3)
    df["vfima"] = ta.EMA(df["vfi"], signalLength)
    df["vfi_hist"] = df["vfi"] - df["vfima"]

    # clean up columns used vfi calculation but not needed for strategy
    df.drop("hlc", axis=1, inplace=True)
    df.drop("inter", axis=1, inplace=True)
    df.drop("vinter", axis=1, inplace=True)
    df.drop("cutoff", axis=1, inplace=True)
    df.drop("vave", axis=1, inplace=True)
    df.drop("vmax", axis=1, inplace=True)
    df.drop("vc", axis=1, inplace=True)
    df.drop("mf", axis=1, inplace=True)
    df.drop("vcp", axis=1, inplace=True)

    return df["vfi"], df["vfima"], df["vfi_hist"]


def stc(dataframe, fast=23, slow=50, length=10):
    # First, the 23-period and the 50-period EMA and the MACD values are calculated:
    # EMA1 = EMA (Close, Short Length);
    # EMA2 = EMA (Close, Long Length);
    # MACD = EMA1 – EMA2.
    # Second, the 10-period Stochastic from the MACD values is calculated:
    # %K (MACD) = %KV (MACD, 10);
    # %D (MACD) = %DV (MACD, 10);
    # Schaff = 100 x (MACD – %K (MACD)) / (%D (MACD) – %K (MACD))

    import talib.abstract as ta

    MACD = ta.EMA(dataframe, timeperiod=fast) - ta.EMA(dataframe, timeperiod=slow)
    STOK = (
        (MACD - MACD.rolling(window=length).min())
        / (MACD.rolling(window=length).max() - MACD.rolling(window=length).min())
    ) * 100
    STOD = STOK.rolling(window=length).mean()
    dataframe["stc"] = 100 * (MACD - (STOK * MACD)) / ((STOD * MACD) - (STOK * MACD))

    return dataframe["stc"]


def vpcii(dataframe, period_short=5, period_long=20, hist=8, hist_long=30):
    """
    improved version of the vpcii


    :param dataframe:
    :param period_short:
    :param period_long:
    :param hist:
    :return:
    """

    dataframe = dataframe.copy()
    dataframe["vpci"] = vpci(dataframe, period_short, period_long)
    dataframe["vpcis"] = dataframe["vpci"].rolling(hist).mean()
    dataframe["vpci_hist"] = (dataframe["vpci"] - dataframe["vpcis"]).pct_change()

    return dataframe["vpci_hist"].abs()


def vpci(dataframe, period_short=5, period_long=20):
    """
    volume confirming indicator as seen here

    https://www.tradingview.com/script/lmTqKOsa-Indicator-Volume-Price-Confirmation-Indicator-VPCI/


    should be used with bollinger bands, for deccision making
    :param dataframe:
    :param period_long:
    :param period_short:
    :return:
    """

    vpc = vwma(dataframe, period_long) - sma(dataframe, period_long)
    vpr = vwma(dataframe, period_short) / sma(dataframe, period_short)
    vm = sma(dataframe, period_short, field="volume") / sma(dataframe, period_long, field="volume")

    vpci = vpc * vpr * vm

    return vpci


def fibonacci_retracements(df, field="close") -> DataFrame:
    # Common Fibonacci replacement thresholds:
    # 1.0, sqrt(F_n / F_{n+1}), F_n / F_{n+1}, 0.5, F_n / F_{n+2}, F_n / F_{n+3}, 0.0
    thresholds = [1.0, 0.786, 0.618, 0.5, 0.382, 0.236, 0.0]

    window_min, window_max = df[field].min(), df[field].max()
    # fib_levels = [window_min + t * (window_max - window_min) for t in thresholds]

    # Scale data to match to thresholds
    # Can be returned instead if one is looking at the movement between levels
    data = (df[field] - window_min) / (window_max - window_min)

    # Otherwise, we return a step indicator showing the fibonacci level
    # which each candle exceeds
    return data.apply(lambda x: max(t for t in thresholds if x >= t))


def return_on_investment(dataframe, decimals=2) -> DataFrame:
    """
    Simple ROI indicator.

    :param dataframe:
    :param decimals:
    :return:
    """

    close = np.array(dataframe["close"])
    buy = np.array(dataframe["buy"])
    buy_idx = np.where(buy == 1)[0]
    roi = np.zeros(len(close))
    if len(buy_idx) > 0:
        # get chunks starting with a buy signal
        # everything before the first buy signal is discarded
        buy_chunks = np.split(close, buy_idx)[1:]
        for idx, chunk in zip(buy_idx, buy_chunks):
            # round ROI to avoid float accuracy problems
            chunk_roi = np.round(100.0 * (chunk / chunk[0] - 1.0), decimals)
            roi[idx : idx + len(chunk)] = chunk_roi

    dataframe["roi"] = roi

    return dataframe


def td_sequential(dataframe):
    """
    TD Sequential
    Author(Freqtrade): MichealReed
    Original Author: Tom Demark


    :param dataframe: dataframe
    :return: Dataframe with additional column TD_count
            content: TD Sequential:values -9 to +9
    """

    # Copy DF
    df = dataframe.copy()

    condv = df["volume"] > 0
    cond1 = df["close"] > df["close"].shift(4)
    cond2 = df["close"] < df["close"].shift(4)

    df["cond_tdb_a"] = (df.groupby(((cond1)[condv]).cumsum()).cumcount() % 10 == 0).cumsum()
    df["cond_tds_a"] = (df.groupby(((cond2)[condv]).cumsum()).cumcount() % 10 == 0).cumsum()
    df["cond_tdb_b"] = (df.groupby(((cond1)[condv]).cumsum()).cumcount() % 10 != 0).cumsum()
    df["cond_tds_b"] = (df.groupby(((cond2)[condv]).cumsum()).cumcount() % 10 != 0).cumsum()

    df["tdb_a"] = df.groupby(df["cond_tdb_a"]).cumcount()
    df["tds_a"] = df.groupby(df["cond_tds_a"]).cumcount()

    df["tdb_b"] = df.groupby(df["cond_tdb_b"]).cumcount()
    df["tds_b"] = df.groupby(df["cond_tds_b"]).cumcount()

    df["tdc"] = df["tds_a"] - df["tdb_a"]
    df["tdc"] = df.apply((lambda x: x["tdb_b"] % 9 if x["tdb_b"] > 9 else x["tdc"]), axis=1)
    df["tdc"] = df.apply((lambda x: (x["tds_b"] % 9) * -1 if x["tds_b"] > 9 else x["tdc"]), axis=1)
    dataframe.loc[:, "TD_count"] = df["tdc"]
    return dataframe


def TKE(dataframe, *, length=14, emaperiod=5):
    """
    Source: https://www.tradingview.com/script/Pcbvo0zG/
    Author: Dr Yasar ERDINC

    The calculation is simple:
    TKE=(RSI+STOCHASTIC+ULTIMATE OSCILLATOR+MFI+WIILIAMS %R+MOMENTUM+CCI)/7
    Buy signal: when TKE crosses above 20 value
    Oversold region: under 20 value
    Overbought region: over 80 value

    Another usage of TKE is with its EMA ,
    the default value is defined as 5 bars of EMA of the TKE line,
    Go long: when TKE crosses above EMALine
    Go short: when TKE crosses below EMALine

    Usage:
        `dataframe['TKE'], dataframe['TKEema'] = TKE1(dataframe)`
    """
    import talib.abstract as ta

    df = dataframe.copy()
    # TKE=(RSI+STOCHASTIC+ULTIMATE OSCILLATOR+MFI+WIILIAMS %R+MOMENTUM+CCI)/7
    df["rsi"] = ta.RSI(df, timeperiod=length)
    df["stoch"] = (
        100
        * (df["close"] - df["low"].rolling(window=length).min())
        / (df["high"].rolling(window=length).max() - df["low"].rolling(window=length).min())
    )

    df["ultosc"] = ta.ULTOSC(df, timeperiod1=7, timeperiod2=14, timeperiod3=28)
    df["mfi"] = ta.MFI(df, timeperiod=length)
    df["willr"] = ta.WILLR(df, timeperiod=length)
    df["mom"] = ta.ROCR100(df, timeperiod=length)
    df["cci"] = ta.CCI(df, timeperiod=length)
    df["TKE"] = df[["rsi", "stoch", "ultosc", "mfi", "willr", "mom", "cci"]].mean(axis="columns")
    df["TKEema"] = ta.EMA(df["TKE"], timeperiod=emaperiod)
    return df["TKE"], df["TKEema"]


def vwmacd(dataframe, *, fastperiod=12, slowperiod=26, signalperiod=9):
    """
    Volume Weighted MACD
    Author: KIVANC @fr3762 on twitter
    Developer: Buff Dormeier @BuffDormeierWFA on twitter
    Source: https://www.tradingview.com/script/wVe6AfGA

    study("VOLUME WEIGHTED MACD V2", shorttitle="VWMACDV2")
    fastperiod = input(12,title="fastperiod",type=integer,minval=1,maxval=500)
    slowperiod = input(26,title="slowperiod",type=integer,minval=1,maxval=500)
    signalperiod = input(9,title="signalperiod",type=integer,minval=1,maxval=500)
    fastMA = ema(volume*close, fastperiod)/ema(volume, fastperiod)
    slowMA = ema(volume*close, slowperiod)/ema(volume, slowperiod)
    vwmacd = fastMA - slowMA
    signal = ema(vwmacd, signalperiod)
    hist= vwmacd - signal
    plot(vwmacd, color=blue, linewidth=2)
    plot(signal, color=red, linewidth=2)
    plot(hist, color=green, linewidth=4, style=histogram)
    plot(0, color=black)

    Usage:
        vwmacd = vwmacd(dataframe)
        dataframe['vwmacd'] = vwmacd['vwmacd']
        dataframe['vwmacdsignal'] = vwmacd['signal']
        dataframe['vwmacdhist'] = vwmacd['hist']
        # simplified:
        dataframe = vwmacd(dataframe)
    :returns: dataframe with new columns for vwmacd, signal and hist

    """

    import talib.abstract as ta

    dataframe["fastMA"] = ta.EMA(dataframe["volume"] * dataframe["close"], fastperiod) / ta.EMA(
        dataframe["volume"], fastperiod
    )
    dataframe["slowMA"] = ta.EMA(dataframe["volume"] * dataframe["close"], slowperiod) / ta.EMA(
        dataframe["volume"], slowperiod
    )
    dataframe["vwmacd"] = dataframe["fastMA"] - dataframe["slowMA"]
    dataframe["signal"] = ta.EMA(dataframe["vwmacd"], signalperiod)
    dataframe["hist"] = dataframe["vwmacd"] - dataframe["signal"]
    dataframe = dataframe.drop(["fastMA", "slowMA"], axis=1)
    return dataframe


def RMI(dataframe, *, length=20, mom=5):
    """
    Source: https://www.marketvolume.com/technicalanalysis/relativemomentumindex.asp
    length: Length of EMA
    mom: Momentum

    Usage:
        dataframe['RMI'] = RMI(dataframe)

    """
    import talib.abstract as ta

    df = dataframe.copy()
    df["maxup"] = (df["close"] - df["close"].shift(mom)).clip(lower=0).fillna(0)
    df["maxdown"] = (df["close"].shift(mom) - df["close"]).clip(lower=0).fillna(0)

    df["emaInc"] = ta.EMA(df, price="maxup", timeperiod=length)
    df["emaDec"] = ta.EMA(df, price="maxdown", timeperiod=length)

    df["RMI"] = np.where(df["emaDec"] == 0, 0, 100 - 100 / (1 + df["emaInc"] / df["emaDec"]))
    return df["RMI"]


def VIDYA(dataframe, length=9, select=True):
    """
    Source: https://www.tradingview.com/script/64ynXU2e/
    Author: Tushar Chande
    Pinescript Author: KivancOzbilgic

    Variable Index Dynamic Average VIDYA

    To achieve the goals, the indicator filters out the market fluctuations (noises)
    by averaging the price values of the periods, over which it is calculated.
    In the process, some extra value (weight) is added to the average prices,
    as it is done during calculations of all weighted indicators, such as EMA , LWMA, and SMMA.
    But during the VIDYA indicator's calculation, every period's price
    receives a weight increment adapted to the current market's volatility .

    select: True = CMO, False= StdDev as volatility index
    usage:
      dataframe['VIDYA'] = VIDYA(dataframe)
    """
    df = dataframe.copy()
    alpha = 2 / (length + 1)
    df["momm"] = df["close"].diff()
    df["m1"] = np.where(df["momm"] >= 0, df["momm"], 0.0)
    df["m2"] = np.where(df["momm"] >= 0, 0.0, -df["momm"])

    df["sm1"] = df["m1"].rolling(length).sum()
    df["sm2"] = df["m2"].rolling(length).sum()

    df["chandeMO"] = 100 * (df["sm1"] - df["sm2"]) / (df["sm1"] + df["sm2"])
    if select:
        df["k"] = abs(df["chandeMO"]) / 100
    else:
        df["k"] = df["close"].rolling(length).std()

    cols = ["momm", "m1", "m2", "sm1", "sm2", "chandeMO", "k"]
    df.loc[:, cols] = df.loc[:, cols].fillna(0.0)

    df["VIDYA"] = 0.0
    for i in range(length, len(df)):
        df["VIDYA"].iat[i] = (
            alpha * df["k"].iat[i] * df["close"].iat[i]
            + (1 - alpha * df["k"].iat[i]) * df["VIDYA"].iat[i - 1]
        )

    return df["VIDYA"]


def MADR(dataframe, length=21, stds_dist=2, matype="sma"):
    """
    Moving Average Deviation Rate, similar to bollinger bands
    Source: https://tradingview.com/script/25KCgL9H/
    Author: tarantula3535

    Moving average deviation rate

    Simple moving average deviation rate and standard deviation.

    The bollinger band is momentum value standard deviation.
    But the bollinger band is not normal distribution to close price.
    Moving average deviation rate is normal distribution.

    This indicator will define upper and lower bounds based of stds-σ standard deviation of rate column.
    If it exceeds stds-σ, it is a trading opportunity.

    """

    import talib.abstract as ta

    df = dataframe.copy()
    """ tradingview's code
    _maPeriod = input(21, title="Moving average period")

    //deviation rate
    _sma = sma(close, _maPeriod)
    _rate = close / _sma * 100 - 100

    //deviation rate std
    _stdCenter = sma(_rate, _maPeriod * 2)
    _std = stdev(_rate, _maPeriod * 2)
    _plusDev = _stdCenter + _std * 2
    _minusDev = _stdCenter - _std * 2
    """

    if matype.lower() == "sma":
        ma_close = ta.SMA(df, timeperiod=length)
    elif matype.lower() == "ema":
        ma_close = ta.EMA(df, timeperiod=length)
    else:
        ma_close = ta.SMA(df, timeperiod=length)

    df["rate"] = ((df["close"] / ma_close) * 100) - 100

    if matype.lower() == "sma":
        df["stdcenter"] = ta.SMA(df.rate, timeperiod=(length * stds_dist))
    elif matype.lower() == "ema":
        df["stdcenter"] = ta.EMA(df.rate, timeperiod=(length * stds_dist))
    else:
        df["stdcenter"] = ta.SMA(df.rate, timeperiod=(length * stds_dist))

    std = ta.STDDEV(df.rate, timeperiod=(length * stds_dist))
    df["plusdev"] = df["stdcenter"] + (std * stds_dist)
    df["minusdev"] = df["stdcenter"] - (std * stds_dist)
    # return stdcenter , plusdev , minusdev, rate
    return df


def SSLChannels(dataframe, length=10, mode="sma"):
    """
    Source: https://www.tradingview.com/script/xzIoaIJC-SSL-channel/
    Author: xmatthias
    Pinescript Author: ErwinBeckers

    SSL Channels.
    Average over highs and lows form a channel - lines "flip" when close crosses
    either of the 2 lines.
    Trading ideas:
        * Channel cross
        * as confirmation based on up > down for long

    Usage:
        dataframe['sslDown'], dataframe['sslUp'] = SSLChannels(dataframe, 10)
    """
    import talib.abstract as ta

    mode_lower = mode.lower()

    if mode_lower not in ("sma", "ema"):
        raise ValueError(f"Mode {mode} not supported yet")

    df = dataframe.copy()

    if mode_lower == "sma":
        ma_high = df["high"].rolling(length).mean()
        ma_low = df["low"].rolling(length).mean()
    elif mode_lower == "ema":
        ma_high = ta.EMA(df["high"], length)
        ma_low = ta.EMA(df["low"], length)

    df["hlv"] = np.where(df["close"] > ma_high, 1, np.where(df["close"] < ma_low, -1, np.NAN))
    df["hlv"] = df["hlv"].ffill()

    df["sslDown"] = np.where(df["hlv"] < 0, ma_high, ma_low)
    df["sslUp"] = np.where(df["hlv"] < 0, ma_low, ma_high)

    return df["sslDown"], df["sslUp"]


def PMAX(dataframe, period=10, multiplier=3, length=12, MAtype=1, src=1):  # noqa: C901
    """
    Function to compute PMAX
    Source: https://www.tradingview.com/script/sU9molfV/
    Pinescript Author: KivancOzbilgic

    Args :
        df : Pandas DataFrame with the columns ['date', 'open', 'high', 'low', 'close', 'volume']
        period : Integer indicates the period of computation in terms of number of candles
        multiplier : Integer indicates value to multiply the ATR
        length: moving averages length
        MAtype: type of the moving average

    Returns :
        df : Pandas DataFrame with new columns added for
            ATR (ATR_$period)
            PMAX (pm_$period_$multiplier_$length_$Matypeint)
            PMAX Direction (pmX_$period_$multiplier_$length_$Matypeint)
    """
    import talib.abstract as ta

    df = dataframe.copy()
    mavalue = "MA_" + str(MAtype) + "_" + str(length)
    atr = "ATR_" + str(period)
    df[atr] = ta.ATR(df, timeperiod=period)
    pm = "pm_" + str(period) + "_" + str(multiplier) + "_" + str(length) + "_" + str(MAtype)
    pmx = "pmX_" + str(period) + "_" + str(multiplier) + "_" + str(length) + "_" + str(MAtype)
    # MAtype==1 --> EMA
    # MAtype==2 --> DEMA
    # MAtype==3 --> T3
    # MAtype==4 --> SMA
    # MAtype==5 --> VIDYA
    # MAtype==6 --> TEMA
    # MAtype==7 --> WMA
    # MAtype==8 --> VWMA
    if src == 1:
        masrc = df["close"]
    elif src == 2:
        masrc = (df["high"] + df["low"]) / 2
    elif src == 3:
        masrc = (df["high"] + df["low"] + df["close"] + df["open"]) / 4
    if MAtype == 1:
        df[mavalue] = ta.EMA(masrc, timeperiod=length)
    elif MAtype in (2, 9):
        # Compatibility for ZEMA (https://github.com/freqtrade/technical/pull/356 for details)
        df[mavalue] = ta.DEMA(masrc, timeperiod=length)
    elif MAtype == 3:
        df[mavalue] = ta.T3(masrc, timeperiod=length)
    elif MAtype == 4:
        df[mavalue] = ta.SMA(masrc, timeperiod=length)
    elif MAtype == 5:
        df[mavalue] = VIDYA(df, length=length)
    elif MAtype == 6:
        df[mavalue] = ta.TEMA(masrc, timeperiod=length)
    elif MAtype == 7:
        df[mavalue] = ta.WMA(df, timeperiod=length)
    elif MAtype == 8:
        df[mavalue] = vwma(df, length)
    else:
        raise ValueError(f"MAtype {MAtype} not supported.")
    # Compute basic upper and lower bands
    df["basic_ub"] = df[mavalue] + (multiplier * df[atr])
    df["basic_lb"] = df[mavalue] - (multiplier * df[atr])
    # Compute final upper and lower bands
    df["final_ub"] = 0.00
    df["final_lb"] = 0.00
    for i in range(period, len(df)):
        df["final_ub"].iat[i] = (
            df["basic_ub"].iat[i]
            if (
                df["basic_ub"].iat[i] < df["final_ub"].iat[i - 1]
                or df[mavalue].iat[i - 1] > df["final_ub"].iat[i - 1]
            )
            else df["final_ub"].iat[i - 1]
        )
        df["final_lb"].iat[i] = (
            df["basic_lb"].iat[i]
            if (
                df["basic_lb"].iat[i] > df["final_lb"].iat[i - 1]
                or df[mavalue].iat[i - 1] < df["final_lb"].iat[i - 1]
            )
            else df["final_lb"].iat[i - 1]
        )

    # Set the Pmax value
    df[pm] = 0.00
    for i in range(period, len(df)):
        df[pm].iat[i] = (
            df["final_ub"].iat[i]
            if (
                df[pm].iat[i - 1] == df["final_ub"].iat[i - 1]
                and df[mavalue].iat[i] <= df["final_ub"].iat[i]
            )
            else (
                df["final_lb"].iat[i]
                if (
                    df[pm].iat[i - 1] == df["final_ub"].iat[i - 1]
                    and df[mavalue].iat[i] > df["final_ub"].iat[i]
                )
                else (
                    df["final_lb"].iat[i]
                    if (
                        df[pm].iat[i - 1] == df["final_lb"].iat[i - 1]
                        and df[mavalue].iat[i] >= df["final_lb"].iat[i]
                    )
                    else (
                        df["final_ub"].iat[i]
                        if (
                            df[pm].iat[i - 1] == df["final_lb"].iat[i - 1]
                            and df[mavalue].iat[i] < df["final_lb"].iat[i]
                        )
                        else 0.00
                    )
                )
            )
        )

    # Mark the trend direction up/down
    df[pmx] = np.where((df[pm] > 0.00), np.where((df[mavalue] < df[pm]), "down", "up"), np.NaN)
    # Remove basic and final bands from the columns
    df.drop(["basic_ub", "basic_lb", "final_ub", "final_lb", mavalue], inplace=True, axis=1)

    cols = [pm, pmx, atr]
    df.loc[:, cols] = df.loc[:, cols].fillna(0.0)

    return df


def tv_wma(dataframe: DataFrame, length: int = 9, field="close") -> Series:
    """
    Source: Tradingview "Moving Average Weighted"
    Pinescript Author: Unknown

    Args :
        dataframe : Pandas Dataframe
        length : WMA length
        field : Field to use for the calculation

    Returns :
        series : Pandas Series
    """

    if isinstance(dataframe, Series):
        data = dataframe
    else:
        data = dataframe[field]

    norm = 0
    sum = 0

    for i in range(1, length - 1):
        weight = (length - i) * length
        norm = norm + weight
        sum = sum + data.shift(i) * weight

    tv_wma = sum / norm if (norm != 0) else 0
    return tv_wma


def tv_hma(dataframe: DataFrame, length: int = 9, field="close") -> Series:
    """
    Source: Tradingview "Hull Moving Average"
    Pinescript Author: Unknown

    Args :
        dataframe : Pandas Dataframe
        length : HMA length
        field : Field to use for the calculation

    Returns :
        series : Pandas Series
    """

    if isinstance(dataframe, Series):
        data = dataframe
    else:
        data = dataframe[field]

    h = 2 * tv_wma(data, math.floor(length / 2)) - tv_wma(data, length)

    tv_hma = tv_wma(h, math.floor(math.sqrt(length)))

    return tv_hma


def tv_alma(
    dataframe: DataFrame, length: int = 8, offset: int = 0, sigma: int = 0, field="close"
) -> Series:
    """
    Source: Tradingview "Arnaud Legoux Moving Average"
    Links:  https://www.tradingview.com/pine-script-reference/v5/#fun_ta.alma
            https://www.tradingview.com/support/solutions/43000594683/
    Pinescript Author: Arnaud Legoux and Dimitrios Douzis-Loukas
    Description:    Gaussian distribution that is shifted with
                    a calculated offset in order for
                    the average to be biased towards
                    more recent days, instead of more
                    evenly centered on the window.

    Args :
        dataframe : Pandas Dataframe
        length  : ALMA windowframe
        offset  : Shift
        sigma   : Gaussian Smoothing
        field   : Field to use for the calculation

    Returns :
        series : Series of ALMA values
    """

    """ This is simple computation way, just for reference """
    # sigma = sigma or 1e-10
    # m = offset * (length - 1)
    # s = length / sigma
    # norm = 0.0
    # sum = 0.0
    # for i in range(length - 1):
    #     weight = np.exp(-1 * np.power(i - m, 2) / (2 * np.power(s, 2)))
    #     norm += weight
    #     sum += dataframe[field].shift(length - i - 1) * weight
    # return sum / norm

    """ Vectorized method """
    sigma = sigma or 1e-10

    m = offset * (length - 1)
    s = length / sigma

    indices = np.arange(length)
    weights = np.exp(-np.power(indices - m, 2) / (2 * np.power(s, 2)))
    weights /= weights.sum()  # Normalize the weights

    alma = np.convolve(dataframe[field], weights[::-1], mode="valid")
    return Series(np.pad(alma, (length - 1, 0), mode="constant", constant_values=np.nan))


def tv_trama(dataframe: DataFrame, length: int = 99, field="close") -> Series:
    """
    Name : Tradingview "Trend Regularity Adaptive Moving Average"
    Pinescript Author : LuxAlgo
    Link :
        tradingview.com/script/p8wGCPi6-Trend-Regularity-Adaptive-Moving-Average-LuxAlgo/

    Args :
        dataframe : Pandas Dataframe
        length : Period of the indicator
        field : Field to use for the calculation

    Returns :
        series : 'TRAMA' values
    """

    import talib.abstract as ta

    df_len = len(dataframe)

    hh = ta.MAX(dataframe["high"], length)
    ll = ta.MIN(dataframe["low"], length)
    hh_or_ll = np.where(np.diff(hh) > 0, 1, 0) + np.where(np.diff(ll) < 0, 1, 0)

    tc = np.zeros(df_len)
    tc[:-1] = np.nan_to_num(ta.SMA(hh_or_ll.astype(float), length) ** 2)

    ama = np.zeros(df_len)
    ama[0] = dataframe[field].iloc[0]
    for i in range(1, df_len):
        ama[i] = ama[i - 1] + tc[i - 1] * (dataframe[field].iloc[i] - ama[i - 1])

    return Series(ama)
