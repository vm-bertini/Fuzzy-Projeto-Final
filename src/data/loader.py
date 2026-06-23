import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import List, Tuple, Dict, Union

import config

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

_CATEGORICAL = {
    'heart': ['Sex', 'ChestPainType', 'FastingBS', 'RestingECG', 'ExerciseAngina', 'ST_Slope'],
    'pima':  [],
}

_META = {
    'heart': {'file': 'heart_failure.csv', 'target': 'HeartDisease', 'task': 'classification'},
    'pima':  {'file': 'pima_diabetes.csv', 'target': 'Outcome',      'task': 'classification'},
}


class PartialScaler:
    """
    StandardScaler que só padroniza features numéricas.
    Features categóricas mantêm seus códigos inteiros originais (0, 1, 2 …).

    mean_  e scale_  têm shape [n_features]:
      - feature numérica : mean/std reais da coluna
      - feature categórica : mean=0, scale=1  (identidade)

    Isso garante que plot_mf_anfis, plot_mf_fcm e ClassicFuzzyModel possam usar
    scaler.mean_[fi] / scaler.scale_[fi] para qualquer feature sem lógica especial.
    """

    def __init__(self) -> None:
        self._ss         = StandardScaler()
        self._num_idx: List[int] = []
        self.mean_:  np.ndarray = None
        self.scale_: np.ndarray = None

    def fit_transform(self, X: np.ndarray, numeric_idx: List[int]) -> np.ndarray:
        self._num_idx = numeric_idx
        n_feat = X.shape[1]
        self.mean_  = np.zeros(n_feat, dtype=np.float64)
        self.scale_ = np.ones(n_feat,  dtype=np.float64)
        out = X.copy()
        if numeric_idx:
            out[:, numeric_idx] = self._ss.fit_transform(X[:, numeric_idx])
            self.mean_[numeric_idx]  = self._ss.mean_
            self.scale_[numeric_idx] = self._ss.scale_
        return out

    def transform(self, X: np.ndarray) -> np.ndarray:
        out = X.copy()
        if self._num_idx:
            out[:, self._num_idx] = self._ss.transform(X[:, self._num_idx])
        return out


def _encode_categoricals(
    df: pd.DataFrame,
    cat_cols: List[str],
) -> Tuple[pd.DataFrame, Dict[str, Dict[int, str]]]:
    mappings: Dict[str, Dict[int, str]] = {}
    for col in cat_cols:
        if col not in df.columns:
            continue
        cat = pd.Categorical(df[col])
        mappings[col] = {i: str(v) for i, v in enumerate(cat.categories)}
        df[col] = cat.codes.astype(float)
    return df, mappings


def load_dataset(
    dataset: str = config.DATASET,
    test_size: float = 1.0 - config.TRAIN_RATIO,
    random_state: int = config.RANDOM_SEED,
) -> Tuple[
    torch.Tensor, torch.Tensor,
    torch.Tensor, torch.Tensor,
    List[str], str,
    PartialScaler,
    List[Union[str, int]],
    Dict[str, Dict[int, str]],
]:
    meta     = _META[dataset]
    cat_cols = _CATEGORICAL.get(dataset, [])
    path     = os.path.join(DATA_DIR, meta['file'])
    df       = pd.read_csv(path)

    if dataset == 'heart':
        for col in ('Cholesterol', 'RestingBP'):
            if col in df.columns:
                median_val = df.loc[df[col] > 0, col].median()
                df[col]    = df[col].replace(0, median_val)

    df, cat_mappings = _encode_categoricals(df, cat_cols)

    target_col    = meta['target']
    feature_names = [c for c in df.columns if c != target_col]
    X = df[feature_names].values.astype(np.float32)
    y = df[target_col].values.astype(np.float32)

    feature_types: List[Union[str, int]] = []
    for fname in feature_names:
        if fname in cat_mappings:
            feature_types.append(len(cat_mappings[fname]))
        else:
            feature_types.append('gaussian')

    numeric_idx = [i for i, ft in enumerate(feature_types) if ft == 'gaussian']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    scaler  = PartialScaler()
    X_train = scaler.fit_transform(X_train, numeric_idx).astype(np.float32)
    X_test  = scaler.transform(X_test).astype(np.float32)

    return (
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(X_test,  dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32).unsqueeze(1),
        torch.tensor(y_test,  dtype=torch.float32).unsqueeze(1),
        feature_names, meta['task'], scaler, feature_types, cat_mappings,
    )
