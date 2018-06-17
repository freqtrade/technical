from keras import Sequential
from pandas import DataFrame
from numpy import mean, std, array


class SNNR:
    """
    provides a single neural regression for 1 feature
    """

    def normalize(self, data) -> DataFrame:
        """
            normalizes the incomming dataframe
        :param data:
        :return:
        """
        X = [(array(data) - mean(data)) / std(data) for x in X]

    def build_model(self, training_epochs, trainning_data) -> Sequential:
        """"""

        pass
