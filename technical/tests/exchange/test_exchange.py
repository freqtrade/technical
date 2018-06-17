from technical.exchange import load_ticker, historical_data
import datetime


def test_load_ticker():
    ticker = load_ticker("USDT", "ETH")

    assert ticker is not None
    ticker = load_ticker("USDT", "ALCAS")
    assert ticker is None


def test_historical_data():
    days = datetime.datetime.today() - datetime.timedelta(days=7)
    print(days)
    data = historical_data(
        "USDT", "BNB", "1d", days.timestamp())

    assert len(data) == 7


def test_historical_data_ploniex():
    """ this one is awesome since you can download years worth of data"""
    days = datetime.datetime.today() - datetime.timedelta(days=90)

    data = historical_data(
        "BTC", "ETH", "1d", days.timestamp(), "poloniex")

    assert len(data) == 90


def test_historical_data_ploniex_long():
    """ this one is awesome since you can download years worth of data"""
    days = datetime.datetime.today() - datetime.timedelta(days=365)

    data = historical_data(
        "BTC", "ETC", "1d", days.timestamp(), "poloniex")

    assert len(data) == 365
