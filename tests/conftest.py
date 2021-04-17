# pragma pylint: disable=missing-docstring
import json
import logging

import pytest
from pandas import DataFrame

from technical.util import ticker_history_to_dataframe

logging.getLogger("").setLevel(logging.INFO)


@pytest.fixture(scope="class")
def testdata_1m_btc() -> DataFrame:
    with open("tests/testdata/UNITTEST_BTC-1m.json") as data_file:
        return ticker_history_to_dataframe(json.load(data_file))
