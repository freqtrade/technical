import numpy as np
import talib.abstract as ta
from pandas import DataFrame, Series


def supertrend(dataframe: DataFrame, multiplier: int = 10, period: int = 3) -> DataFrame:
    """
    Calculate SuperTrend indicator

    :param dataframe: dataframe containing 'date', 'open', 'high', 'low', 'close', 'volume' columns
    :param multiplier: multiplier for ATR
    :param period: period for ATR calculation
    :return: Tuple of two series, SuperTrend value and SuperTrend direction

    Usage:
        `dataframe['ST'], dataframe['STX'] = supertrend(dataframe)`
    """
    df = dataframe.copy()
    high = df["high"].values
    low = df["low"].values
    close = df["close"].values
    length = len(df)

    # TR and ATR
    tr = ta.TRANGE(df["high"], df["low"], df["close"])
    atr = Series(tr).rolling(period).mean().to_numpy()

    # basic upper / lower bands
    basic_ub = (high + low) / 2 + multiplier * atr
    basic_lb = (high + low) / 2 - multiplier * atr

    # final upper / lower bands
    final_ub = np.zeros(length)
    final_lb = np.zeros(length)

    for i in range(period, length):
        final_ub[i] = (
            basic_ub[i]
            if basic_ub[i] < final_ub[i - 1] or close[i - 1] > final_ub[i - 1]
            else final_ub[i - 1]
        )
        final_lb[i] = (
            basic_lb[i]
            if basic_lb[i] > final_lb[i - 1] or close[i - 1] < final_lb[i - 1]
            else final_lb[i - 1]
        )

    # ST calculation
    st = np.zeros(length)
    for i in range(period, length):
        if st[i - 1] == final_ub[i - 1]:
            st[i] = final_ub[i] if close[i] <= final_ub[i] else final_lb[i]
        elif st[i - 1] == final_lb[i - 1]:
            st[i] = final_lb[i] if close[i] >= final_lb[i] else final_ub[i]

    # STX direction
    stx = np.where(st > 0, np.where(close < st, "down", "up"), None)

    return st, stx
