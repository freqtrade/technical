"""
 the purpose of this file is to generate a history of pairs and stores them in a local database
 this allows us to quickly get past data for neural networks and if they don't exist this module will
 download the for us
"""
import datetime

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

_DECL_BASE = declarative_base()


def init():
    """
        setups our persistence for this module
    :return:
    """

    engine = create_engine(os.environ.get("TECHNICAL_HISTORY_DB", 'sqlite:///history.db'))
    session = scoped_session(sessionmaker(bind=engine, autoflush=True, autocommit=True))
    OHLCV.session = session
    OHLCV.query = session.query_property()
    _DECL_BASE.metadata.create_all(engine)


def load_data(pair, interval, days, ccxt_api="poloniex", force=False):
    """
        this method will try to load historical ticker data for the specified attribute
        from the local database, if they don't exist, it will download them from the remote
        exchange to it's best ability.

        By default it will utilize poloniex, since we can download years worth of data from them
    :param pair: which pair we want to use
    :param interval: a defined interval, like 5m
    :param days: how many days worth of data do we need, like 90
    :param ccxt_api: our cxxt object or the name of an exchange
    :param force: should we fetch all data and ignored previous persisted onces
    :return: a dataframe of all the related data, be aware that this can contain a lot of memory!
    """

    # generate exchange
    from technical.exchange import _create_exchange, historical_data
    ccxt_api = _create_exchange(ccxt_api)

    pair = pair.upper().split("/")
    stake = pair[1]
    asset = pair[0]

    # get newest data from the internal store for this pair

    latest_time = OHLCV.session.query(func.max(OHLCV.timestamp)).filter(
            OHLCV.exchange == ccxt_api.name,
            OHLCV.pair == "{}/{}".format(asset.upper(), stake.upper()),
            OHLCV.interval == interval
    ).one()[0]

    if force:
        print("forcing database refresh and downloading all data!")
        latest_time = None

    # add additional data on top
    if latest_time is None:
        print("init database for the last {} days".format(days))

        # store data for all
        for row in historical_data(stake, asset, interval, days, ccxt_api):
            o = OHLCV(
                id="{}-{}-{}/{}:{}".format(ccxt_api.name, interval, asset.upper(), stake.upper(), row[0]),
                exchange=ccxt_api.name,
                pair="{}/{}".format(asset.upper(), stake.upper()),
                interval=interval,
                open=row[1],
                close=row[4],
                high=row[2],
                low=row[3],
                volume=row[5],
                timestamp=datetime.datetime.utcfromtimestamp(row[0] / 1000)
            )
            OHLCV.session.merge(o)

    else:
        # calculate the difference in days and download and merge the data files
        date = datetime.datetime.now()

        to_fetch = (date - latest_time).days
        print("loading additional days: {}".format(to_fetch))

        for row in historical_data(stake, asset, interval, to_fetch, ccxt_api):
            o = OHLCV(
                id="{}-{}-{}/{}:{}".format(ccxt_api.name, interval, asset.upper(), stake.upper(), row[0]),
                exchange=ccxt_api.name,
                pair="{}/{}".format(asset.upper(), stake.upper()),
                interval=interval,
                open=row[1],
                close=row[4],
                high=row[2],
                low=row[3],
                volume=row[5],
                timestamp=datetime.datetime.utcfromtimestamp(row[0] / 1000)
            )
            OHLCV.session.merge(o)

    # return all data to user
    result = []

    # filter by exchange, currency and other pairs
    for row in OHLCV.session.query(OHLCV).filter(
            OHLCV.exchange == ccxt_api.name,
            OHLCV.pair == "{}/{}".format(asset.upper(), stake.upper()),
            OHLCV.interval == interval
    ).all():
        result.append([row.timestamp.timestamp(), row.open, row.high, row.low, row.close, row.volume])

    return result


class OHLCV(_DECL_BASE):
    """
    Class used to define a trade structure
    """
    __tablename__ = 'ohlcv'

    id = Column(String, primary_key=True)
    exchange = Column(String, nullable=False)
    pair = Column(String, nullable=False)
    interval = Column(String, nullable=False)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    def __repr__(self):
        return 'OHLCV(' \
               'id={}, ' \
               'pair={}, ' \
               'exchange={}, ' \
               'interval={}, ' \
               'open={}, ' \
               'close={}, ' \
               'low={}, ' \
               'high={}, ' \
               'volume={}, ' \
               'date={}' \
               ')'.format(
            self.id,
            self.pair,
            self.exchange,
            self.interval,
            self.open,
            self.close,
            self.low,
            self.high,
            self.volume,
            self.timestamp
        )


init()
