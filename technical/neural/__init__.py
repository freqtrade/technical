"""

this module will provide neural network based technical indicators to remove the complexity of them from the user
"""
from pandas import DataFrame


def nnc(dataframe: DataFrame, pair: str, exchange=None) -> int:
    """
        this neural network will classify if the price goes up (1) or down (-1)
    :param dataframe: dataframe with our ticker data
    :param pair: trading pair we are interested in
    :param exchange: Exchange to us, if None, we create our own exchange object
    :return:
    """
    data = _populate_history(dataframe, exchange, pair)

    # TODO
    pass


def nnf(dataframe: DataFrame, pair: str, forecast_period=7, exchange=None) -> dict:
    """
        this neural network will classify if the price goes up (1) or down (-1)
    :param dataframe: dataframe with our ticker data
    :param pair: trading pair we are interested in
    :param forecast_period: how far in the future do we want to forecast. This is given in candles
    :param exchange: Exchange to us, if None, we create our own exchange object
    :return:
    """
    data = _populate_history(dataframe, exchange, pair)
    # TODO
    pass


def _populate_history(dataframe, exchange, pair):
    """
    calculates our interval and returns required data for use
    :param dataframe:
    :param exchange:
    :param pair:
    :return:
    """
    from technical.util import compute_interval
    from technical.history import load_data
    interval = compute_interval(dataframe, True)
    return load_data(pair, interval, 5000, exchange)
