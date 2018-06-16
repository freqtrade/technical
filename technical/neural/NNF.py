import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential


class NNF:

    def run(self, dataframe):

        print(dataframe)

        dataframe['date'] = dataframe['date'].apply(lambda x: x.timestamp())
        # Reorder the columns for convenience
        data = dataframe[['open', 'high', 'low', 'volume', 'close']]

        data.head()

        sequence_length = 21  # 20 preceeding inputs
        n_features = len(data.columns)
        val_ratio = 0.1
        n_epochs = 5
        batch_size = 512

        data = data.as_matrix()
        data_processed = []
        for index in range(len(data) - sequence_length):
            data_processed.append(data[index: index + sequence_length])
        data_processed = np.array(data_processed)

        val_split = round((1 - val_ratio) * data_processed.shape[0])
        train = data_processed[: int(val_split), :]
        val = data_processed[int(val_split):, :]

        print('Training data: {}'.format(train.shape))
        print('Validation data: {}'.format(val.shape))

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

        model = Sequential()
        model.add(LSTM(input_shape=(X_train.shape[1:]), units=128, return_sequences=True))
        model.add(Dropout(0.5))
        model.add(LSTM(128, return_sequences=False))
        model.add(Dropout(0.25))
        model.add(Dense(units=1))
        model.add(Activation("linear"))

        model.compile(loss="mse", optimizer="adam")

        history = model.fit(
            X_train,
            y_train,
            batch_size=batch_size,
            epochs=n_epochs,
            verbose=1
        )

        preds_val = model.predict(X_val)
        diff = []
        for i in range(len(y_val)):
            pred = preds_val[i][0]
            diff.append(y_val[i] - pred)

        real_min = preprocessor.data_min_[104]
        real_max = preprocessor.data_max_[104]
        print(preprocessor.data_min_[104])
        print(preprocessor.data_max_[104])

        preds_real = preds_val * (real_max - real_min) + real_min
        y_val_real = y_val * (real_max - real_min) + real_min

        plt.plot(preds_real, label='Predictions')
        plt.plot(y_val_real, label='Actual values')
        plt.xlabel('test')
        plt.legend(loc=0)
        plt.show()
