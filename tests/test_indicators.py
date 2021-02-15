import numpy
import pytest


def test_atr(testdata_1m_btc):
    from technical.indicators import atr

    result = testdata_1m_btc
    result['atr'] = atr(testdata_1m_btc, 14)

    result = result.tail(10)

    assert result['atr'].all() > 0


def test_atr_percent(testdata_1m_btc):
    from technical.indicators import atr_percent

    result = testdata_1m_btc
    result['atr'] = atr_percent(testdata_1m_btc, 14)

    result = result.tail(10)

    assert result['atr'].all() > 0


def test_bollinger_bands(testdata_1m_btc):
    from technical.indicators import bollinger_bands

    result = bollinger_bands(testdata_1m_btc)

    result = result.tail(10)

    assert result['bb_lower'].all() > 0
    assert result['bb_middle'].all() > 0
    assert result['bb_upper'].all() > 0


def test_chaikin_money_flow(testdata_1m_btc):
    from technical.indicators import cmf, chaikin_money_flow

    assert cmf is chaikin_money_flow

    result = chaikin_money_flow(testdata_1m_btc, 14)

    # drop nan, they are exspected, based on the period
    result = result[~numpy.isnan(result)]

    assert result.min() >= -1
    assert result.max() <= 1


def test_fibonacci_retracements(testdata_1m_btc):
    from technical.indicators import fibonacci_retracements

    result = fibonacci_retracements(testdata_1m_btc)

    assert result.min() < 1.0e-8
    assert result.max() > 1.0 - 1.0e-8


def test_return_on_investment():
    from pandas import DataFrame
    from technical.indicators import return_on_investment

    close = numpy.array([100, 200, 300, 400, 500, 600])
    buys = numpy.array([[0, 0, 0, 0, 0, 0],
                        [0, 1, 0, 1, 0, 1],
                        [1, 0, 1, 0, 1, 0]])
    rois = numpy.array([[0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
                        [0.0, 0.0, 50.0, 0.0, 25.0, 0.0],
                        [0.0, 100.0, 0.0, 33.33, 0.0, 20.0]])

    for buy, roi in zip(buys, rois):
        dataframe = DataFrame()
        dataframe['close'] = close
        dataframe['buy'] = buy

        dataframe = return_on_investment(dataframe, decimals=2)
        assert (dataframe['roi'] >= 0).all()
        assert ((dataframe.loc[dataframe['buy'] == 1, 'roi'] == 0).all())
        assert numpy.allclose(numpy.array(dataframe['roi']), roi)
