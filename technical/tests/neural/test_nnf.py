from technical.neural import nnf
from technical.exchange import load_ticker
from technical.util import ticker_to_dataframe, resample_to_interval


def test_nnf():
    ticker = load_ticker("USDT", "BTC")

    dataframe = ticker_to_dataframe(ticker)
    dataframe = resample_to_interval(dataframe, 15)

    result = nnf(dataframe, "BTC/USDT")
