"""Fuzzy C-Means — algoritmo de Bezdek."""
import numpy as np


class FuzzyCMeans:
    def __init__(self, n_clusters: int, fuzziness: float = 2.0, max_iter: int = 300, tol: float = 1e-6):
        self.c        = n_clusters
        self.m        = fuzziness
        self.max_iter = max_iter
        self.tol      = tol
        self.centers_: np.ndarray = None   # [c, d]
        self.u_:       np.ndarray = None   # [n_samples, c]

    def fit(self, X: np.ndarray) -> 'FuzzyCMeans':
        n, _ = X.shape
        rng = np.random.default_rng(42)
        U = rng.random((n, self.c))
        U /= U.sum(axis=1, keepdims=True)

        for _ in range(self.max_iter):
            U_prev = U.copy()
            Um = U ** self.m                                           # [n, c]
            self.centers_ = (Um.T @ X) / Um.sum(axis=0)[:, None]     # [c, d]

            dist = np.linalg.norm(
                X[:, None, :] - self.centers_[None, :, :], axis=2
            )                                                          # [n, c]
            dist = np.maximum(dist, 1e-10)
            exp   = 2.0 / (self.m - 1)
            ratio = (dist[:, :, None] / dist[:, None, :]) ** exp     # [n, c, c]
            U     = 1.0 / ratio.sum(axis=2)                          # [n, c]

            if np.max(np.abs(U - U_prev)) < self.tol:
                break

        self.u_ = U
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Pertinência [n_samples, c] para novos dados."""
        dist  = np.linalg.norm(X[:, None, :] - self.centers_[None, :, :], axis=2)
        dist  = np.maximum(dist, 1e-10)
        exp   = 2.0 / (self.m - 1)
        ratio = (dist[:, :, None] / dist[:, None, :]) ** exp
        return 1.0 / ratio.sum(axis=2)

    def cluster_variances(self, X_input: np.ndarray) -> np.ndarray:
        """
        Desvio-padrão ponderado de cada feature de entrada em cada cluster.
        X_input : [n, n_input_features] — sem a coluna de saída.
        Retorna  : [n_input_features, c]
        """
        n_feats = X_input.shape[1]
        Um      = self.u_ ** self.m                           # [n, c]
        in_ctr  = self.centers_[:, :n_feats]                 # [c, n_feats]
        variances = np.zeros((n_feats, self.c))
        for fi in range(n_feats):
            for k in range(self.c):
                w    = Um[:, k]
                diff = X_input[:, fi] - in_ctr[k, fi]
                variances[fi, k] = np.sqrt((w * diff ** 2).sum() / (w.sum() + 1e-10))
        return np.maximum(variances, 1e-6)
