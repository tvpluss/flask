import pickle
from river import optim, reco, metrics, stream
import pandas as pd


class MFModel:
    def __init__(self, path) -> None:
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
        self.path = path

    def load_model(self):
        with open(self.path, 'rb') as f:
            self.model = pickle.load(f)

    def save_model(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self.model, f)

    def unload_model(self):
        del self.model

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

    def predict(self, user_id: str, books: pd.DataFrame, top: int = 10):
        predicted_ratings = []
        for row in books.itertuples():
            pred = self.model.predict_one(user_id, row.id)
            predicted_ratings.append(pred)
        books['pred_rating'] = predicted_ratings
        books = books.sort_values(
            by='pred_rating', ascending=False)

        return books.head(top) if top else books


if __name__ == '__main__':
    import time

    start_time = time.perf_counter()

    # Your code here

    model = MFModel()
    model.load_model('./model/MF_model.pkl')
    print('loaded model')
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    print(f"Elapsed time: {elapsed_time:.5f} seconds")
    # data = [['278066', '0062737465', 4],
    #         ['277978', '0896083535', 4],
    #         ['277965', '1888387408', 3]]
    # df = pd.DataFrame(data, columns=['user', 'item', 'rate'])
    # print(df)
    # print(model.test(df))
