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
        indicator_case(qtpylib.hull_moving_average, "close"),
        indicator_case(qtpylib.sma, "close"),
        indicator_case(qtpylib.wma, "close"),
        indicator_case(qtpylib.hma, "close"),
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
            marks=pytest.mark.xfail(
                raises=ValueError, strict=True, reason="min_periods > window for sma kind"
            ),
        ),
        indicator_case(qtpylib.zlema, "close", 20),
        indicator_case(
            qtpylib.zlsma,
            "close",
            20,
            marks=pytest.mark.xfail(
                raises=ValueError, strict=True, reason="min_periods > window for sma kind"
            ),
        ),
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
