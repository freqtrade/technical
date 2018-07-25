from technical.consensus import Consensus


class MovingAverageConsensus(Consensus):
    """
    This provides the consensus MovingAverage based indicators. It's configuration
    is identical with the configuration seen here

    https://www.tradingview.com/symbols/BTCUSD/technicals/
    """

    def __init__(self, dataframe, public=False):
        super(MovingAverageConsensus, self).__init__(dataframe, public)

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
    consensus based indicator, based on several
    """

    def __init__(self,dataframe,public=False):
        super(OscillatorConsensus,self).__init__(dataframe,public)
        self.evaluate_rsi(period=14)
        self.evaluate_stoch()
        self.evaluate_cci(period=20)
        self.evaluate_adx()
        # awesome osc
        self.evaluate_macd()
        self.evaluate_momentum(period=10)
        #stoch rsi
        self.evaluate_williams()
        #bull bear
        #ultimate osc