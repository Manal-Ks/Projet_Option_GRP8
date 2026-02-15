from __future__ import annotations
import numpy as np
from typing import Dict, Sequence
from ..config import DEFAULT_WEIGHTS
from .base import BaseAlgorithm

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier


class WSMAlgorithm(BaseAlgorithm):
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def fit(self, df_train, y_train=None):
        return self

    def predict(self, df_test) -> np.ndarray:
        cols = list(self.weights.keys())
        w = np.array([self.weights[c] for c in cols], dtype=float)
        w = w / (w.sum() if w.sum() > 0 else 1.0)
        X = np.vstack([df_test[c].fillna(0).astype(float).values for c in cols]).T
        scores = X.dot(w)
        return np.clip(scores, 0.0, 1.0)


class WPMAlgorithm(BaseAlgorithm):
    def __init__(self, weights: Dict[str, float] = None, eps: float = 1e-6):
        self.weights = weights or DEFAULT_WEIGHTS
        self.eps = eps

    def fit(self, df_train, y_train=None):
        return self

    def predict(self, df_test) -> np.ndarray:
        cols = list(self.weights.keys())
        ws = np.array([self.weights[c] for c in cols], dtype=float)
        X = np.vstack([df_test[c].fillna(0).astype(float).values + self.eps for c in cols]).T
        prod = np.prod(X ** ws, axis=1)
        sum_w = ws.sum() if ws.sum() > 0 else 1.0
        scores = prod ** (1.0 / sum_w)
        return np.clip(scores, 0.0, 1.0)


class TOPSISAlgorithm(BaseAlgorithm):
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def fit(self, df_train, y_train=None):
        return self

    def predict(self, df_test) -> np.ndarray:
        cols = list(self.weights.keys())
        W = np.array([self.weights[c] for c in cols], dtype=float)
        X = np.vstack([df_test[c].fillna(0).astype(float).values for c in cols]).T
        norm = np.sqrt((X ** 2).sum(axis=0))
        norm[norm == 0] = 1.0
        X_norm = X / norm
        Xw = X_norm * W
        ideal_best = Xw.max(axis=0)
        ideal_worst = Xw.min(axis=0)
        d_pos = np.sqrt(((Xw - ideal_best) ** 2).sum(axis=1))
        d_neg = np.sqrt(((Xw - ideal_worst) ** 2).sum(axis=1))
        scores = d_neg / (d_pos + d_neg + 1e-12)
        return np.clip(scores, 0.0, 1.0)


class LogisticRegressionAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.model = LogisticRegression(max_iter=200)
        self.features = None

    def fit(self, df_train, y_train):
        df = df_train.copy()
        self.features = self._build_features(df)
        self.model.fit(df[self.features], y_train)
        return self

    def _build_features(self, df):
        base = ["score_skills", "score_experience", "score_education", "score_languages", "score_sector"]
        feats = base + ["skills_experience", "education_languages", "sector_skills"]
        if "skills_experience" not in df.columns:
            df["skills_experience"] = df["score_skills"] * df["score_experience"]
        if "education_languages" not in df.columns:
            df["education_languages"] = df["score_education"] * df["score_languages"]
        if "sector_skills" not in df.columns:
            df["sector_skills"] = df["score_sector"] * df["score_skills"]
        return feats

    def predict(self, df_test) -> np.ndarray:
        df = df_test.copy()
        if self.features is None:
            self._build_features(df)
        df["skills_experience"] = df["score_skills"] * df["score_experience"]
        df["education_languages"] = df["score_education"] * df["score_languages"]
        df["sector_skills"] = df["score_sector"] * df["score_skills"]
        probs = self.model.predict_proba(df[self.features])[:, 1]
        return np.clip(probs, 0.0, 1.0)


class GradientBoostingAlgorithm(LogisticRegressionAlgorithm):
    def __init__(self):
        self.model = GradientBoostingClassifier()
        self.features = None


class RandomForestAlgorithm(LogisticRegressionAlgorithm):
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=50)
        self.features = None
