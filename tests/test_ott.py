"""
test_ott_indicator_2.py

Validates ott_indicator_2.ott() / get_ma() against an independent,
bar-by-bar transcription of the original OTT Pine Script
(https://tr.tradingview.com/script/zVhoDQME/) -- not against the module's
own internals -- so a bug shared between the reference and the
implementation is the only way these tests could give a false pass.

Run with: pytest test_ott_indicator_2.py -v
"""

import numpy as np
import pandas as pd
import pytest

from technical.indicators import get_ma, ott

# --------------------------------------------------------------------------
# Independent reference implementation (transcribed directly from the Pine
# source pasted by the user, not from ott_indicator_2.py)
# --------------------------------------------------------------------------


def _ref_ma(close: pd.Series, length: int, matype: str, cmo_length: int = 9) -> pd.Series:
    matype = matype.upper()
    if matype == "SMA":
        return close.rolling(length).mean()
    if matype == "EMA":
        return close.ewm(span=length, adjust=False).mean()
    if matype == "WMA":
        w = np.arange(1, length + 1)
        return close.rolling(length).apply(lambda x: np.dot(x, w) / w.sum(), raw=True)
    if matype == "TMA":
        h1, h2 = int(np.ceil(length / 2)), int(np.floor(length / 2)) + 1
        return close.rolling(h1).mean().rolling(h2).mean()
    if matype == "VAR":
        alpha = 2 / (length + 1)
        diff = close.diff()
        vud = diff.clip(lower=0).rolling(cmo_length).sum()
        vdd = (-diff).clip(lower=0).rolling(cmo_length).sum()
        cmo = ((vud - vdd) / (vud + vdd)).fillna(0).values
        c = close.values
        out = np.zeros(len(close))
        for i in range(1, len(close)):
            out[i] = alpha * abs(cmo[i]) * c[i] + (1 - alpha * abs(cmo[i])) * out[i - 1]
        return pd.Series(out, index=close.index)
    if matype == "WWMA":
        alpha = 1 / length
        c = close.values
        out = np.zeros(len(close))
        for i in range(1, len(close)):
            out[i] = alpha * c[i] + (1 - alpha) * out[i - 1]
        return pd.Series(out, index=close.index)
    if matype == "ZLEMA":
        lag = length // 2 if length % 2 == 0 else (length - 1) // 2
        zx = close + (close - close.shift(lag))
        return zx.ewm(span=length, adjust=False).mean()
    if matype == "TSF":
        def lr(x):
            idx = np.arange(len(x))
            slope, intercept = np.polyfit(idx, x, 1)
            lrc = slope * (len(x) - 1) + intercept
            lrc1 = slope * (len(x) - 2) + intercept
            return lrc + (lrc - lrc1)
        return close.rolling(length).apply(lr, raw=True)
    raise ValueError(matype)


def pine_reference_ott(close: pd.Series, length=2, percent=1.4, matype="VAR", cmo_length=9):
    """Bar-by-bar transcription of the OTT Pine Script's trailing-stop recursion."""
    ma = _ref_ma(close, length, matype, cmo_length)
    fark = ma * percent * 0.01

    n = len(close)
    long_stop = np.full(n, np.nan)
    short_stop = np.full(n, np.nan)
    direction = np.ones(n, dtype=int)
    ott_line = np.full(n, np.nan)
    ma_v, fark_v = ma.values, fark.values

    for i in range(n):
        if np.isnan(ma_v[i]):
            continue
        ls, ss = ma_v[i] - fark_v[i], ma_v[i] + fark_v[i]
        if i == 0 or np.isnan(long_stop[i - 1]):
            pls, pss, pdir = ls, ss, 1
        else:
            pls, pss, pdir = long_stop[i - 1], short_stop[i - 1], direction[i - 1]

        long_stop[i] = max(ls, pls) if ma_v[i] > pls else ls
        short_stop[i] = min(ss, pss) if ma_v[i] < pss else ss

        if pdir == -1 and ma_v[i] > pss:
            direction[i] = 1
        elif pdir == 1 and ma_v[i] < pls:
            direction[i] = -1
        else:
            direction[i] = pdir

        mt = long_stop[i] if direction[i] == 1 else short_stop[i]
        ott_line[i] = mt * (200 + percent) / 200 if ma_v[i] > mt else mt * (200 - percent) / 200

    return pd.Series(ott_line, index=close.index)


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ohlcv():
    rng = np.random.default_rng(42)
    n = 400
    close = 100 + np.cumsum(rng.normal(0, 1, n))
    idx = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame(
        {
            "date": idx,
            "open": close,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": 1.0,
        }
    )


