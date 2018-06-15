from technical.history import load_data


def test_load_ticker():
    ticker = load_data("USDT", "ETH", "1d", 1000, "poloniex", True)
    print(len(ticker))
    assert len(ticker) == 1000
    ticker = load_data("USDT", "BTC", "1d", 100, "poloniex", True)
    print(len(ticker))
    assert len(ticker) == 100
    ticker = load_data("USDT", "BTC", "4h", 100, "poloniex", False)
    print(len(ticker))
    assert len(ticker) == 600
