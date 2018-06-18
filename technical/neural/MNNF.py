

class MNNF:
    """
        a neural network, based on several internal neural networks to forecast
        values a certain time in the future

    """

    def run(self, input, training, input_len_for_prediction=20, n_epochs=50, forcast=7,
            features=('open', 'high', 'low', 'volume', 'close')):

        # we should
        nnf = []
        for x in features:
            nnf.append(self.build(training, input_len_for_prediction, n_epochs, x))

        for index, network in enumerate(nnf, start=0):
            data = input[features[index]]

            print(data)
            for d in range(forcast):
                value = network.predict(data)
                print(value)
