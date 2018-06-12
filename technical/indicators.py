"""
This file contains a collection of common indicators, which are based on third party or custom libraries

"""
from pyti.chaikin_money_flow import chaikin_money_flow
from pyti.accumulation_distribution import accumulation_distribution as acd


def cmf(dataframe, period):
    return chaikin_money_flow(dataframe['close'], dataframe['high'], dataframe['low'], dataframe['volume'], period)


def accumulation_distribution(dataframe):
    return acd(dataframe['close'], dataframe['high'], dataframe['low'], dataframe['volume'])
