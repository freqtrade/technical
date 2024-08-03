import pandas as pd
import talib.abstract as ta

from technical.qtpylib import crossed_above


class Consensus:
    """
    This file provides you with the consensus indicator and all associated helper methods.

    The idea is based on the concept that, if you have one indicator telling you to buy
    things are great.
    If 100 indicators are telling you to buy at the same time, things are better.

    If we can now have an easily understandable score, things should be perfect.

    Configuration:

    Each of the utility methods utilizes the default parameters as based in the literature.
    Assuming that these are the signals, most trades will use.

    Usage:

    1.

    from technical.consensus import Consensus

    c = Consensus(dataframe)

    2.

    call the indicators you would like to have evaluated in your consensus model
    with optional parameters. Like the impact

    c.evaluate_rsi()

    3. call the score method. This will basically compute 2 scores for you, which can be easily
    plotted

    c.score()

    if you like to apply some smoothing, you can call

    c.score(smooth=3)

    for example.


    """

    def __init__(self, dataframe: pd.DataFrame):
        """
        initializes the consensus object.
        :param dataframe: dataframe to evaluate
        """
        self.dataframe = dataframe.copy()
        self.buy_weights = 0
        self.sell_weights = 0

    def _weights(self, impact_buy, impact_sell):
        """
        helper method to compute total count of utilized indicators and their weights
        :param impact_buy:
        :param impact_sell:
        :return:
        """
        self.buy_weights = self.buy_weights + impact_buy
        self.sell_weights = self.sell_weights + impact_sell

    def score(self, prefix="consensus", smooth=None):
        """
        this computes the consensus score, which should always be between 0 and 100
        :param prefix:
        :param smooth: Allows to specify an integer for a smoothing interval
        :return:
        """
        dataframe = self.dataframe
        scores = dataframe.filter(regex="^(buy|sell)_.*").fillna(0)

        # computes a score between 0 and 100. The closer to 100 the more aggrement
        dataframe.loc[:, f"{prefix}_score_sell"] = (
            scores.filter(regex="^(sell)_.*").sum(axis=1) / self.sell_weights * 100
        )
        dataframe.loc[:, f"{prefix}_score_buy"] = (
            scores.filter(regex="^(buy)_.*").sum(axis=1) / self.buy_weights * 100
        )

        if smooth is not None:
            dataframe[f"{prefix}_score_buy"] = (
                dataframe[f"{prefix}_score_buy"].rolling(smooth).mean()
            )
            dataframe[f"{prefix}_score_sell"] = (
                dataframe[f"{prefix}_score_sell"].rolling(smooth).mean()
            )

        return {
            "sell": dataframe[f"{prefix}_score_sell"],
            "buy": dataframe[f"{prefix}_score_buy"],
            "buy_agreement": scores.filter(regex="^(buy)_.*").sum(axis=1),
            "sell_agreement": scores.filter(regex="^(sell)_.*").sum(axis=1),
            "buy_disagreement": scores.filter(regex="^(buy)_.*").count(axis=1)
            - scores.filter(regex="^(buy)_.*").sum(axis=1),
            "sell_disagreement": scores.filter(regex="^(sell)_.*").count(axis=1)
            - scores.filter(regex="^(sell)_.*").sum(axis=1),
        }

    def evaluate_rsi(self, period=14, prefix="rsi", impact_buy=1, impact_sell=1):
        """
        evaluates a s
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        self._weights(impact_buy, impact_sell)

        name = f"{prefix}_{period}"
        dataframe = self.dataframe
        dataframe[name] = ta.RSI(dataframe, timeperiod=period)

        dataframe.loc[(dataframe[name] < 30), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] > 70), f"sell_{name}"] = 1 * impact_sell

    def evaluate_stoch(self, prefix="stoch", impact_buy=1, impact_sell=1):
        """
        evaluates the stochastic fast
        :param dataframe:
        :param prefix:
        :return:
        """
        name = f"{prefix}"
        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        stoch_fast = ta.STOCHF(dataframe, 5, 3, 0, 3, 0)

        dataframe[f"{name}_fastd"] = stoch_fast["fastd"]
        dataframe[f"{name}_fastk"] = stoch_fast["fastk"]

        dataframe.loc[(dataframe[f"{name}_fastk"] < 20), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[f"{name}_fastk"] > 80), f"sell_{name}"] = 1 * impact_sell

    def evaluate_stoch_rsi(
        self, period=14, smoothd=3, smoothk=3, prefix="stoch_rsi", impact_buy=1, impact_sell=1
    ):
        """
        evaluates the stochastic rsi fast (TradingView version)
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """

        name = f"{prefix}_{period}"
        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe

        # We don't use the talib.STOCHRSI library because it seems
        # like the results are not identical to Trading View's version
        dataframe[f"rsi_{period}"] = ta.RSI(dataframe, timeperiod=period)
        stochrsi = (
            dataframe[f"rsi_{period}"] - dataframe[f"rsi_{period}"].rolling(period).min()
        ) / (
            dataframe[f"rsi_{period}"].rolling(period).max()
            - dataframe[f"rsi_{period}"].rolling(period).min()
        )

        dataframe[f"{name}_fastk"] = stochrsi.rolling(smoothk).mean() * 100
        # The fastd below is not used
        dataframe[f"{name}_fastd"] = dataframe[f"{name}_fastk"].rolling(smoothd).mean()

        dataframe.loc[(dataframe[f"{name}_fastk"] < 20), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[f"{name}_fastk"] > 80), f"sell_{name}"] = 1 * impact_sell

    def evaluate_macd_cross_over(self, prefix="macd_crossover", impact_buy=2, impact_sell=2):
        """
        evaluates the MACD if we should buy or sale based on a crossover
        :param dataframe:
        :param prefix:
        :return:
        """

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        macd = ta.MACD(dataframe)
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]
        dataframe["macdhist"] = macd["macdhist"]

        dataframe.loc[
            (crossed_above(dataframe["macdsignal"], dataframe["macd"])), f"sell_{prefix}"
        ] = 1 * impact_sell

        dataframe.loc[
            (crossed_above(dataframe["macd"], dataframe["macdsignal"])), f"buy_{prefix}"
        ] = 1 * impact_buy

        return dataframe

    def evaluate_macd(self, prefix="macd", impact_buy=1, impact_sell=1):
        """
        evaluates the MACD if we should buy or sale
        :param dataframe:
        :param prefix:
        :return:
        """

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        macd = ta.MACD(dataframe)
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]
        dataframe["macdhist"] = macd["macdhist"]

        # macd < macds & macd < 0 == sell
        dataframe.loc[
            ((dataframe["macd"] < dataframe["macdsignal"]) & (dataframe["macd"] < 0)),
            f"sell_{prefix}",
        ] = impact_sell

        # macd > macds & macd > 0 == buy
        dataframe.loc[
            ((dataframe["macd"] > dataframe["macdsignal"]) & (dataframe["macd"] > 0)),
            f"buy_{prefix}",
        ] = impact_buy

        return dataframe

    def evaluate_hull(self, period=9, field="close", prefix="hull", impact_buy=1, impact_sell=1):
        """
        evaluates a hull moving average
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        from technical.indicators import hull_moving_average

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}_{field}_{period}"
        dataframe[name] = hull_moving_average(dataframe, period, field)

        dataframe.loc[(dataframe[name] > dataframe[field]), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] < dataframe[field]), f"sell_{name}"] = 1 * impact_sell

    def evaluate_vwma(self, period=9, prefix="vwma", impact_buy=1, impact_sell=1):
        """
        evaluates a volume weighted moving average
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        from technical.indicators import vwma

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}_{period}"
        dataframe[name] = vwma(dataframe, period)

        dataframe.loc[(dataframe[name] > dataframe["close"]), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] < dataframe["close"]), f"sell_{name}"] = 1 * impact_sell

    def evaluate_tema(self, period, field="close", prefix="tema", impact_buy=1, impact_sell=1):
        """
        evaluates a tema moving average
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}_{field}_{period}"
        dataframe[name] = ta.TEMA(dataframe, timeperiod=period, field=field)

        dataframe.loc[(dataframe[name] < dataframe[field]), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] > dataframe[field]), f"sell_{name}"] = 1 * impact_sell

    def evaluate_ema(self, period, field="close", prefix="ema", impact_buy=1, impact_sell=1):
        """
        evaluates a sma moving average
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}_{field}_{period}"
        dataframe[name] = ta.EMA(dataframe, timeperiod=period, field=field)

        dataframe.loc[(dataframe[name] < dataframe[field]), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] > dataframe[field]), f"sell_{name}"] = 1 * impact_sell

    def evaluate_sma(self, period, field="close", prefix="sma", impact_buy=1, impact_sell=1):
        """
        evaluates a sma moving average
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        self._weights(impact_buy, impact_sell)
        name = f"{prefix}_{field}_{period}"
        dataframe = self.dataframe
        dataframe[name] = ta.SMA(dataframe, timeperiod=period, field=field)

        dataframe.loc[(dataframe[name] < dataframe[field]), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] > dataframe[field]), f"sell_{name}"] = 1 * impact_sell

    def evaluate_laguerre(self, prefix="lag", impact_buy=1, impact_sell=1):
        """
        evaluates the laguerre
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        from technical.indicators import laguerre

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}"
        dataframe[name] = laguerre(dataframe)

        dataframe.loc[(dataframe[name] < 0.1), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] > 0.9), f"sell_{name}"] = 1 * impact_sell

    def evaluate_osc(self, period=12, prefix="osc", impact_buy=1, impact_sell=1):
        """
        evaluates the osc
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        from technical.indicators import osc

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}_{period}"
        dataframe[name] = osc(dataframe, period)

        dataframe.loc[(dataframe[name] < 0.3), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] > 0.8), f"sell_{name}"] = 1 * impact_sell

    def evaluate_cmf(self, period=12, prefix="cmf", impact_buy=1, impact_sell=1):
        """
        evaluates the cmf
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        from technical.indicators import cmf

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}_{period}"
        dataframe[name] = cmf(dataframe, period)

        dataframe.loc[(dataframe[name] > 0.5), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] < -0.5), f"sell_{name}"] = 1 * impact_sell

    def evaluate_cci(
        self, period=20, prefix="cci", impact_buy=1, impact_sell=1, sell_signal=100, buy_signal=-100
    ):
        """
        evaluates the cci
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}_{period}"
        dataframe[name] = ta.CCI(dataframe, timeperiod=period)

        dataframe.loc[(dataframe[name] < buy_signal), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] > sell_signal), f"sell_{name}"] = 1 * impact_sell

    def evaluate_consensus(
        self,
        consensus,
        prefix,
        smooth=0,
        buy_score=80,
        sell_score=80,
        impact_buy=1,
        impact_sell=1,
        average=False,
    ):
        """
        evaluates another consensus indicator
        and integrates it into this indicator
        :param dataframe:
        :param period:
        :param prefix:
        :param average: should an average based approach be used or the total computed weight
        :return:
        """

        if average:
            self._weights(impact_buy, impact_sell)
        else:
            self._weights(consensus.buy_weights, consensus.sell_weights)

        dataframe = self.dataframe
        name = f"{prefix}_"

        result = {}
        if smooth > 0:
            result = consensus.score(smooth=smooth)
        else:
            result = consensus.score()

        dataframe[f"{name}_buy"] = result["buy"]
        dataframe[f"{name}_sell"] = result["sell"]

        if average:
            dataframe.loc[(dataframe[f"{name}_buy"] > buy_score), f"buy_{name}"] = 1 * impact_buy

            dataframe.loc[(dataframe[f"{name}_sell"] >= sell_score), f"sell_{name}"] = (
                1 * impact_sell
            )
        else:
            dataframe.loc[(dataframe[f"{name}_buy"] > buy_score), f"buy_{name}"] = (
                consensus.buy_weights * impact_buy
            )

            dataframe.loc[(dataframe[f"{name}_sell"] >= sell_score), f"sell_{name}"] = (
                consensus.sell_weights * impact_sell
            )

    def evaluate_cmo(self, period=20, prefix="cmo", impact_buy=1, impact_sell=1):
        """
        evaluates the cmo
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}_{period}"
        dataframe[name] = ta.CMO(dataframe, timeperiod=period)

        dataframe.loc[(dataframe[name] < -50), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] > 50), f"sell_{name}"] = 1 * impact_sell

    def evaluate_ichimoku(self, prefix="ichimoku", impact_buy=1, impact_sell=1):
        """
        evaluates the ichimoku
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        from technical.indicators import ichimoku

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}"
        ichimoku = ichimoku(dataframe)

        dataframe[f"{name}_tenkan_sen"] = ichimoku["tenkan_sen"]
        dataframe[f"{name}_kijun_sen"] = ichimoku["kijun_sen"]
        dataframe[f"{name}_senkou_span_a"] = ichimoku["senkou_span_a"]
        dataframe[f"{name}_senkou_span_b"] = ichimoku["senkou_span_b"]
        dataframe[f"{name}_chikou_span"] = ichimoku["chikou_span"]

        # price is above the cloud
        dataframe.loc[
            (
                (dataframe[f"{name}_senkou_span_a"] > dataframe["open"])
                & (dataframe[f"{name}_senkou_span_b"] > dataframe["open"])
            ),
            f"buy_{name}",
        ] = impact_buy

        # price is below the cloud
        dataframe.loc[
            (
                (dataframe[f"{name}_senkou_span_a"] < dataframe["open"])
                & (dataframe[f"{name}_senkou_span_b"] < dataframe["open"])
            ),
            f"sell_{name}",
        ] = impact_sell

    def evaluate_ultimate_oscilator(self, prefix="uo", impact_buy=1, impact_sell=1):
        """
        evaluates the ultimate_oscilator
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}"
        dataframe[name] = ta.ULTOSC(dataframe)

        dataframe.loc[(dataframe[name] < 30), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] > 70), f"sell_{name}"] = 1 * impact_sell

    def evaluate_williams(self, prefix="williams", impact_buy=1, impact_sell=1):
        """
        evaluates the williams
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """
        from technical.indicators import williams_percent

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}"
        dataframe[name] = williams_percent(dataframe)

        dataframe.loc[(dataframe[name] < -80), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] > -20), f"sell_{name}"] = 1 * impact_sell

    def evaluate_momentum(self, period=20, prefix="momentum", impact_buy=1, impact_sell=1):
        """
        evaluates the momentum
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}_{period}"
        dataframe[name] = ta.MOM(dataframe, timeperiod=period)

        dataframe.loc[(dataframe[name] > 100), f"buy_{name}"] = 1 * impact_buy

        dataframe.loc[(dataframe[name] < 100), f"sell_{name}"] = 1 * impact_sell

    def evaluate_adx(
        self, period=14, prefix="adx", trend_line=25, use_di=True, impact_buy=1, impact_sell=1
    ):
        """
        evaluates the adx (optionally use plus_di and minus_di to detect buy or sell)
        :param dataframe:
        :param period:
        :param prefix:
        :param trend_line: The ADX value at which we consider that a trend is present (Default: 25)
        :param use_di: Enable/disable the usage of plus_di and minus_di (Default: Enabled)
        :return:
        """

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}_{period}"
        dataframe[name] = ta.ADX(dataframe, timeperiod=period)

        # We can use PLUS_DI and MINUS_DI to be able to detect if we should buy or sell
        # See https://www.investopedia.com/articles/trading/07/adx-trend-indicator.asp
        if use_di:
            dataframe[f"{name}_plus_di"] = ta.PLUS_DI(dataframe, timeperiod=period)
            dataframe[f"{name}_minus_di"] = ta.MINUS_DI(dataframe, timeperiod=period)

            dataframe.loc[
                (
                    (dataframe[name] > trend_line)
                    & (dataframe[f"{name}_plus_di"] > dataframe[f"{name}_minus_di"])
                ),
                f"buy_{name}",
            ] = 1 * impact_buy

            dataframe.loc[
                (
                    (dataframe[name] > trend_line)
                    & (dataframe[f"{name}_plus_di"] < dataframe[f"{name}_minus_di"])
                ),
                f"sell_{name}",
            ] = 1 * impact_sell
        else:
            dataframe.loc[(dataframe[name] > trend_line), f"buy_{name}"] = 1 * impact_buy

            dataframe.loc[(dataframe[name] > trend_line), f"sell_{name}"] = 1 * impact_sell

    def evaluate_ao(self, prefix="ao", impact_buy=1, impact_sell=1):
        """
        evaluates the ao (Awesome Oscillator)
        :param dataframe:
        :param prefix:
        :return:
        """
        from technical.qtpylib import awesome_oscillator

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}"
        dataframe[name] = awesome_oscillator(dataframe)

        dataframe.loc[(dataframe[name] > (dataframe[name].shift(1) + 0.05)), f"buy_{name}"] = (
            1 * impact_buy
        )

        dataframe.loc[(dataframe[name] < (dataframe[name].shift(1) - 0.05)), f"sell_{name}"] = (
            1 * impact_sell
        )

    def evaluate_bbp(self, period=13, prefix="bbp", impact_buy=1, impact_sell=1):
        """
        evaluates the bbp (Bears Bulls Power)
        :param dataframe:
        :param period:
        :param prefix:
        :return:
        """

        self._weights(impact_buy, impact_sell)
        dataframe = self.dataframe
        name = f"{prefix}_{period}"

        # Bears/Bulls Power is using EMA
        dataframe[f"{name}_ema"] = ta.EMA(dataframe, timeperiod=period)
        dataframe[f"{name}_bulls"] = dataframe["high"] - dataframe[f"{name}_ema"]
        dataframe[f"{name}_bears"] = dataframe["low"] - dataframe[f"{name}_ema"]

        dataframe.loc[
            (
                (dataframe[f"{name}_ema"] > dataframe[f"{name}_ema"].shift(1))
                & (dataframe[f"{name}_bulls"] > dataframe[f"{name}_bulls"].shift(1))
            ),
            f"buy_{name}",
        ] = 1 * impact_buy

        dataframe.loc[
            (
                (dataframe[f"{name}_ema"] < dataframe[f"{name}_ema"].shift(1))
                & (dataframe[f"{name}_bears"] > dataframe[f"{name}_bears"].shift(1))
            ),
            f"sell_{name}",
        ] = 1 * impact_sell
