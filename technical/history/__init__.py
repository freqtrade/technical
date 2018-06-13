"""
this provides easy access to historical data, which will be stored in a local database or downloaded on demand and
cached
"""
from pandas import DataFrame


def historical_data(stake, currency, interval, begin_date, end_date) -> DataFrame:
    """

    :param stake: the stake currency, like USDT, BTC, ETH
    :param currency: the currency of choice, for example ETH

    these two will form your trade pair!

    :param interval: your desired interval in minutes,

    :param begin_date: earliest date of observed data
    :param end_date: latest date of observed data (normaly right now0
    :return: the dataframe, containing the aggregated data
    """