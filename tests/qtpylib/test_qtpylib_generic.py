import numpy as np
import pytest
from pandas import DataFrame, Series

from technical import qtpylib
from tests.helpers import indicator_case


@pytest.mark.parametrize(
    "function,source,args,kwargs",
    [
        # Dataframe based indicators
        indicator_case(qtpylib.heikinashi, "df"),
        indicator_case(qtpylib.awesome_oscillator, "df"),
        indicator_case(qtpylib.awesome_oscillator, "df", id_suffix="weighted", weighted=True),
        indicator_case(qtpylib.typical_price, "df"),
        indicator_case(qtpylib.mid_price, "df"),
        indicator_case(qtpylib.ibs, "df"),
        indicator_case(qtpylib.true_range, "df"),
        indicator_case(qtpylib.atr, "df"),
        indicator_case(qtpylib.atr, "df", id_suffix="exp", exp=True),
        indicator_case(qtpylib.rolling_vwap, "df"),
        indicator_case(qtpylib.keltner_channel, "df"),
        indicator_case(
            qtpylib.cci,
            "df",
            marks=pytest.mark.filterwarnings("ignore:qtpylib.cci is deprecated:FutureWarning"),
        ),
        indicator_case(qtpylib.stoch, "df"),
        indicator_case(qtpylib.stoch, "df", id_suffix="fast", fast=True),
        indicator_case(qtpylib.zscore, "df"),
        indicator_case(qtpylib.pvt, "df"),
        indicator_case(qtpylib.chopiness, "df"),
        # Series based indicators
        indicator_case(qtpylib.tdi, "close"),
        indicator_case(qtpylib.rolling_std, "close"),
        indicator_case(qtpylib.rolling_std, "close", 20, 5, id_suffix="min_periods"),
        indicator_case(qtpylib.rolling_mean, "close"),
        indicator_case(qtpylib.rolling_mean, "close", 20, 5, id_suffix="min_periods"),
        indicator_case(qtpylib.rolling_min, "close"),
        indicator_case(qtpylib.rolling_max, "close"),
        indicator_case(qtpylib.rolling_weighted_mean, "close"),
        indicator_case(
            qtpylib.hull_moving_average,
            "close",
            marks=pytest.mark.filterwarnings(
                "ignore:qtpylib.hull_moving_average.*is deprecated:FutureWarning"
            ),
        ),
        indicator_case(qtpylib.sma, "close"),
        indicator_case(
            qtpylib.wma,
            "close",
            marks=pytest.mark.filterwarnings("ignore:qtpylib.wma is deprecated:FutureWarning"),
        ),
        indicator_case(qtpylib.rsi, "close"),
        indicator_case(qtpylib.macd, "close"),
        indicator_case(qtpylib.bollinger_bands, "close"),
        indicator_case(qtpylib.weighted_bollinger_bands, "close"),
        indicator_case(qtpylib.returns, "close"),
        indicator_case(qtpylib.log_returns, "close"),
        indicator_case(qtpylib.implied_volatility, "close"),
        indicator_case(qtpylib.roc, "close"),
        indicator_case(qtpylib.zlma, "close"),
        indicator_case(qtpylib.zlma, "close", id_suffix="hma", kind="hma"),
        indicator_case(
            qtpylib.zlma,
            "close",
            id_suffix="sma",
            kind="sma",
        ),
        indicator_case(qtpylib.zlema, "close", 20),
        indicator_case(qtpylib.zlsma, "close", 20),
        indicator_case(qtpylib.zlhma, "close", 20),
        indicator_case(qtpylib.crossed, "close", 0.0026),
        indicator_case(qtpylib.crossed_above, "close", 0.0026),
        indicator_case(qtpylib.crossed_below, "close", 0.0026),
    ],
)
def test_qtpylib_indicators_generic_interface(
    function, source, args, kwargs, testdata_1m_btc, snapshot
):
    assert 13680 == len(testdata_1m_btc)
    # Mimic freqtrade dataframes, which use a 0-based RangeIndex.
    input_df = testdata_1m_btc.iloc[-1000:].reset_index(drop=True)
    indicator_input = input_df if source == "df" else input_df[source]
    res = function(indicator_input.copy(), *args, **kwargs)

    final_result = input_df.copy()
    name = function.__name__
    if isinstance(res, DataFrame):
        assert len(res) == 1000
        assert res.index.equals(input_df.index)
        for col in res.columns:
            final_result[f"{name}_{col}"] = res[col]
    elif isinstance(res, Series):
        assert len(res) == 1000
        assert res.index.equals(input_df.index)
        final_result[name] = res
    elif isinstance(res, np.ndarray):
        assert len(res) == 1000
        final_result[name] = res
    else:
        pytest.fail(f"Unexpected result type {type(res)} for {name}.")

    assert len(final_result) == 1000
    csv_string = final_result.to_csv(index=False, float_format="%.10f")
    assert snapshot == csv_string


def test_qtpylib_hma_is_linear_weighted():
    series = Series(np.arange(1.0, 31.0))
    with pytest.warns(FutureWarning, match="use talib.HMA instead"):
        assert qtpylib.hma(series, 14).iloc[-1] == pytest.approx(29.6666666667)
    with pytest.warns(FutureWarning, match="use talib.HMA instead"):
        assert qtpylib.hull_moving_average(series, 14).iloc[-1] == pytest.approx(29.6666666667)
    with pytest.warns(FutureWarning, match="use talib.HMA instead"):
        series.hma(14)


def test_qtpylib_zlhma_no_deprecation_warning(recwarn):
    series = Series(np.arange(1.0, 61.0))
    qtpylib.zlhma(series, 20)
    series.zlhma(20)
    assert not [w for w in recwarn if issubclass(w.category, FutureWarning)]


def test_qtpylib_ema_remains_exponential():
    series = Series(np.arange(1.0, 31.0))
    expected = series.ewm(span=14, min_periods=14).mean()
    assert np.allclose(series.ema(14), expected, equal_nan=True)
    assert np.allclose(qtpylib.zlema(series, 29), qtpylib.zlma(series, 29), equal_nan=True)
    lag = (29 - 1) // 2
    shifted = 2 * series - series.shift(lag)
    expected_zl = shifted.ewm(span=lag, min_periods=29).mean()
    assert np.allclose(qtpylib.zlema(series, 29), expected_zl, equal_nan=True)


def test_qtpylib_wma_is_linear_weighted():
    series = Series(np.arange(1.0, 31.0))
    # Linear weighted: sum(i * x_i) / sum(i) over the last 14 values
    weights = np.arange(1, 15)
    expected_wma = (series.iloc[-14:].to_numpy() * weights).sum() / weights.sum()
    with pytest.warns(FutureWarning, match="qtpylib.wma is deprecated"):
        res_wma = qtpylib.wma(series, 14)
    assert res_wma.iloc[-1] == pytest.approx(expected_wma)
    assert res_wma.iloc[-1] == pytest.approx(25.6666666667)
    with pytest.warns(FutureWarning, match="use talib.WMA instead"):
        series.wma(14)
