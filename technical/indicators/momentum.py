"""
Momentum indicators
"""

from numpy.core.records import ndarray
from pandas import DataFrame


########################################
#
# Momentum Indicator Functions
#

# ADX                  Average Directional Movement Index
# ADXR                 Average Directional Movement Index Rating
# APO                  Absolute Price Oscillator

# AROON                Aroon
def aroon(dataframe, period=25, field='close', colum_prefix="aroon") -> DataFrame:
    from pyti.aroon import aroon_up as up
    from pyti.aroon import aroon_down as down
    dataframe["{}_up".format(colum_prefix)] = up(dataframe[field], period)
    dataframe["{}_down".format(colum_prefix)] = down(dataframe[field], period)
    return dataframe


# AROONOSC             Aroon Oscillator
# BOP                  Balance Of Power

# CCI                  Commodity Channel Index
def cci(dataframe, period) -> ndarray:
    from pyti.commodity_channel_index import commodity_channel_index

    return commodity_channel_index(dataframe['close'], dataframe['high'], dataframe['low'], period)


# CMO                  Chande Momentum Oscillator
def cmo(dataframe, period, field='close') -> ndarray:
    from pyti.chande_momentum_oscillator import chande_momentum_oscillator
    return chande_momentum_oscillator(dataframe[field], period)


# DX                   Directional Movement Index
# MACD                 Moving Average Convergence/Divergence
# MACDEXT              MACD with controllable MA type
# MACDFIX              Moving Average Convergence/Divergence Fix 12/26
# MFI                  Money Flow Index
# MINUS_DI             Minus Directional Indicator
# MINUS_DM             Minus Directional Movement

# MOM                  Momentum
def momentum(dataframe, field='close', period=9):
    from pyti.momentum import momentum as m
    return m(dataframe[field], period)


# PLUS_DI              Plus Directional Indicator
# PLUS_DM              Plus Directional Movement
# PPO                  Percentage Price Oscillator
# ROC                  Rate of change : ((price/prevPrice)-1)*100
# ROCP                 Rate of change Percentage: (price-prevPrice)/prevPrice
# ROCR                 Rate of change ratio: (price/prevPrice)
# ROCR100              Rate of change ratio 100 scale: (price/prevPrice)*100
# RSI                  Relative Strength Index
# STOCH                Stochastic
# STOCHF               Stochastic Fast
# STOCHRSI             Stochastic Relative Strength Index
# TRIX                 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA

# ULTOSC               Ultimate Oscillator
def ultimate_oscilator(dataframe):
    from pyti.ultimate_oscillator import ultimate_oscillator as uo
    uo(dataframe['close'], dataframe['low'])


# WILLR                Williams' %R
def williams_percent(dataframe, period=14, field='close'):
    highest_high = dataframe[field].rolling(period).max()
    lowest_low = dataframe[field].rolling(period).min()
    wr = (highest_high - dataframe[field]) / (highest_high - lowest_low) * -100
    return wr
