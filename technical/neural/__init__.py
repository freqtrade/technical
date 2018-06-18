"""

this module will provide neural network based technical indicators to remove the complexity of them from the user
"""
from pandas import DataFrame


def nnf(dataframe: DataFrame,
        training_data: DataFrame,
        features=('open', 'high', 'low', 'volume', 'close'),
        epoch=100,
        input_len_for_prediction=20,
        forecast=10
        ) -> dict:
    """
        this neural network will classify if the price goes up (1) or down (-1)
    :param dataframe: dataframe with our ticker data
    :param pair: trading pair we are interested in
    :param forecast_period: how far in the future do we want to forecast. This is given in candles
    :param exchange: Exchange to us, if None, we create our own exchange object
    :param historical_data_set_size: how many historical data do we want to use, in days
    :param features - which features we want to evaluate
    :return:
    """
    from technical.neural.NNF import NNF
    from numpy import append

    model = NNF(training_data, features=features, n_epochs=epoch,
                input_len_for_prediction=input_len_for_prediction)

    values = dataframe['close'].values
    for i in range(forecast):
        print("evaluating: {}".format(len(values)))
        forecasted = model.forecast(values)
        values = append(values, forecasted)

    import matplotlib.pyplot as plt

    plt.plot(values, label='Forecasted')
    plt.plot(dataframe[features[0]], label='Actual values')
    plt.xlabel('real prediction - {}'.format(features))
    plt.legend(loc=0)
    plt.show()

    pass


def mnnf(dataframe: DataFrame,
         training_data: DataFrame,
         features=('open', 'high', 'low', 'volume', 'close'),
         epoch=100,
         input_len_for_prediction=2
         ):
    from technical.neural.MNNF import MNNF
    MNNF().run(input=dataframe,
               training=training_data, features=features, n_epochs=epoch,
               input_len_for_prediction=input_len_for_prediction)
