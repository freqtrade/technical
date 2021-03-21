from technical.consensus.consensus import Consensus


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
