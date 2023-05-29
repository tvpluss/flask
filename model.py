import pickle
from river import optim, reco, metrics, stream
import pandas as pd


class MFModel:
    def __init__(self) -> None:
        biased_mf_params = {
            'n_factors': 10,
            'bias_optimizer': optim.SGD(0.025),
            'latent_optimizer': optim.SGD(0.05),
            'weight_initializer': optim.initializers.Zeros(),
            'latent_initializer': optim.initializers.Normal(mu=0., sigma=0.1, seed=73),
            'l2_bias': 0.,
            'l2_latent': 0.
        }
        self.model = reco.BiasedMF(**biased_mf_params)

    def load_model(self, path):
        with open(path, 'rb') as f:
            self.model = pickle.load(f)

    def save_model(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)

    def transform(self, df: pd.DataFrame):
        y = df.pop('rate')
        return stream.iter_pandas(df, y)

    def test(self, data: pd.DataFrame):
        res = []
        # model = reco.RandomNormal(seed=42)
        metric = metrics.MAE() + metrics.RMSE()
        X_y = self.transform(data)
        cnt = 0
        for x, y in X_y:
            y_pred = self.model.predict_one(user=x['user'], item=x['item'])
            metric.update(y_pred=y_pred, y_true=y)
            cnt += 1
        print('On testing', cnt, metric)
        res.extend(metric.get())
        return res

    def train(self, data: pd.DataFrame):
        res = []
        # model = reco.RandomNormal(seed=42)
        metric = metrics.MAE() + metrics.RMSE()
        X_y = self.transform(data)
        cnt = 0
        for x, y in X_y:
            y_pred = self.model.predict_one(user=x['user'], item=x['item'])

            metric.update(y_pred=y_pred, y_true=y)
            _ = self.model.learn_one(user=x['user'], item=x['item'], x=x, y=y)
            cnt += 1
        print('On training', cnt, metric)
        res.extend(metric.get())
        return res


if __name__ == '__main__':
    model = MFModel()
    model.load_model('./model/MF_model.pkl')
    data = [['278066', '0062737465', 4],
            ['277978', '0896083535', 4],
            ['277965', '1888387408', 3]]
    df = pd.DataFrame(data, columns=['user', 'item', 'rate'])
    print(df)
    print(model.test(df))
