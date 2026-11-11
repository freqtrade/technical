import numpy as np
import pytest
from pandas import DataFrame, Series

from technical import qtpylib


def _case(function, source, *args, id_suffix=None, marks=(), **kwargs):
    """
    Build a parametrized test case.
    source is either "df" (the full ohlcv dataframe) or a column name
    (e.g. "close") which is passed to the indicator as a Series.
    """
    case_id = f"{function.__name__}-{source}"
    if id_suffix:
        case_id += f"-{id_suffix}"
    return pytest.param(function, source, args, kwargs, id=case_id, marks=marks)


@pytest.mark.parametrize(
    "function,source,args,kwargs",
    [
        # Dataframe based indicators
        _case(qtpylib.heikinashi, "df"),
        _case(qtpylib.awesome_oscillator, "df"),
        _case(qtpylib.awesome_oscillator, "df", id_suffix="weighted", weighted=True),
        _case(qtpylib.typical_price, "df"),
        _case(qtpylib.mid_price, "df"),
        _case(qtpylib.ibs, "df"),
        _case(qtpylib.true_range, "df"),
        _case(qtpylib.atr, "df"),
        _case(qtpylib.atr, "df", id_suffix="exp", exp=True),
        _case(qtpylib.rolling_vwap, "df"),
        _case(qtpylib.keltner_channel, "df"),
        _case(
            qtpylib.cci,
            "df",
            marks=pytest.mark.filterwarnings("ignore:qtpylib.cci is deprecated:FutureWarning"),
        ),
        _case(qtpylib.stoch, "df"),
        _case(qtpylib.stoch, "df", id_suffix="fast", fast=True),
        _case(qtpylib.zscore, "df"),
        _case(qtpylib.pvt, "df"),
        _case(qtpylib.chopiness, "df"),
        # Series based indicators
        _case(qtpylib.tdi, "close"),
        _case(qtpylib.rolling_std, "close"),
        _case(qtpylib.rolling_std, "close", 20, 5, id_suffix="min_periods"),
        _case(qtpylib.rolling_mean, "close"),
        _case(qtpylib.rolling_mean, "close", 20, 5, id_suffix="min_periods"),
        _case(qtpylib.rolling_min, "close"),
        _case(qtpylib.rolling_max, "close"),
        _case(qtpylib.rolling_weighted_mean, "close"),
        _case(qtpylib.hull_moving_average, "close"),
        _case(qtpylib.sma, "close"),
        _case(qtpylib.wma, "close"),
        _case(qtpylib.hma, "close"),
        _case(qtpylib.rsi, "close"),
        _case(qtpylib.macd, "close"),
        _case(qtpylib.bollinger_bands, "close"),
        _case(qtpylib.weighted_bollinger_bands, "close"),
        _case(qtpylib.returns, "close"),
        _case(qtpylib.log_returns, "close"),
        _case(qtpylib.implied_volatility, "close"),
        _case(qtpylib.roc, "close"),
        _case(qtpylib.zlma, "close"),
        _case(qtpylib.zlma, "close", id_suffix="hma", kind="hma"),
        _case(
            qtpylib.zlma,
            "close",
            id_suffix="sma",
            kind="sma",
            marks=pytest.mark.xfail(
                raises=ValueError, strict=True, reason="min_periods > window for sma kind"
            ),
        ),
        _case(qtpylib.zlema, "close", 20),
        _case(
            qtpylib.zlsma,
            "close",
            20,
            marks=pytest.mark.xfail(
                raises=ValueError, strict=True, reason="min_periods > window for sma kind"
            ),
        ),
        _case(qtpylib.zlhma, "close", 20),
        _case(qtpylib.crossed, "close", 0.0026),
        _case(qtpylib.crossed_above, "close", 0.0026),
        _case(qtpylib.crossed_below, "close", 0.0026),
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
