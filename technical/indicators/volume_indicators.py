"""
Volume indicators
"""

########################################
#
# Volume Indicator Functions
#

# AD                   Chaikin A/D Line

# ADOSC                Chaikin A/D Oscillator
# OBV                  On Balance Volume


# Other Volume Indicator Functions
def chaikin_money_flow(dataframe, period=21):
    mfm = (dataframe["close"] - dataframe["low"]) - (dataframe["high"] - dataframe["close"]) / (
        dataframe["high"] - dataframe["low"]
    )
    mfv = mfm * dataframe["volume"]
    cmf = mfv.rolling(period).sum() / dataframe["volume"].rolling(period).sum()
    return cmf


cmf = chaikin_money_flow
