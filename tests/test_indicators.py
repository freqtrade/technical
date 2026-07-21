import numpy


def test_atr(testdata_1m_btc):
    from technical.indicators import atr

    result = testdata_1m_btc
    result["atr"] = atr(testdata_1m_btc, 14)

    result = result.tail(10)

    assert result["atr"].all() > 0


def test_atr_percent(testdata_1m_btc):
    from technical.indicators import atr_percent

    result = testdata_1m_btc
    result["atr"] = atr_percent(testdata_1m_btc, 14)

    result = result.tail(10)

    assert result["atr"].all() > 0


def test_bollinger_bands(testdata_1m_btc):
    from technical.indicators import bollinger_bands

    result = bollinger_bands(testdata_1m_btc)

    result = result.tail(10)

    assert result["bb_lower"].all() > 0
    assert result["bb_middle"].all() > 0
    assert result["bb_upper"].all() > 0


def test_chaikin_money_flow(testdata_1m_btc):
    from technical.indicators import chaikin_money_flow, cmf

    assert cmf is chaikin_money_flow

    result = chaikin_money_flow(testdata_1m_btc, 14)

    # drop nan, they are expected, based on the period
    result = result[~numpy.isnan(result)]

    assert result.min() >= -1
    assert result.max() <= 1


def test_fibonacci_retracements(testdata_1m_btc):
    from technical.indicators import fibonacci_retracements

    # window=0 uses the whole dataframe (lookahead bias)
    result = fibonacci_retracements(testdata_1m_btc, window=0)

    assert result.notna().all()
    assert result.min() < 1.0e-8
    assert result.max() > 1.0 - 1.0e-8

    # Rolling window - no lookahead bias
    window = 60
    result = fibonacci_retracements(testdata_1m_btc, window=window)

    # The first `window - 1` candles cannot be calculated
    assert result.iloc[: window - 1].isna().all()
    assert result.iloc[window - 1 :].notna().all()

    assert result.min() < 1.0e-8
    assert result.max() > 1.0 - 1.0e-8

    # Result must not change when future candles are added
    partial = fibonacci_retracements(testdata_1m_btc.iloc[:500], window=window)
    assert numpy.allclose(partial.iloc[window - 1 :], result.iloc[window - 1 : 500])

    # The default is a rolling window
    default = fibonacci_retracements(testdata_1m_btc)
    assert default.equals(fibonacci_retracements(testdata_1m_btc, window=120))


def test_return_on_investment():
    from pandas import DataFrame

    from technical.indicators import return_on_investment

    close = numpy.array([100, 200, 300, 400, 500, 600])
    buys = numpy.array([[0, 0, 0, 0, 0, 0], [0, 1, 0, 1, 0, 1], [1, 0, 1, 0, 1, 0]])
    rois = numpy.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 50.0, 0.0, 25.0, 0.0],
            [0.0, 100.0, 0.0, 33.33, 0.0, 20.0],
        ]
    )

    for buy, roi in zip(buys, rois):
        dataframe = DataFrame()
        dataframe["close"] = close
        dataframe["buy"] = buy

        dataframe = return_on_investment(dataframe, decimals=2)
        assert (dataframe["roi"] >= 0).all()
        assert (dataframe.loc[dataframe["buy"] == 1, "roi"] == 0).all()
        assert numpy.allclose(numpy.array(dataframe["roi"]), roi)


def test_rma():
    from pandas import DataFrame

    from technical.indicators import rma

    close = numpy.array([6, -1, 5, 4, 12, 5, 11, 10, 3, 13], dtype=float)
    dataframe = DataFrame({"high": close})

    # Seeded with the SMA of the first 5 values, then (prev * 4 + current) / 5.
    expected = [numpy.nan] * 4 + [5.2, 5.16, 6.328, 7.0624, 6.249920, 7.599936]

    result = rma(dataframe, 5, field="high")

    assert numpy.allclose(result, expected, equal_nan=True)
    # Warmup is period - 1 candles, matching talib's lookback for a period-length seed
    assert result.isna().sum() == 4


def test_rma_short_dataframe():
    from pandas import DataFrame

    from technical.indicators import rma

    dataframe = DataFrame({"close": numpy.array([1.0, 2.0, 3.0])})

    assert rma(dataframe, 5).isna().all()
