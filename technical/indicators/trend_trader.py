import numpy as np
import talib.abstract as ta
from pandas import DataFrame, Series


def trend_trader(dataframe: DataFrame, length: int = 21, multiplier: float = 3.0) -> DataFrame:
    """Calculate Andrew Abraham's Trend Trader trailing level and direction.

    The limits use the previous bar's rolling highest/lowest close and weighted
    average true range. The level is carried forward unless the current close
    crosses both limits. Direction is 1 above the level, -1 below it, and retains
    its previous value on equality. Before the limits are available, the level
    is initialized to the first close and direction starts at zero.

    Returns ``trend`` and ``direction`` columns on the input index without
    modifying the input. See technical issue #274 for the requested indicator.
    """
    if length < 1:
        raise ValueError("length must be greater than zero")
    if not np.isfinite(multiplier) or multiplier <= 0:
        raise ValueError("multiplier must be finite and greater than zero")
    close = dataframe["close"].to_numpy(dtype=float)
    if not len(close):
        return DataFrame(index=dataframe.index, columns=["trend", "direction"], dtype=float)

    true_range = Series(ta.TRANGE(dataframe), index=dataframe.index)
    # With no previous close, the first true range is the bar's high-low range.
    true_range.iloc[0] = float(dataframe["high"].iloc[0] - dataframe["low"].iloc[0])
    # WMA requires at least two periods; a one-period weighted mean is the input.
    average = ta.WMA(true_range, timeperiod=length) if length > 1 else true_range
    average = Series(average, index=dataframe.index)
    upper = dataframe["close"].rolling(length).max().shift(1) - average.shift(1) * multiplier
    lower = dataframe["close"].rolling(length).min().shift(1) + average.shift(1) * multiplier
    levels = np.empty(len(close))
    directions = np.zeros(len(close), dtype=int)
    level, direction = close[0], 0
    for i, (price, high, low) in enumerate(zip(close, upper, lower, strict=True)):
        if price > high and price > low:
            level = high
        elif price < low and price < high:
            level = low
        direction = 1 if price > level else -1 if price < level else direction
        levels[i], directions[i] = level, direction
    return DataFrame({"trend": levels, "direction": directions}, index=dataframe.index)
