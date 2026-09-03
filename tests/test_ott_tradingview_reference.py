"""
test_ott_tradingview_reference.py

Compares technical.indicators.ott() against values logged directly from
the real Pine Script running on TradingView.
"""

import os

import pandas as pd

from technical.indicators import ott

REFERENCE_CSV = os.path.join(os.path.dirname(__file__), "testdata", "ott_pine_reference.csv")
TOLERANCE = 1e-6
MAX_CONVERGENCE_BARS = 120


def _load_reference():
    return pd.read_csv(REFERENCE_CSV)


def _first_stable_index(diff: pd.Series, tol: float) -> int | None:
    matched = diff <= tol
    for i in range(len(matched)):
        if matched.iloc[i:].all():
            return i
    return None


def _check_convergence(name: str, actual: pd.Series, expected: pd.Series, tol: float) -> int:
    diff = (actual - expected).abs()
    stabilize_at = _first_stable_index(diff, tol)
    n = len(actual)
    if stabilize_at is None:
        print(f"{name}: never converges within {n} bars (max diff {diff.max():.6g})")
    else:
        print(
            f"{name}: converges at bar {stabilize_at}/{n}, exact match for remaining {n - stabilize_at} bars"
        )
    return stabilize_at


def test_ott_matches_tradingview_reference():
    pine = _load_reference()
    df = pine[["open", "high", "low", "close", "volume"]].copy()

    result = ott(df, src_col="close", length=2, percent=1.4, matype="VAR")

    ma_stabilize_at = _check_convergence(
        "ott_ma vs MAvg", result["ott_ma"], pine["MAvg"], TOLERANCE
    )
    ott_stabilize_at = _check_convergence("ott vs OTT", result["ott"], pine["OTT"], TOLERANCE)
    shifted_stabilize_at = _check_convergence(
        "ott_shifted2 vs OTT.shift(2)", result["ott_shifted2"], pine["OTT"].shift(2), TOLERANCE
    )

    assert ott_stabilize_at is not None, "ott() never converges to the TradingView reference"
    assert ott_stabilize_at < MAX_CONVERGENCE_BARS, (
        f"took {ott_stabilize_at} bars to converge to the TradingView reference"
    )

    for name, stabilize_at, actual, expected in [
        ("ott_ma", ma_stabilize_at, result["ott_ma"], pine["MAvg"]),
        ("ott", ott_stabilize_at, result["ott"], pine["OTT"]),
        ("ott_shifted2", shifted_stabilize_at, result["ott_shifted2"], pine["OTT"].shift(2)),
    ]:
        assert stabilize_at is not None, f"{name} never converges to the TradingView reference"
        pd.testing.assert_series_equal(
            actual.iloc[stabilize_at:].reset_index(drop=True),
            expected.iloc[stabilize_at:].reset_index(drop=True),
            check_names=False,
            atol=TOLERANCE,
        )
