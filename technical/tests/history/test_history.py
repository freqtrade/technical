import datetime

from technical.history import load_data


def test_load_ticker():
    days = datetime.datetime.today() - datetime.timedelta(days=10)

    ticker = load_data("ETH/USDT", "1d", from_date=days.timestamp(), ccxt_api="poloniex", force=True)
    print(len(ticker))
    assert len(ticker) == 10
    days = datetime.datetime.today() - datetime.timedelta(days=100)

    ticker = load_data("BTC/USDT", "1d", from_date=days.timestamp(), ccxt_api="poloniex", force=True)
    print(len(ticker))
    assert len(ticker) == 100
    days = datetime.datetime.today() - datetime.timedelta(days=10)

    ticker = load_data("BTC/USDT", "4h", from_date=days.timestamp(), ccxt_api="poloniex", force=False)
    print(len(ticker))
    assert len(ticker) == 60
