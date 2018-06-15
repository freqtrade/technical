from technical.history import load_data


def test_load_ticker():
    ticker = load_data("ETH/USDT", "1d", 10, "poloniex", True)
    print(len(ticker))
    assert len(ticker) == 10
    ticker = load_data("BTC/USDT", "1d", 100, "poloniex", True)
    print(len(ticker))
    assert len(ticker) == 100
    ticker = load_data("BTC/USDT", "4h", 10, "poloniex", False)
    print(len(ticker))
    assert len(ticker) == 60
