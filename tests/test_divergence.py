"""Validates technical.indicators.divergence against TradingView Pine Logs CSV exports.


Performs two different tests for different input files. Passing tests
show agreement with the origianl algorithm in Trading View
( "Divergence for many indicator v3" by LonesomeTheBlue).

Both input files are Trading View logs. One input file hides hidden
divergences ("regular") while the other shows them ("hidden").

"""

import os
from pathlib import Path

import numpy
import pandas
import pytest

from technical.indicators.divergence import populate_divergences

TESTDATA_DIR = Path(__file__).parent / "testdata"
REGULAR_CSV = Path(
    os.environ.get(
        "TRADINGVIEW_DIVERGENCE_REGULAR_CSV",
        TESTDATA_DIR / "divergence_tradingview_log_regular.csv",
    )
)
HIDDEN_CSV = Path(
    os.environ.get(
        "TRADINGVIEW_DIVERGENCE_HIDDEN_CSV", TESTDATA_DIR / "divergence_tradingview_log_hidden.csv"
    )
)

WARMUP_CANDLES = 300

FLOAT_COLUMNS = ["mom", "cci", "stk", "vwmacd", "cmf", "mfi"]
PIVOT_COLUMNS = ["ph", "pl"]
REGULAR_COUNT_COLUMNS = ["bearish_divergence", "bullish_divergence"]
HIDDEN_COUNT_COLUMNS = ["bearish_hidden_divergence", "bullish_hidden_divergence"]


def _build_merged(csv_path: Path) -> pandas.DataFrame:
    tradingview_log = pandas.read_csv(csv_path)
    tradingview_log["date"] = pandas.to_datetime(tradingview_log["time"], unit="ms", utc=True)
    tradingview_log = tradingview_log.sort_values("date").reset_index(drop=True)

    ohlcv = tradingview_log[["time", "date", "open", "high", "low", "close", "volume"]].copy()
    result = populate_divergences(ohlcv)

    pivot_idx = [
        i
        for i in (result["ph"].first_valid_index(), result["pl"].first_valid_index())
        if i is not None
    ]
    start = max(WARMUP_CANDLES, max(pivot_idx) + 1) if pivot_idx else WARMUP_CANDLES

    combined = result.merge(tradingview_log, on="date", suffixes=("", "_tv"))
    return combined.iloc[start:].reset_index(drop=True)


@pytest.fixture
def merged_regular():
    if not REGULAR_CSV.exists():
        pytest.skip("regular (showhidden=false) TradingView fixture not present")
    return _build_merged(REGULAR_CSV)


@pytest.fixture
def merged_hidden():
    if not HIDDEN_CSV.exists():
        pytest.skip("hidden (showhidden=true) TradingView fixture not present")
    return _build_merged(HIDDEN_CSV)


@pytest.mark.parametrize("column", FLOAT_COLUMNS)
def test_indicator_matches_tradingview(merged_regular, column):
    assert numpy.allclose(
        merged_regular[column], merged_regular[f"{column}_tv"], atol=1e-4, rtol=1e-3, equal_nan=True
    )


@pytest.mark.parametrize("column", PIVOT_COLUMNS)
def test_pivot_matches_tradingview(merged_regular, column):
    assert numpy.allclose(
        merged_regular[column], merged_regular[f"{column}_tv"], atol=1e-8, equal_nan=True
    )


@pytest.mark.parametrize("column", REGULAR_COUNT_COLUMNS)
def test_regular_divergence_count_matches_tradingview(merged_regular, column):
    mismatches = merged_regular.index[merged_regular[column] != merged_regular[f"{column}_tv"]]
    assert mismatches.empty, f"{column} mismatch at rows: {list(mismatches)}"


@pytest.mark.parametrize("column", HIDDEN_COUNT_COLUMNS)
def test_hidden_divergence_count_matches_tradingview(merged_hidden, column):
    mismatches = merged_hidden.index[merged_hidden[column] != merged_hidden[f"{column}_tv"]]
    assert mismatches.empty, f"{column} mismatch at rows: {list(mismatches)}"
