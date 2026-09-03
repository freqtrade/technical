"""
Optimized Trend Tracker (OTT) indicator for freqtrade strategies.

Usage:

    from technical.indicators import ott

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = ott(dataframe, src_col="close", length=2, percent=1.4, matype="VAR")
        return dataframe
"""

import numpy as np
import pandas as pd
import talib.abstract as ta

from technical.vendor.qtpylib.indicators import zlema as _lib_zlema

from .indicators import VIDYA as _lib_vidya

__all__ = ["ott"]


def _ema(series: pd.Series, length: int) -> pd.Series:
    """EMA."""
    return series.ewm(span=length, adjust=False).mean()


def _zlema(series: pd.Series, length: int) -> pd.Series:
    """Zero Lag EMA."""
    lag = length // 2
    zx = series + (series - series.shift(lag))
    return zx.ewm(span=length, adjust=False).mean()


def _wwma(series: pd.Series, length: int) -> pd.Series:
    """Welles Wilder's Moving Average."""
    alpha = 1 / length
    src = series.values
    out = np.zeros(len(series))
    for i in range(1, len(series)):
        out[i] = alpha * src[i] + (1 - alpha) * out[i - 1]
    return pd.Series(out, index=series.index)


def _tma(series: pd.Series, length: int) -> pd.Series:
    """Triangular Moving Average."""
    half1 = int(np.ceil(length / 2))
    half2 = int(np.floor(length / 2)) + 1
    return series.rolling(half1).mean().rolling(half2).mean()


def _get_ma(
    dataframe: pd.DataFrame,
    src_col: str,
    length: int,
    matype: str = "VAR",
    use_technical_lib: bool = False,
    cmo_length: int = 9,
) -> pd.Series:
    """Dispatches to the requested moving-average type."""
    matype = matype.upper()
    series = dataframe[src_col]

    if matype == "SMA":
        result = ta.SMA(series, timeperiod=length)
    elif matype == "EMA":
        result = _ema(series, length)
    elif matype == "WMA":
        result = ta.WMA(series, timeperiod=length)
    elif matype == "TMA":
        result = _tma(series, length)
    elif matype == "VAR":
        vidya_df = dataframe[[src_col]].rename(columns={src_col: "close"})
        result = _lib_vidya(vidya_df, length=length, cmo_length=cmo_length, select=True)
    elif matype == "WWMA":
        result = _wwma(series, length)
    elif matype == "ZLEMA":
        result = _lib_zlema(series, length) if use_technical_lib else _zlema(series, length)
    elif matype == "TSF":
        result = ta.TSF(series, timeperiod=length)
    else:
        raise ValueError(f"Unknown moving average type: {matype}")

    if not isinstance(result, pd.Series):
        result = pd.Series(np.asarray(result), index=dataframe.index)
    return result


def ott(
    dataframe: pd.DataFrame,
    src_col: str = "close",
    length: int = 2,
    percent: float = 1.4,
    matype: str = "VAR",
    use_technical_lib: bool = False,
    cmo_length: int = 9,
) -> pd.DataFrame:
    """
    Adds OTT columns to a freqtrade OHLCV dataframe.

    New columns: ott_ma, ott, ott_shifted2.
    """
    df = dataframe.copy()
    ma = _get_ma(df, src_col, length, matype, use_technical_lib, cmo_length)
    fark = ma * percent * 0.01

    ma_vals = ma.values
    fark_vals = fark.values
    n = len(df)

    long_stop = np.full(n, np.nan)
    short_stop = np.full(n, np.nan)
    direction = np.ones(n, dtype=int)
    mt = np.full(n, np.nan)
    ott_raw = np.full(n, np.nan)

    for i in range(n):
        if np.isnan(ma_vals[i]):
            continue

        ls = ma_vals[i] - fark_vals[i]
        ss = ma_vals[i] + fark_vals[i]

        if i == 0 or np.isnan(long_stop[i - 1]):
            prev_long_stop, prev_short_stop, prev_dir = ls, ss, 1
        else:
            prev_long_stop = long_stop[i - 1]
            prev_short_stop = short_stop[i - 1]
            prev_dir = direction[i - 1]

        long_stop[i] = max(ls, prev_long_stop) if ma_vals[i] > prev_long_stop else ls
        short_stop[i] = min(ss, prev_short_stop) if ma_vals[i] < prev_short_stop else ss

        if prev_dir == -1 and ma_vals[i] > prev_short_stop:
            direction[i] = 1
        elif prev_dir == 1 and ma_vals[i] < prev_long_stop:
            direction[i] = -1
        else:
            direction[i] = prev_dir

        mt[i] = long_stop[i] if direction[i] == 1 else short_stop[i]
        ott_raw[i] = (
            mt[i] * (200 + percent) / 200 if ma_vals[i] > mt[i] else mt[i] * (200 - percent) / 200
        )

    df["ott_ma"] = ma
    df["ott"] = ott_raw
    df["ott_shifted2"] = pd.Series(ott_raw, index=df.index).shift(2)

    return df
