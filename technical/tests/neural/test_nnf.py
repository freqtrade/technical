from technical.neural import nnf
from technical.exchange import historical_data
from technical.util import ticker_history_to_dataframe, resample_to_interval


def test_nnf():
    print("populate intial data set")
    ticker = historical_data("USDT", "BTC", "5m")

    dataframe = ticker_history_to_dataframe(ticker)
    #
    print("execute neural network")
    result = nnf(dataframe, "BTC/USDT", historical_data_set_size=1)
