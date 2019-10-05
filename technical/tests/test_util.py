import json

from technical.indicators import cmf
from technical.util import (resample_to_interval, resampled_merge,
                            ticker_history_to_dataframe)


def test_ticker_to_dataframe():
    with open('technical/tests/testdata/UNITTEST_BTC-1m.json') as data_file:
        data = ticker_history_to_dataframe(json.load(data_file))
        assert len(data) > 0


def test_resample_to_interval(testdata_1m_btc):
    result = resample_to_interval(testdata_1m_btc, 5)

    # should be roughly a factor 5
    assert (len(testdata_1m_btc) / len(result) > 4.5)
    assert (len(testdata_1m_btc) / len(result) < 5.5)


def test_resampled_merge(testdata_1m_btc):
    resampled = resample_to_interval(testdata_1m_btc, 5)

    merged = resampled_merge(testdata_1m_btc, resampled)

    assert (len(merged) == len(testdata_1m_btc))
    assert "resample_5_open" in merged
    assert "resample_5_close" in merged
    assert "resample_5_low" in merged
    assert "resample_5_high" in merged

    assert "resample_5_date" not in merged
    assert "resample_5_volume" not in merged


def test_resampled_merge_contains_indicator(testdata_1m_btc):
    resampled = resample_to_interval(testdata_1m_btc, 5)
    resampled['cmf'] = cmf(resampled, 5)
    merged = resampled_merge(testdata_1m_btc, resampled)

    print(merged)
    assert "resample_5_cmf" in merged
