"""
Volume indicators
"""

from numpy.core.records import ndarray


########################################
#
# Volume Indicator Functions
#

# AD                   Chaikin A/D Line

def accumulation_distribution(dataframe) -> ndarray:
    from pyti.accumulation_distribution import accumulation_distribution as acd

    return acd(dataframe['close'], dataframe['high'], dataframe['low'], dataframe['volume'])


# ADOSC                Chaikin A/D Oscillator
# OBV                  On Balance Volume

# Other Volume Indicator Functions
def chaikin_money_flow(dataframe, period=21):
    mfm = (
        (dataframe['close'] - dataframe['low']) - (dataframe['high'] - dataframe['close'])
        / (dataframe['high'] - dataframe['low'])
    )
    mfv = mfm * dataframe['volume']
    cmf = mfv.rolling(period).sum() / dataframe['volume'].rolling(period).sum()
    return cmf


cmf = chaikin_money_flow
