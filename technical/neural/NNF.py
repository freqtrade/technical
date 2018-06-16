import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from keras.layers import TimeDistributed, Flatten
from sklearn.preprocessing import MinMaxScaler

from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential


class NNF:
    """
    this neural network forecasts
    """

    def run(self, dataframe, input_len_for_prediction=20, n_epochs=50,
            features=('open', 'high', 'low', 'volume', 'close')):

        print("evaluating features: {} ({})".format(len(features), features))
        model = self.build(dataframe[:-input_len_for_prediction], input_len_for_prediction, n_epochs, features)

    def build(self, dataframe, input_len_for_prediction, n_epochs,
              features) -> Sequential:
        """
            this builds the actual model. The dataframe will be split into training and validation data

        :param dataframe: longterm data, which will be used for training and validation. Needs to have all features
        you care about
        :param input_len_for_prediction: how many input data are required for the prediction
        :param n_epochs: on how many epochs do we want to train it
        :param features: which features do we want to use to train the network
        :return:
        """

        # limit the dataframe to the features we want
        data = dataframe[list(features)]

        data.head()

        sequence_length = input_len_for_prediction  # preceeding inputs required for training
        n_features = len(data.columns)
        val_ratio = 0.1

        batch_size = 512

        data = data.as_matrix()
        data_processed = []
        for index in range(len(data) - sequence_length):
            data_processed.append(data[index: index + sequence_length])
        data_processed = np.array(data_processed)

        val_split = round((1 - val_ratio) * data_processed.shape[0])
        train = data_processed[: int(val_split), :]
        val = data_processed[int(val_split):, :]

        train_samples, train_nx, train_ny = train.shape
        val_samples, val_nx, val_ny = val.shape

        train = train.reshape((train_samples, train_nx * train_ny))
        val = val.reshape((val_samples, val_nx * val_ny))

        preprocessor = MinMaxScaler().fit(train)
        train = preprocessor.transform(train)
        val = preprocessor.transform(val)

        train = train.reshape((train_samples, train_nx, train_ny))
        val = val.reshape((val_samples, val_nx, val_ny))

        X_train = train[:, : -1]
        y_train = train[:, -1][:, -1]

        X_val = val[:, : -1]
        y_val = val[:, -1][:, -1]

        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], n_features))
        X_val = np.reshape(X_val, (X_val.shape[0], X_val.shape[1], n_features))

        print('Training data: {}'.format(train.shape))
        print('Validation data: {}'.format(val.shape))

        model = Sequential()
        model.add(LSTM(input_shape=(X_train.shape[1:]), units=128, return_sequences=True))
        model.add(Dropout(0.5))
        model.add(LSTM(128, return_sequences=False))
        model.add(Dropout(0.25))
        model.add(Dense(units=1))
        model.add(Activation("linear"))

        model.compile(loss='mse', optimizer="adam")

        model.summary()
        history = model.fit(
            X_train,
            y_train,
            batch_size=batch_size,
            epochs=n_epochs,
            verbose=0
        )

        print('Prediction input data: {}'.format(X_val.shape))
        print(X_val)

        preds_val = model.predict(X_val)
        diff = []
        for i in range(len(y_val)):
            pred = preds_val[i][0]
            diff.append(y_val[i] - pred)

        index = n_features * sequence_length - 1
        real_min = preprocessor.data_min_[index]
        real_max = preprocessor.data_max_[index]

        # re normalize data
        preds_real = preds_val * (real_max - real_min) + real_min
        y_val_real = y_val * (real_max - real_min) + real_min

        print('Predicted data: {}'.format(preds_real.shape))

        plt.plot(preds_real, label='Predictions')
        plt.plot(y_val_real, label='Actual values')
        plt.xlabel('test - {}'.format(features))
        plt.legend(loc=0)
        plt.show()

        # print(preds_real)
        # print(y_val_real)

        return model
