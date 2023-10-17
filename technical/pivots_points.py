"""
Indicators for Freqtrade
author@: Gerald Lonlas
"""

import numpy as np
import pandas as pd

def pivots_points(dataframe: pd.DataFrame, timeperiod=30, levels=3) -> pd.DataFrame:
    """
    Pivots Points
    Formula:
    Pivot = (Previous High + Previous Low + Previous Close) / 3

    Resistance #1 = (2 * Pivot) - Previous Low
    Support #1 = (2 * Pivot) - Previous High

    Resistance #2 = (Pivot - Support #1) + Resistance #1
    Support #2 = Pivot - (Resistance #1 - Support #1)

    Resistance #3 = (Pivot - Support #2) + Resistance #2
    Support #3 = Pivot - (Resistance #2 - Support #2)
    ...

    :param dataframe:
    :param timeperiod: Period to compare (in ticker)
    :param levels: Num of support/resistance desired
    :return: dataframe
    """

    typical_price = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3
    data = {"pivot": typical_price}

    for i in range(1, levels + 1):
        data[f"r{i}"] = 2 * data["pivot"] - dataframe['low']
        data[f"s{i}"] = 2 * data["pivot"] - dataframe['high']

    for i in range(2, levels + 1):
        prev_support = data[f"s{i - 1}"]
        prev_resistance = data[f"r{i - 1}"]

        data[f"r{i}"] = (data["pivot"] - prev_support) + prev_resistance
        data[f"s{i}"] = data["pivot"] - (prev_resistance - prev_support)

    return pd.DataFrame(data)



