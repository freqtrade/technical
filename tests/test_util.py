import json

import pandas as pd

from technical.indicators import chaikin_money_flow
from technical.util import resample_to_interval, resampled_merge, ticker_history_to_dataframe


def test_ticker_to_dataframe():
    with open("tests/testdata/UNITTEST_BTC-1m.json") as data_file:
        data = ticker_history_to_dataframe(json.load(data_file))
        assert len(data) > 0


def test_resample_to_interval(testdata_1m_btc):
    result = resample_to_interval(testdata_1m_btc, 5)

    # should be roughly a factor 5
    assert len(testdata_1m_btc) / len(result) > 4.5
    assert len(testdata_1m_btc) / len(result) < 5.5


def test_resampled_merge(testdata_1m_btc):
    resampled = resample_to_interval(testdata_1m_btc, 5)

    merged = resampled_merge(testdata_1m_btc, resampled)

    assert len(merged) == len(testdata_1m_btc)
    assert "resample_5_open" in merged
    assert "resample_5_close" in merged
    assert "resample_5_low" in merged
    assert "resample_5_high" in merged

    assert "resample_5_date" in merged
    assert "resample_5_volume" in merged
    # Verify the assignment goes to the correct candle
    # If resampling to 5m, then the resampled value needs to be on the 5m candle.
    date = pd.to_datetime("2017-11-14 22:45:00", utc=True)
    assert merged.loc[merged["date"] == "2017-11-14 22:48:00", "resample_5_date"].iloc[0] != date
    # The 5m candle for 22:45 is available at 22:50,
    # when both :49 1m and :45 5m candles close
    assert merged.loc[merged["date"] == "2017-11-14 22:49:00", "resample_5_date"].iloc[0] == date
    assert merged.loc[merged["date"] == "2017-11-14 22:50:00", "resample_5_date"].iloc[0] == date
    assert merged.loc[merged["date"] == "2017-11-14 22:51:00", "resample_5_date"].iloc[0] == date
    assert merged.loc[merged["date"] == "2017-11-14 22:52:00", "resample_5_date"].iloc[0] == date
    assert merged.loc[merged["date"] == "2017-11-14 22:53:00", "resample_5_date"].iloc[0] == date
    # The 5m candle for 22:50 is available at 22:54,
    # when both :54 1m and :50 5m candles close
    date = pd.to_datetime("2017-11-14 22:50:00", utc=True)
    assert merged.loc[merged["date"] == "2017-11-14 22:54:00", "resample_5_date"].iloc[0] == date
    assert merged.loc[merged["date"] == "2017-11-14 22:55:00", "resample_5_date"].iloc[0] == date
    assert merged.loc[merged["date"] == "2017-11-14 22:56:00", "resample_5_date"].iloc[0] == date
    assert merged.loc[merged["date"] == "2017-11-14 22:57:00", "resample_5_date"].iloc[0] == date
    assert merged.loc[merged["date"] == "2017-11-14 22:58:00", "resample_5_date"].iloc[0] == date


def test_resampled_merge_contains_indicator(testdata_1m_btc):
    resampled = resample_to_interval(testdata_1m_btc, 5)
    resampled["cmf"] = chaikin_money_flow(resampled, 5)
    merged = resampled_merge(testdata_1m_btc, resampled)

    print(merged)
    assert "resample_5_cmf" in merged
