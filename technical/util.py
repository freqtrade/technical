"""
defines utility functions to be used
"""

from pandas import DataFrame, DatetimeIndex, merge, to_datetime, to_timedelta

TICKER_INTERVAL_MINUTES = {
    "1m": 1,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "60m": 60,
    "2h": 120,
    "4h": 240,
    "6h": 360,
    "12h": 720,
    "1d": 1440,
    "1w": 10080,
}


def ticker_history_to_dataframe(ticker: list) -> DataFrame:
    """
    builds a dataframe based on the given ticker history

    :param ticker: See exchange.get_ticker_history
    :return: DataFrame
    """
    cols = ["date", "open", "high", "low", "close", "volume"]
    frame = DataFrame(ticker, columns=cols)

    frame["date"] = to_datetime(frame["date"], unit="ms", utc=True)

    # group by index and aggregate results to eliminate duplicate ticks
    frame = frame.groupby(by="date", as_index=False, sort=True).agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "max",
        }
    )
    frame.drop(frame.tail(1).index, inplace=True)  # eliminate partial candle
    return frame


def resample_to_interval(dataframe: DataFrame, interval):
    """
    Resamples the given dataframe to the desired interval.
    Please be aware you need to use resampled_merge to merge to another dataframe to
    avoid lookahead bias

    :param dataframe: dataframe containing close/high/low/open/volume
    :param interval: to which ticker value in minutes would you like to resample it
    :return:
    """
    if isinstance(interval, str):
        interval = TICKER_INTERVAL_MINUTES[interval]

    df = dataframe.copy()
    df = df.set_index(DatetimeIndex(df["date"]))
    ohlc_dict = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    # Resample to "left" border as dates are candle open dates
    df = df.resample(str(interval) + "min", label="left").agg(ohlc_dict).dropna()
    df.reset_index(inplace=True)

    return df


def resampled_merge(original: DataFrame, resampled: DataFrame, fill_na=True):
    """
    Merges a resampled dataset back into the original data set.
    Resampled candle will match OHLC only if full timespan is available in original dataframe.

    :param original: the original non resampled dataset
    :param resampled:  the resampled dataset
    :return: the merged dataset
    """

    original_int = compute_interval(original)
    resampled_int = compute_interval(resampled)

    if original_int < resampled_int:
        # Subtract "small" timeframe so merging is not delayed by 1 small candle.
        # Detailed explanation in https://github.com/freqtrade/freqtrade/issues/4073
        resampled["date_merge"] = (
            resampled["date"] + to_timedelta(resampled_int, "m") - to_timedelta(original_int, "m")
        )
    else:
        raise ValueError(
            "Tried to merge a faster timeframe to a slower timeframe." "Upsampling is not possible."
        )

    # rename all the columns to the correct interval
    resampled.columns = [f"resample_{resampled_int}_{col}" for col in resampled.columns]

    dataframe = merge(
        original,
        resampled,
        how="left",
        left_on="date",
        right_on=f"resample_{resampled_int}_date_merge",
    )
    dataframe = dataframe.drop(f"resample_{resampled_int}_date_merge", axis=1)

    if fill_na:
        dataframe = dataframe.ffill()

    return dataframe


def compute_interval(dataframe: DataFrame, exchange_interval=False):
    """
    Calculates the interval of the given dataframe for us
    :param dataframe:
    :param exchange_interval: should we convert the result to an exchange interval or just a number
    :return:
    """
    res_interval = int((dataframe["date"] - dataframe["date"].shift()).min().total_seconds() // 60)

    if exchange_interval:
        # convert to our allowed ticker values
        converted = list(TICKER_INTERVAL_MINUTES.keys())[
            list(TICKER_INTERVAL_MINUTES.values()).index(res_interval)
        ]
        if len(converted) > 0:
            return converted
        else:
            raise Exception(
                f"sorry, your interval of {res_interval} is not "
                f"supported in {TICKER_INTERVAL_MINUTES}"
            )

    return res_interval
