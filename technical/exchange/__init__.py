import logging
from typing import List, Dict, Optional

import arrow
import ccxt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

TICKER_INTERVAL_MINUTES = {
    '1m': 1,
    '5m': 5,
    '15m': 15,
    '30m': 30,
    '1h': 60,
    '60m': 60,
    '2h': 120,
    '4h': 240,
    '6h': 360,
    '12h': 720,
    '1d': 1440,
    '1w': 10080,
}


def load_ticker(stake, asset, ccxt_api=None):
    """
        this loads the ticker for the given stake and asset. If an ccxt exchange is provided we will loose it,
        otherwise we just going to create an internal exchange object

    :param stake:
    :param asset:
    :param ccxt_api:
    :return:
    """

    ccxt_api = _create_exchange(ccxt_api)

    ticker = ccxt_api.fetch_tickers()

    asset = asset.upper()
    stake = stake.upper()

    if "{}/{}".format(asset, stake) in ticker:
        return ticker["{}/{}".format(asset, stake)]
    else:
        return None


def _create_exchange(ccxt_api):
    if ccxt_api is None:
        # create new exchange object to fetch data
        return getattr(ccxt, "binance")({
            'apiKey': "",
            'secret': "",
            'password': "",
            'uid': "",
            'enableRateLimit': True,
        })
    elif isinstance(ccxt_api, str):
        return getattr(ccxt, ccxt_api)({
            'apiKey': "",
            'secret': "",
            'password': "",
            'uid': "",
            'enableRateLimit': True,
        })
    else:
        return ccxt_api


def historical_data(stake, currency, interval, from_date=0, ccxt_api=None, days=None):
    """

    :param stake: the stake currency, like USDT, BTC, ETH
    :param currency: the currency of choice, for example ETH

    these two will form your trade pair!

    :param interval: your desired interval in minutes,

    :param days: how many days in the past we want to download data for
    :param ccxt_api: If None we create our own api other we reuse it
    :param days if specified we fetch the last n days
    :return: the dataframe, containing the aggregated data
    """

    if days:
        from_date = (datetime.today() - timedelta(days=days)).timestamp()

    pair = "{}/{}".format(currency.upper(), stake.upper())

    ccxt_api = _create_exchange(ccxt_api)

    # taken from freqtrade for simplicity
    def get_ticker_history(pair: str, tick_interval: str, since_ms: Optional[int] = None) -> List[Dict]:
        try:
            # last item should be in the time interval [now - tick_interval, now]
            till_time_ms = arrow.utcnow().shift(
                minutes=-TICKER_INTERVAL_MINUTES[tick_interval]
            ).timestamp * 1000
            # it looks as if some exchanges return cached data
            # and they update it one in several minute, so 10 mins interval
            # is necessary to skeep downloading of an empty array when all
            # chached data was already downloaded
            till_time_ms = min(till_time_ms, arrow.utcnow().shift(minutes=-10).timestamp * 1000)

            data = []
            while not since_ms or since_ms < till_time_ms:
                data_part = ccxt_api.fetch_ohlcv(pair, timeframe=tick_interval, since=since_ms)

                if not data_part:
                    break

                logging.info('Downloaded data for %s time range [%s, %s]',
                             pair,
                             arrow.get(data_part[0][0] / 1000).format(),
                             arrow.get(data_part[-1][0] / 1000).format())

                data.extend(data_part)
                since_ms = data[-1][0] + 1

            return data
        except ccxt.NotSupported as e:
            raise Exception(
                'Exchange {} does not support fetching historical candlestick data.'
                'Message: {}'.format(ccxt_api.name, e)
            )
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise Exception(
                'Could not load ticker history due to {}. Message: {}'.format(
                    e.__class__.__name__, e))
        except ccxt.BaseError as e:
            raise Exception('Could not fetch ticker data. Msg: {}'.format(e))

    return get_ticker_history(pair, interval, since_ms=int(from_date * 1000))
