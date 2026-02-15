from __future__ import annotations
from typing import Any
import numpy as np


class BaseAlgorithm:
    def fit(self, df_train, y_train: Any = None):
        raise NotImplementedError()

    def predict(self, df_test) -> np.ndarray:
        raise NotImplementedError()
