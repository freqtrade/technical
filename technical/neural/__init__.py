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


def nnf(dataframe: DataFrame, pair: str, forecast_period=7, exchange=None, historical_data_set_size=100) -> dict:
    """
        this neural network will classify if the price goes up (1) or down (-1)
    :param dataframe: dataframe with our ticker data
    :param pair: trading pair we are interested in
    :param forecast_period: how far in the future do we want to forecast. This is given in candles
    :param exchange: Exchange to us, if None, we create our own exchange object
    :param historical_data_set_size: how many historical data do we want to use, in days
    :return:
    """
    data = _populate_history(dataframe, exchange, pair, historical_data_set_size)
    from technical.neural.NNF import NNF

    NNF().run(data)

    pass


def _populate_history(dataframe, exchange, pair, days):
    """
    calculates our interval and returns required data for use
    :param dataframe:
    :param exchange:
    :param pair:
    :return:
    """
    from technical.util import compute_interval, ticker_history_to_dataframe
    from technical.history import load_data
    interval = compute_interval(dataframe, True)
    return ticker_history_to_dataframe(load_data(pair, interval, days, exchange))
