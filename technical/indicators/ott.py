"""
Optimized Trend Tracker (OTT) — pandas port for freqtrade strategies (v2).

Refactored from the original one-file port to reuse existing `technical` /
TA-Lib functionality wherever a genuine equivalent already exists, instead
of reimplementing it from scratch.

REUSED AS-IS (non-recursive/windowed calculations, verified exact match
against the Pine reference in test_ott_indicator_2.py):
    - SMA / WMA -> talib.abstract.SMA / WMA
    - TSF       -> talib.abstract.TSF ("Time Series Forecast" is the same
                    linear-regression-extrapolation math as Pine's
                    linreg-based TSF)

CHECKED, BUT *NOT* REUSED -- discrepancy found via the test suite:
    - EMA: talib.abstract.EMA seeds its recursion with an SMA of the first
      `timeperiod` bars and returns NaN until that seed is ready. Pine's
      built-in ema() is a simple recursive EMA seeded with the first price,
      with no warm-up NaN period -- equivalent to
      `series.ewm(span=length, adjust=False).mean()`, which is what the
      original ott_indicator.py used. The two conventions only converge
      asymptotically, not exactly, and disagree entirely during warm-up.
      Kept as a custom `_ema` that matches Pine exactly; there's no
      opt-in to the talib version here since there's no legitimate reason
      to prefer the mismatched behaviour.

CHECKED, BUT *NOT* REUSED BY DEFAULT (the "equivalent" library function
turns out to compute something subtly different from Pine's OTT):
    - VAR / VIDYA: technical.indicators.VIDYA() sums its Chande Momentum
      Oscillator over a rolling window of `length` bars
      (`df["m1"].rolling(length).sum()`). Pine's OTT VAR hardcodes that
      window to 9 bars regardless of the OTT `length` parameter
      (`vUD = sum(vud1, 9)` in the source script). OTT is normally run
      with a short length (2-3), so silently swapping in VIDYA() would
      change the indicator's actual output. Kept as a custom `_var_ma`
      that matches Pine bar-for-bar by default; the library version is
      offered as an explicit opt-in (`use_technical_lib=True`) for anyone
      who's fine with that difference. `_var_ma` also exposes the CMO
      window as its own `cmo_length` parameter (default 9, matching both
      Pine's hardcoded value and the conventional default for Chande's
      CMO) so it can be tuned independently of the EMA/averaging `length`
      -- this mirrors Chande's original 1995 VIDYA design, which treats
      the two as separate knobs rather than one.
    - ZLEMA: technical.vendor.qtpylib.indicators.zlema() computes
      lag = (window - 1) // 2 (Pine: length/2, rounded) and then applies a
      *WMA* of period `lag` to the delagged series
      (`wma(series, lag, min_periods)`) rather than an *EMA* of period
      `window`, which is what Pine's `ema(zxEMAData, length)` actually
      does. Same "zero-lag" family of idea, materially different formula
      and output. Kept as a custom `_zlema` that matches Pine bar-for-bar;
      same `use_technical_lib=True` opt-in applies.

STILL ORIGINAL TO THIS MODULE (no equivalent found anywhere in
`technical` or TA-Lib):
    - WWMA (Welles Wilder's Moving Average)
    - TMA  (Triangular Moving Average)
    - the OTT trailing-stop / direction state machine itself

Requires: pandas, numpy, ta-lib, technical (all already part of a normal
freqtrade + `technical` install).

Usage inside a freqtrade IStrategy:

    from ott_indicator_2 import ott

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = ott(dataframe, src_col="close", length=2, percent=1.4, matype="VAR")
        return dataframe
"""



import numpy as np
import pandas as pd
import talib.abstract as ta

from .indicators import VIDYA as _lib_vidya
from ..vendor.qtpylib.indicators import zlema as _lib_zlema

__all__ = ["ott", "get_ma"]

def _var_ma(series: pd.Series, length: int, cmo_length: int = 9) -> pd.Series:
    """
    VIDYA ('VAR' MA type).

    Two independent lookbacks, per Chande's original 1995 design:
        length     - the EMA/averaging period (smoothing speed)
        cmo_length - the Chande Momentum Oscillator period used to measure
                     volatility (defaults to 9, the conventional CMO
                     default, which is also what Pine's OTT script
                     hardcodes). Set this equal to `length` to reproduce
                     technical.indicators.VIDYA()'s behaviour instead.
    """
    alpha = 2 / (length + 1)
    diff = series.diff()
    vud = diff.clip(lower=0)
    vdd = (-diff).clip(lower=0)
    v_ud = vud.rolling(cmo_length).sum()
    v_dd = vdd.rolling(cmo_length).sum()
    v_cmo = ((v_ud - v_dd) / (v_ud + v_dd)).fillna(0)

    src = series.values
    cmo = v_cmo.values
    out = np.zeros(len(series))
    for i in range(1, len(series)):
        out[i] = alpha * abs(cmo[i]) * src[i] + (1 - alpha * abs(cmo[i])) * out[i - 1]
    return pd.Series(out, index=series.index)


