import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from technical.indicators import trend_trader


def bars(closes):
    return pd.DataFrame(
        {"close": closes, "high": np.array(closes) + 1, "low": np.array(closes) - 1},
        index=pd.date_range("2024-01-01", periods=len(closes)),
    )


def test_reference_and_no_lookahead():
    frame = bars([10, 11, 12, 13, 14, 9, 8, 10, 15, 15, 12, 6, 7])
    # Independently calculate each rolling window and carry the prior state.
    length, multiplier = 3, 1.0
    previous_line, previous_direction = frame.close.iloc[0], 0
    lines, directions = [], []
    for i, close in enumerate(frame.close):
        if i >= length:
            ranges = [
                max(
                    frame.high.iloc[j] - frame.low.iloc[j],
                    abs(frame.high.iloc[j] - frame.close.iloc[j - 1]) if j else 0,
                    abs(frame.low.iloc[j] - frame.close.iloc[j - 1]) if j else 0,
                )
                for j in range(i - length, i)
            ]
            average = sum((j + 1) * value for j, value in enumerate(ranges)) / 6
            window = frame.close.iloc[i - length : i]
            upper, lower = max(window) - multiplier * average, min(window) + multiplier * average
            if close > max(upper, lower):
                previous_line = upper
            elif close < min(upper, lower):
                previous_line = lower
        previous_direction = (
            1 if close > previous_line else -1 if close < previous_line else previous_direction
        )
        lines.append(previous_line)
        directions.append(previous_direction)
    original = frame.copy(deep=True)
    result = trend_trader(frame, length=length, multiplier=multiplier)
    np.testing.assert_allclose(result.trend, lines)
    np.testing.assert_array_equal(result.direction, directions)
    assert set(directions) == {-1, 0, 1}
    assert_frame_equal(frame, original)
    assert_frame_equal(trend_trader(frame.iloc[:9], length, multiplier), result.iloc[:9])


def test_defaults_empty_and_short_history():
    frame = bars([10, 11, 9])
    result = trend_trader(frame)
    np.testing.assert_array_equal(result.trend, [10, 10, 10])
    np.testing.assert_array_equal(result.direction, [0, 1, -1])
    assert result.index.equals(frame.index)
    assert list(trend_trader(frame.iloc[:0]).columns) == ["trend", "direction"]


@pytest.mark.parametrize("length,multiplier", [(0, 3), (2, 0), (2, -1)])
def test_invalid_parameters(length, multiplier):
    with pytest.raises(ValueError):
        trend_trader(bars([10, 11]), length, multiplier)


def test_one_period_and_nondefault_index():
    frame = bars([10, 20, 5])
    frame.index = [12, 25, 97]
    result = trend_trader(frame, length=1, multiplier=1)
    np.testing.assert_allclose(result.trend, [10, 8, 31])
    np.testing.assert_array_equal(result.direction, [0, 1, -1])
    assert result.index.equals(frame.index)
