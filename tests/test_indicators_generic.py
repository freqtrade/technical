import pytest
from pandas import DataFrame, Series

import technical.indicators as ti


@pytest.mark.parametrize(
    "function,args,responsetype,new_column_names",
    [
        (ti.atr_percent, [], 'series', ['']),
        (ti.atr, [], 'series', ['',]),
        (ti.bollinger_bands, [], 'df', ['',]),
        (ti.chaikin_money_flow, [], 'series', ['',]),
        (ti.MADR, [], 'df', ['',]),
        (ti.PMAX, [], 'df', ['ATR_10', 'pm_10_3_12_1', 'pmX_10_3_12_1']),
        (ti.RMI, [], 'series', ['',]),
        (ti.SSLChannels, [], 'tuple', ['',]),
        (ti.TKE, [], 'tuple', ['',]),
        (ti.VIDYA, [], 'series', ['',]),
        (ti.atr_percent, [], 'series', ['',]),
        (ti.chaikin_money_flow, [], 'series', ['',]),
        (ti.chopiness, [], 'series', ['',]),
        (ti.cmf, [], 'series', ['',]),
        (ti.ema, [10], 'series', ['',]),
        (ti.fibonacci_retracements, [], 'series', ['',]),
        (ti.hull_moving_average, [10], 'series', ['',]),
        (ti.ichimoku, [], 'dict', ['',]),
        (ti.laguerre, [], 'list', ['',]),
        (ti.madrid_sqz, [], 'tuple', ['',]),
        (ti.mmar, [], 'tuple', ['',]),
        (ti.osc, [], 'series', ['',]),
        # (ti.return_on_investment, [], 'series', ['',]),
        (ti.sma, [10], 'series', ['',]),
        (ti.stc, [], 'series', ['',]),
        (ti.td_sequential, [], 'df', ['',]),
        (ti.dema, [10], 'series', ['',]),
        (ti.tema, [10], 'series', ['',]),
        # (ti.tv_hma, [], 'series', ['',]),
        (ti.tv_wma, [], 'df', ['',]),
        (ti.vfi, [], 'tuple', ['',]),
        (ti.vpci, [], 'series', ['',]),
        (ti.vpcii, [], 'series', ['',]),
        (ti.vwma, [10], 'series', ['',]),
        (ti.vwmacd, [], 'df', ['',]),
        (ti.williams_percent, [], 'series', ['',]),
    ],
)
def test_indicators_generic_interface(
    function,
    args,
    responsetype,
    new_column_names,
    testdata_1m_btc
):
    assert 13680 == len(testdata_1m_btc)
    # Ensure all builtin indicators have the same interface
    res = function(testdata_1m_btc.iloc[-1000:].copy(), *args)

    if responsetype == 'tuple':
        assert isinstance(res, tuple)
        assert len(res[0]) == 1000
        assert len(res[1]) == 1000
    elif responsetype == 'list':
        # only laguerre is this
        # TODO: This should be changed!
        assert isinstance(res, list)
        assert len(res) == 1000
    elif responsetype == 'dict' :
        assert isinstance(res, dict)
        assert len(res["tenkan_sen"]) == 1000
    elif responsetype == 'series':
        assert isinstance(res, Series)
        assert len(res) == 1000
    elif responsetype == 'df':
        # Result is dataframe
        assert isinstance(res, DataFrame)
        assert len(res) == 1000
        # if (len(new_column_names) > 0):
        #     assert len(res.columns) == len(new_column_names) + 6
        #     assert all([x in res.columns for x in new_column_names])
    else:
        assert False
