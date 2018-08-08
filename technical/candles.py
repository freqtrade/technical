import pandas as pd

def heikinashi(bars):
    bars = bars.copy()
    bars['ha_close'] = (bars['open'] + bars['high'] +
                        bars['low'] + bars['close']) / 4

    bars['ha_open'] = (bars['open'].shift(1) + bars['close'].shift(1)) / 2
    bars.loc[:1, 'ha_open'] = bars['open'].values[0]
    for x in range(2):
        bars.loc[1:, 'ha_open'] = (
                                          (bars['ha_open'].shift(1) + bars['ha_close'].shift(1)) / 2)[1:]

    bars['ha_high'] = bars.loc[:, ['high', 'ha_open', 'ha_close']].max(axis=1)
    bars['ha_low'] = bars.loc[:, ['low', 'ha_open', 'ha_close']].min(axis=1)

    return pd.DataFrame(
        index=bars.index,
        data={
            'open': bars['ha_open'],
            'high': bars['ha_high'],
            'low': bars['ha_low'],
            'close': bars['ha_close']})
