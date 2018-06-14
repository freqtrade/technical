from technical.exchange import load_ticker, historical_data
import datetime


def test_load_ticker():
    ticker = load_ticker("USDT", "ETH")

    assert ticker is not None
    ticker = load_ticker("USDT", "ALCAS")
    assert ticker is None


def test_historical_data():
    data = historical_data(
        "USDT", "ETH", "1d", 7)

    assert len(data) == 7


def test_historical_data_ploniex():
    """ this one is awesome since you can download years worth of data"""
    data = historical_data(
        "USDT", "ETH", "1d", 90, "poloniex")

    assert len(data) == 90


def test_historical_data_ploniex_long():
    """ this one is awesome since you can download years worth of data"""
    data = historical_data(
        "USDT", "ETH", "1d", 365, "poloniex")

    assert len(data) == 365
