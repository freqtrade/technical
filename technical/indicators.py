"""
This file contains a collection of common indicators, which are based on third party or custom libraries

"""


def cmf(dataframe, period):
    from pyti.chaikin_money_flow import chaikin_money_flow

    return chaikin_money_flow(dataframe['close'], dataframe['high'], dataframe['low'], dataframe['volume'], period)


def accumulation_distribution(dataframe):
    from pyti.accumulation_distribution import accumulation_distribution as acd

    return acd(dataframe['close'], dataframe['high'], dataframe['low'], dataframe['volume'])
