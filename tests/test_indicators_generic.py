import pytest

import technical.indicators as ti


@pytest.mark.parametrize(
    "function, args",
    [
        (ti.atr_percent, []),
        (ti.atr, []),
        (ti.bollinger_bands, []),
        (ti.chaikin_money_flow, []),
        (ti.MADR, []),
        (ti.PMAX, []),
        (ti.RMI, []),
        (ti.SSLChannels, []),
        (ti.TKE, []),
        (ti.VIDYA, []),
        (ti.atr_percent, []),
        (ti.bollinger_bands, []),
        (ti.chaikin_money_flow, []),
        (ti.chopiness, []),
        (ti.cmf, []),
        (ti.ema, [10]),
        (ti.fibonacci_retracements, []),
        (ti.hull_moving_average, [10]),
        (ti.ichimoku, []),
        (ti.laguerre, []),
        (ti.madrid_sqz, []),
        (ti.mmar, []),
        (ti.osc, []),
        # (ti.return_on_investment, []),
        (ti.sma, [10]),
        (ti.stc, []),
        (ti.td_sequential, []),
        (ti.dema, [10]),
        (ti.tema, [10]),
        # (ti.tv_hma, []),
        (ti.tv_wma, []),
        (ti.vfi, []),
        (ti.vpci, []),
        (ti.vpcii, []),
        (ti.vwma, [10]),
        (ti.vwmacd, []),
        (ti.williams_percent, []),
    ],
)
def test_indicators_generic_interface(function, args, testdata_1m_btc):
    assert 13680 == len(testdata_1m_btc)
    # Ensure all builtin indicators have the same interface
    res = function(testdata_1m_btc.iloc[-1000:].copy(), *args)
    if isinstance(res, tuple):
        assert len(res[0]) == 1000
        assert len(res[1]) == 1000
    elif isinstance(res, dict):
        assert len(res["tenkan_sen"]) == 1000
    else:
        assert len(res) == 1000
