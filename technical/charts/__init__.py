from typing import List


def plot_dataframe(self, name, data, pair, indicators: List[str]):
    """
    plots our dataframe and stores it under the user data directory
    and a tick is closed
    :param name: base name of this chart, we wil automatically extend it with the pair and date infromation
    :param indicators: list of indicators
    :param data:
    :return:
    """

    import plotly.graph_objs as go
    from plotly import tools
    from plotly.offline import plot as plt

    def generate_row(fig, row, raw_indicators, data) -> tools.make_subplots:
        """
        Generator all the indicator selected by the user for a specific row
        """
        if raw_indicators is None or raw_indicators == "":
            return fig
        for indicator in raw_indicators.split(','):
            if indicator in data:
                scattergl = go.Scattergl(
                    x=data['date'],
                    y=data[indicator],
                    name=indicator
                )
            fig.append_trace(scattergl, row, 1)

        return fig

    rows = len(indicators)

    if rows < 3:
        rows = 3

    # Define the graph
    fig = tools.make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        row_width=[1, 1, 4],
        vertical_spacing=0.0001,
    )

    fig['layout'].update(title=pair)
    fig['layout']['yaxis1'].update(title='Price')
    fig['layout']['yaxis2'].update(title='Volume')
    fig['layout']['yaxis3'].update(title='Other')

    if rows > 3:
        for x in range(3, rows):
            fig['layout']['yaxis{}'.format(x)].update(title='Other {}'.format(x))

    # Common information
    candles = go.Candlestick(
        x=data.date,
        open=data.open,
        high=data.high,
        low=data.low,
        close=data.close,
        name='Price'
    )
    fig.append_trace(candles, 1, 1)

    # Row 2
    volume = go.Bar(
        x=data['date'],
        y=data['volume'],
        name='Volume'
    )
    fig.append_trace(volume, 2, 1)

    row = 0
    for indicator in indicators:
        row = row + 1
        print(row)
        generate_row(fig, row, indicator, data)

    from pathlib import Path
    plt(fig, auto_open=False, filename=str(
        Path('user_data').joinpath(
            "{}_analyze_{}_{}.html".format(name, self.ticker_interval, data['date'].iloc[-1]))))
