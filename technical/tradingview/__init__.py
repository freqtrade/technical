from technical.consensus import Consensus


class MovingAverageConsensus(Consensus):
    """
    This provides the consensus MovingAverage based indicators. It's configuration
    is identical with the configuration seen here

    https://www.tradingview.com/symbols/BTCUSD/technicals/
    """

    def __init__(self, dataframe):
        super().__init__(dataframe)

        self.evaluate_sma(period=10)
        self.evaluate_sma(period=20)
        self.evaluate_sma(period=30)
        self.evaluate_sma(period=50)
        self.evaluate_sma(period=100)
        self.evaluate_sma(period=200)

        self.evaluate_ema(period=10)
        self.evaluate_ema(period=20)
        self.evaluate_ema(period=30)
        self.evaluate_ema(period=50)
        self.evaluate_ema(period=100)
        self.evaluate_ema(period=200)
        self.evaluate_ichimoku()
        self.evaluate_hull()
        self.evaluate_vwma(period=20)


class OscillatorConsensus(Consensus):
    """
    consensus based indicator, based on several oscillators. Rule of thumb for entry should be
    that buy is larger than sell line.
    """

    def __init__(self, dataframe):
        super().__init__(dataframe)
        self.evaluate_rsi(period=14)
        self.evaluate_stoch()
        self.evaluate_cci(period=20)
        self.evaluate_adx()
        # awesome osc
        self.evaluate_macd()
        self.evaluate_momentum(period=10)
        # stoch rsi
        self.evaluate_williams()
        # bull bear
        self.evaluate_ultimate_oscilator()


class SummaryConsensus(Consensus):
    """
     an overall consensus of the trading view based configurations
     and it's basically a binary operation (on/off switch), meaning it needs
     to be combined with a couple of other indicators to avoid false buys.

    """

    def __init__(self, dataframe):
        super().__init__(dataframe)
        self.evaluate_consensus(OscillatorConsensus(dataframe), "osc", average=False)
        self.evaluate_consensus(MovingAverageConsensus(dataframe), "moving_average_consensus", average=False)
