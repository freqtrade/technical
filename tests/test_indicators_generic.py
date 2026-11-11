import pytest
from pandas import DataFrame, Series

import technical.indicators as ftt
from tests.helpers import indicator_case


@pytest.mark.parametrize(
    "function,responsetype,args,kwargs",
    [
        indicator_case(ftt.atr_percent, "series"),
        indicator_case(ftt.atr, "series"),
        indicator_case(ftt.bollinger_bands, "df"),
        indicator_case(ftt.chaikin_money_flow, "series"),
        indicator_case(ftt.MADR, "df"),
        indicator_case(ftt.PMAX, "df"),
        indicator_case(ftt.RMI, "series"),
        indicator_case(ftt.SSLChannels, "tuple"),
        indicator_case(ftt.TKE, "tuple"),
        indicator_case(ftt.VIDYA, "series"),
        indicator_case(ftt.chopiness, "series"),
        indicator_case(ftt.cmf, "series", id_suffix="cmf"),  # alias of chaikin_money_flow
        indicator_case(ftt.ema, "series", 10),
        indicator_case(ftt.fibonacci_retracements, "series"),
        indicator_case(ftt.fibonacci_retracements, "series", "close", 15, id_suffix="close-15"),
        indicator_case(ftt.hull_moving_average, "series", 10),
        indicator_case(ftt.ichimoku, "dict"),
        indicator_case(ftt.laguerre, "series"),
        indicator_case(ftt.madrid_sqz, "tuple"),
        indicator_case(ftt.mmar, "tuple"),
        indicator_case(ftt.osc, "series"),
        # indicator_case(ftt.return_on_investment, "series"),
        indicator_case(ftt.sma, "series", 10),
        # indicator_case(ftt.stc, "series"),  # disabled for slightly different results on ARM
        indicator_case(ftt.td_sequential, "df"),
        indicator_case(ftt.dema, "series", 10),
        indicator_case(ftt.tema, "series", 10),
        indicator_case(ftt.tv_hma, "series", 10),
        indicator_case(ftt.tv_wma, "series", 10),
        indicator_case(ftt.tv_alma, "series"),
        indicator_case(ftt.vfi, "tuple"),
        indicator_case(ftt.vpci, "series"),
        indicator_case(ftt.vpcii, "series"),
        indicator_case(ftt.vwma, "series", 10),
        indicator_case(ftt.vwmacd, "df"),
        indicator_case(ftt.williams_percent, "series"),
        indicator_case(ftt.supertrend, "tuple"),
        indicator_case(ftt.rma, "series", 14),
    ],
)
def test_indicators_generic_interface(
    function, responsetype, args, kwargs, testdata_1m_btc, snapshot
):
    assert 13680 == len(testdata_1m_btc)
    # Ensure all builtin indicators have the same interface
    input_df = testdata_1m_btc.iloc[-1000:].copy()
    res = function(input_df, *args, **kwargs)

    final_result = None
    if responsetype == "tuple":
        assert isinstance(res, tuple)
        assert len(res[0]) == 1000
        assert len(res[1]) == 1000
        final_result = input_df
        for i, x in enumerate(res):
            final_result.loc[:, f"{function.__name__}_{i}"] = x

    elif responsetype == "dict":
        assert isinstance(res, dict)
        assert len(res["tenkan_sen"]) == 1000
        final_result = input_df

        for k, v in res.items():
            final_result.loc[:, f"{function.__name__}_{k}"] = v
    elif responsetype == "series":
        assert isinstance(res, Series)
        assert len(res) == 1000
        final_result = input_df
        final_result.loc[:, function.__name__] = res
    elif responsetype == "df":
        # Result is dataframe
        assert isinstance(res, DataFrame)
        assert len(res) == 1000
        final_result = res
        # Indicator columns are added to the input - the snapshot pins the exact column names.
        default_columns = ["date", "open", "high", "low", "close", "volume"]
        assert all(x in res.columns for x in default_columns)
    else:
        assert False

    # Ensure full output is serialized
    # can probably be removed once https://github.com/syrupy-project/syrupy/issues/887
    # is implemented
    assert isinstance(final_result, DataFrame)
    assert len(final_result) == 1000
    csv_string = final_result.to_csv(index=False, float_format="%.10f")
    assert snapshot == csv_string