@pytest.fixture(scope="module")
def trending():
    """Deterministic V-shaped series: strong sustained downtrend, then uptrend."""
    down = 200 - np.arange(60) * 2.0
    up = down[-1] + np.arange(60) * 2.0
    close = np.concatenate([down, up])
    idx = pd.date_range("2024-01-01", periods=len(close), freq="h")
    return pd.DataFrame(
        {
            "date": idx,
            "open": close,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": 1.0,
        }
    )


# --------------------------------------------------------------------------
# Tests: every MA type matches the independent Pine reference bar-for-bar
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "matype,length,percent",
    [
        ("SMA", 10, 1.4),
        ("EMA", 10, 1.4),
        ("WMA", 10, 1.0),
        ("TMA", 8, 1.0),
        ("VAR", 2, 1.4),
        ("WWMA", 7, 1.0),
        ("ZLEMA", 5, 1.0),
        ("TSF", 12, 1.0),
    ],
)
def test_matches_pine_reference(ohlcv, matype, length, percent):
    result = ott(ohlcv, length=length, percent=percent, matype=matype)
    ref = pine_reference_ott(ohlcv["close"], length, percent, matype)
    pd.testing.assert_series_equal(
        result["ott"].reset_index(drop=True),
        ref.reset_index(drop=True),
        check_names=False,
        atol=1e-9,
    )


def test_var_cmo_length_matches_reference(ohlcv):
    """cmo_length decoupled from length should still match the reference exactly."""
    result = ott(ohlcv, length=2, percent=1.4, matype="VAR", cmo_length=20)
    ref = pine_reference_ott(ohlcv["close"], 2, 1.4, "VAR", cmo_length=20)
    pd.testing.assert_series_equal(
        result["ott"].reset_index(drop=True),
        ref.reset_index(drop=True),
        check_names=False,
        atol=1e-9,
    )


# --------------------------------------------------------------------------
# Tests: structural properties any correct OTT implementation must have
# --------------------------------------------------------------------------


def test_ott_shifted2_is_ott_shifted_by_two_bars(ohlcv):
    result = ott(ohlcv, length=2, percent=1.4, matype="VAR")
    pd.testing.assert_series_equal(
        result["ott_shifted2"].reset_index(drop=True),
        result["ott"].shift(2).reset_index(drop=True),
        check_names=False,
    )


def test_direction_tracks_strong_trend(trending):
    """
    Per the indicator's own definition: in a sustained downtrend OTT should
    sit above price; in a sustained uptrend it should sit below price.
    """
    result = ott(trending, length=2, percent=1.4, matype="VAR")
    deep_down = result.iloc[40:59]  # well into the downtrend leg
    deep_up = result.iloc[100:119]  # well into the uptrend leg

    assert (deep_down["close"] < deep_down["ott"]).all()
    assert (deep_up["close"] > deep_up["ott"]).all()


def test_percent_band_scales_distance_from_ma(ohlcv):
    """A larger `percent` should widen the average |ma - ott| gap."""
    tight = ott(ohlcv, length=5, percent=0.5, matype="EMA")
    wide = ott(ohlcv, length=5, percent=3.0, matype="EMA")
    gap_tight = (tight["ott_ma"] - tight["ott"]).abs().mean()
    gap_wide = (wide["ott_ma"] - wide["ott"]).abs().mean()
    assert gap_wide > gap_tight


def test_invalid_matype_raises(ohlcv):
    with pytest.raises(ValueError):
        get_ma(ohlcv, "close", 10, matype="NOT_A_TYPE")


def test_no_nans_after_warmup(ohlcv):
    result = ott(ohlcv, length=10, percent=1.4, matype="SMA")
    assert result["ott"].iloc[30:].isna().sum() == 0


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
