import numpy
import pytest
from pandas import DataFrame


def test_qtpylib_cci_uses_talib(testdata_1m_btc):
    import talib

    from technical import qtpylib

    candles = testdata_1m_btc.iloc[:300]
    with pytest.warns(FutureWarning, match="qtpylib.cci is deprecated"):
        result = qtpylib.cci(candles, 14)
    expected = talib.CCI(candles["high"], candles["low"], candles["close"], 14)
    assert result.index.equals(candles.index)
    assert result.index.equals(expected.index)
    numpy.testing.assert_allclose(result, expected, equal_nan=True)

    flat = DataFrame({"high": [10.0] * 20, "low": [10.0] * 20, "close": [10.0] * 20})
    with pytest.warns(FutureWarning):
        assert (qtpylib.cci(flat, 14).iloc[13:] == 0).all()
