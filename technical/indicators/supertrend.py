import numpy as np
import talib.abstract as ta
from pandas import DataFrame


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

    df["TR"] = ta.TRANGE(df)
    df["ATR"] = ta.SMA(df["TR"], period)

    st = "ST_" + str(period) + "_" + str(multiplier)
    stx = "STX_" + str(period) + "_" + str(multiplier)

    # Compute basic upper and lower bands
    df["basic_ub"] = (df["high"] + df["low"]) / 2 + multiplier * df["ATR"]
    df["basic_lb"] = (df["high"] + df["low"]) / 2 - multiplier * df["ATR"]

    # Compute final upper and lower bands
    df["final_ub"] = 0.00
    df["final_lb"] = 0.00
    for i in range(period, len(df)):
        df["final_ub"].iat[i] = (
            df["basic_ub"].iat[i]
            if df["basic_ub"].iat[i] < df["final_ub"].iat[i - 1]
            or df["close"].iat[i - 1] > df["final_ub"].iat[i - 1]
            else df["final_ub"].iat[i - 1]
        )
        df["final_lb"].iat[i] = (
            df["basic_lb"].iat[i]
            if df["basic_lb"].iat[i] > df["final_lb"].iat[i - 1]
            or df["close"].iat[i - 1] < df["final_lb"].iat[i - 1]
            else df["final_lb"].iat[i - 1]
        )

    # Set the supertrend value
    df[st] = 0.00
    for i in range(period, len(df)):
        df[st].iat[i] = (
            df["final_ub"].iat[i]
            if df[st].iat[i - 1] == df["final_ub"].iat[i - 1]
            and df["close"].iat[i] <= df["final_ub"].iat[i]
            else df["final_lb"].iat[i]
            if df[st].iat[i - 1] == df["final_ub"].iat[i - 1]
            and df["close"].iat[i] > df["final_ub"].iat[i]
            else df["final_lb"].iat[i]
            if df[st].iat[i - 1] == df["final_lb"].iat[i - 1]
            and df["close"].iat[i] >= df["final_lb"].iat[i]
            else df["final_ub"].iat[i]
            if df[st].iat[i - 1] == df["final_lb"].iat[i - 1]
            and df["close"].iat[i] < df["final_lb"].iat[i]
            else 0.00
        )
    # Mark the trend direction up/down
    df[stx] = np.where((df[st] > 0.00), np.where((df["close"] < df[st]), "down", "up"), None)

    # Remove basic and final bands from the columns
    df.drop(["basic_ub", "basic_lb", "final_ub", "final_lb"], inplace=True, axis=1)

    df.fillna(0, inplace=True)

    return df[st], df[stx]
