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

    engine = create_engine(os.environ.get("TECHNICAL_HISTORY_DB", 'sqlite://'))
    session = scoped_session(sessionmaker(bind=engine, autoflush=True, autocommit=True))
    OHLCV.session = session
    OHLCV.query = session.query_property()
    _DECL_BASE.metadata.create_all(engine)


def load_data(pair, interval, from_date=0, ccxt_api="poloniex", force=False,
              till_date=datetime.datetime.now().timestamp(), days=None):
    """
        this method will try to load historical ticker data for the specified attribute
        from the local database, if they don't exist, it will download them from the remote
        exchange to it's best ability.

        By default it will utilize poloniex, since we can download years worth of data from them
    :param pair: which pair we want to use
    :param interval: a defined interval, like 5m
    :param ccxt_api: our cxxt object or the name of an exchange
    :param force: should we fetch all data and ignored previous persisted onces
    :param till_date: until when do we want to load data (default is now)
    :param from_date: when do we want to start loading data (default is epoch 0)
    :params days: if specified we will calculates the from data based on days

    :return: a dataframe of all the related data, be aware that this can contain a lot of memory!
    """

    if days:
        print("ignoring from data and fetching {}".format(days))
        from_date = (datetime.datetime.today() - datetime.timedelta(days=days)).timestamp()

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

        # store data for all
        for row in historical_data(stake, asset, interval, from_date, ccxt_api):
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
                timestamp=row[0]
            )
            OHLCV.session.merge(o)

    else:
        # calculate the difference in days and download and merge the data files

        for row in historical_data(stake, asset, interval, latest_time, ccxt_api):
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
                timestamp=row[0]
            )
            OHLCV.session.merge(o)

    # return all data to user
    result = []

    # filter by exchange, currency and other pairs
    for row in OHLCV.session.query(OHLCV).filter(
            OHLCV.exchange == ccxt_api.name,
            OHLCV.pair == "{}/{}".format(asset.upper(), stake.upper()),
            OHLCV.interval == interval,
            OHLCV.timestamp >= from_date * 1000,
            OHLCV.timestamp <= till_date * 1000,
    ).all():
        result.append([row.timestamp, row.open, row.high, row.low, row.close, row.volume])

    return result


class OHLCV(_DECL_BASE):
    """
    Class used to define a trade structure
    """
    __tablename__ = 'ohlcv'

    id = Column(String, primary_key=True)
    exchange = Column(String, nullable=False, index=True)
    pair = Column(String, nullable=False, index=True)
    interval = Column(String, nullable=False, index=True)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False, index=True)

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
