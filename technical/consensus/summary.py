from technical.consensus.consensus import Consensus
from technical.consensus.movingaverage import MovingAverageConsensus
from technical.consensus.oscillator import OscillatorConsensus


class SummaryConsensus(Consensus):
    """
    an overall consensus of the trading view based configurations
    and it's basically a binary operation (on/off switch), meaning it needs
    to be combined with a couple of other indicators to avoid false buys.

    """

    def __init__(self, dataframe):
        super().__init__(dataframe)
        self.evaluate_consensus(OscillatorConsensus(dataframe), "osc", average=False)
        self.evaluate_consensus(
            MovingAverageConsensus(dataframe), "moving_average_consensus", average=False
        )