def _ema(series: pd.Series, length: int) -> pd.Series:
    """
    EMA, matching Pine's built-in ema() exactly: a simple recursive EMA
    seeded with the first price, no warm-up NaN period.

    NOT reused from talib.abstract.EMA -- that function seeds its recursion
    with an SMA of the first `timeperiod` bars and returns NaN before that
    seed is ready, which is a materially different (and non-equivalent,
    only asymptotically converging) result versus Pine's ema(). Discovered
    via the project's own bar-for-bar Pine-reference test suite.
    """
    return series.ewm(span=length, adjust=False).mean()


def _zlema(series: pd.Series, length: int) -> pd.Series:
    """Zero Lag EMA, matching Pine's OTT exactly: EMA of period `length`."""
    lag = length // 2 if length % 2 == 0 else (length - 1) // 2
    zx = series + (series - series.shift(lag))
    return zx.ewm(span=length, adjust=False).mean()


def _wwma(series: pd.Series, length: int) -> pd.Series:
    """Welles Wilder's Moving Average -- no equivalent in technical/TA-Lib."""
    alpha = 1 / length
    src = series.values
    out = np.zeros(len(series))
    for i in range(1, len(series)):
        out[i] = alpha * src[i] + (1 - alpha) * out[i - 1]
    return pd.Series(out, index=series.index)


def _tma(series: pd.Series, length: int) -> pd.Series:
    """Triangular Moving Average -- no equivalent in technical/TA-Lib."""
    half1 = int(np.ceil(length / 2))
    half2 = int(np.floor(length / 2)) + 1
    return series.rolling(half1).mean().rolling(half2).mean()


def get_ma(
    dataframe: pd.DataFrame,
    src_col: str,
    length: int,
    matype: str = "VAR",
    use_technical_lib: bool = False,
    cmo_length: int = 9,
) -> pd.Series:
    """
    Dispatches to the requested moving-average type.

    use_technical_lib:
        False (default) - VAR/ZLEMA use the custom, Pine-exact implementations.
        True            - VAR/ZLEMA reuse technical's VIDYA()/zlema() instead.
                           Numerically different from the original OTT script
                           (see module docstring) -- only set this if that
                           tradeoff is acceptable for your use case. Note
                           technical.indicators.VIDYA() ties its CMO window
                           to `length`, so cmo_length has no effect here --
                           set length == desired cmo_length if you need them
                           to match under this mode.
    cmo_length:
        Only used when matype == "VAR" and use_technical_lib is False.
        The lookback for VIDYA's Chande Momentum Oscillator (the volatility
        measure), independent of `length` (the EMA/averaging period) --
        this is how Chande's original 1995 design treats them: two
        separate knobs. Defaults to 9, the conventional CMO default and
        what Pine's OTT script hardcodes. Set cmo_length == length to
        collapse them into a single-parameter VIDYA, matching how
        technical.indicators.VIDYA() behaves.
    """
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
        if use_technical_lib:
            vidya_df = dataframe[[src_col]].rename(columns={src_col: "close"})
            result = _lib_vidya(vidya_df, length=length, select=True)
        else:
            result = _var_ma(series, length, cmo_length)
    elif matype == "WWMA":
        result = _wwma(series, length)
    elif matype == "ZLEMA":
        result = _lib_zlema(series, length) if use_technical_lib else _zlema(series, length)
    elif matype == "TSF":
        result = ta.TSF(series, timeperiod=length)
    else:
        raise ValueError(f"Unknown moving average type: {matype}")

    # talib.abstract functions can return a bare numpy.ndarray instead of a
    # pandas.Series depending on the installed ta-lib-python version -- always
    # normalise to a Series indexed like the input so downstream code
    # (ott()'s use of `.values`, pandas alignment, etc.) behaves consistently
    # regardless of which version produced `result`.
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

    New columns:
        ott_ma        - the selected moving average ("support line")
        ott           - the raw OTT stop/trend line
        ott_shifted2  - ott shifted 2 bars forward, matching the OTT[2] plot
                         in the original script (use this one for crosses,
                         since that's what's actually plotted on the chart)

    cmo_length:
        Only relevant when matype="VAR" and use_technical_lib=False. See
        get_ma() docstring -- defaults to 9 (Pine's OTT / conventional CMO
        default). Adjust independently of `length` if desired.
    """
    df = dataframe.copy()
    ma = get_ma(df, src_col, length, matype, use_technical_lib, cmo_length)
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
            mt[i] * (200 + percent) / 200
            if ma_vals[i] > mt[i]
            else mt[i] * (200 - percent) / 200
        )

    df["ott_ma"] = ma
    df["ott"] = ott_raw
    df["ott_shifted2"] = pd.Series(ott_raw, index=df.index).shift(2)

    return df
