import pytest
from pandas import DataFrame, Series

import technical.indicators as ti


@pytest.mark.parametrize(
    "function,args,responsetype,new_column_names",
    [
        (ti.atr_percent, [], "series", None),
        (ti.atr, [], "series", None),
        (ti.bollinger_bands, [], "df", ["bb_lower", "bb_middle", "bb_upper"]),
        (ti.chaikin_money_flow, [], "series", None),
        (ti.MADR, [], "df", ["rate", "plusdev", "minusdev", "stdcenter"]),
        (ti.PMAX, [], "df", ["ATR_10", "pm_10_3_12_1", "pmX_10_3_12_1"]),
        (ti.RMI, [], "series", None),
        (ti.SSLChannels, [], "tuple", None),
        (ti.TKE, [], "tuple", None),
        (ti.VIDYA, [], "series", None),
        (ti.atr_percent, [], "series", None),
        (ti.chaikin_money_flow, [], "series", None),
        (ti.chopiness, [], "series", None),
        (ti.cmf, [], "series", None),
        (ti.ema, [10], "series", None),
        (ti.fibonacci_retracements, [], "series", None),
        (ti.hull_moving_average, [10], "series", None),
        (ti.ichimoku, [], "dict", None),
        (ti.laguerre, [], "list", None),
        (ti.madrid_sqz, [], "tuple", None),
        (ti.mmar, [], "tuple", None),
        (ti.osc, [], "series", None),
        # (ti.return_on_investment, [], 'series', None),
        (ti.sma, [10], "series", None),
        (ti.stc, [], "series", None),
        (ti.td_sequential, [], "df", ["TD_count"]),
        (ti.dema, [10], "series", None),
        (ti.tema, [10], "series", None),
        # (ti.tv_hma, [], 'series', None),
        (ti.tv_wma, [], "df", ["tv_wma"]),
        (ti.vfi, [], "tuple", None),
        (ti.vpci, [], "series", None),
        (ti.vpcii, [], "series", None),
        (ti.vwma, [10], "series", None),
        (ti.vwmacd, [], "df", ["vwmacd", "signal", "hist"]),
        (ti.williams_percent, [], "series", None),
    ],
)
def test_indicators_generic_interface(
    function, args, responsetype, new_column_names, testdata_1m_btc
):
    assert 13680 == len(testdata_1m_btc)
    # Ensure all builtin indicators have the same interface
    res = function(testdata_1m_btc.iloc[-1000:].copy(), *args)

    if responsetype == "tuple":
        assert isinstance(res, tuple)
        assert len(res[0]) == 1000
        assert len(res[1]) == 1000
    elif responsetype == "list":
        # only laguerre is this
        # TODO: This should be changed!
        assert isinstance(res, list)
        assert len(res) == 1000
    elif responsetype == "dict":
        assert isinstance(res, dict)
        assert len(res["tenkan_sen"]) == 1000
    elif responsetype == "series":
        assert isinstance(res, Series)
        assert len(res) == 1000
    elif responsetype == "df":
        # Result is dataframe
        assert isinstance(res, DataFrame)
        assert len(res) == 1000
        if len(new_column_names) > 0:
            assert len(res.columns) == len(new_column_names) + 6
            default_columns = ["date", "open", "high", "low", "close", "volume"]
            cols = set(res.columns)
            assert cols == set(new_column_names + default_columns)
            # assert set()
            assert all([x in res.columns for x in new_column_names])
    else:
        assert False
