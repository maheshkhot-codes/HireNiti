import os

import joblib
import numpy as np

from xgboost import XGBRanker


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "ranking_model.json"
)


class RecruitmentRanker:

    def __init__(self):

        self.model = XGBRanker(
            objective="rank:ndcg",
            n_estimators=100,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )

        self.is_trained = False

        if os.path.exists(MODEL_PATH):
            self.load()


    def train(
        self,
        X,
        y,
        group
    ):

        X = np.asarray(X)

        y = np.asarray(y)

        group = np.asarray(group)

        self.model.fit(
            X,
            y,
            qid=np.repeat(
                np.arange(len(group)),
                group
            )
        )

        self.is_trained = True

        self.save()


    def predict(
        self,
        X
    ):

        if not self.is_trained:
            raise RuntimeError(
                "Ranking model has not been trained yet"
            )

        X = np.asarray(X)

        return self.model.predict(X)


    def save(self):

        self.model.save_model(
            MODEL_PATH
        )


    def load(self):

        self.model.load_model(
            MODEL_PATH
        )

        self.is_trained = True


ranker = RecruitmentRanker()