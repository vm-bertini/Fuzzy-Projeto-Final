import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from typing import List, Union

from classes.models.ANFIS import ANFIS


class ANFISModel:
    """
    Wrapper de treino/inferência para ANFIS com regras FCM compartilhadas.

    feature_types : list — 'gaussian' para numérica, int(n_cats) para categórica.
    rule_combos   : mesmas regras derivadas do FCM/K-Means.
    """

    def __init__(
        self,
        feature_types: List[Union[str, int]],
        num_mfs: int,
        rule_combos: torch.Tensor,
        task: str = 'classification',
        lr: float = 1e-3,
        output_dim: int = 1,
        device: str = 'cpu',
    ):
        self.task          = task
        self.device        = torch.device(device)
        self.net           = ANFIS(feature_types, num_mfs, rule_combos, output_dim).to(self.device)
        self.optimizer     = optim.Adam(self.net.parameters(), lr=lr)
        self.criterion     = nn.BCEWithLogitsLoss() if task == 'classification' else nn.MSELoss()
        self.training_time: float = 0.0

    def init_centers_from_fcm(self, km_centers: np.ndarray) -> None:
        """
        Inicializa os centros Gaussianos com base nos percentis dos centros K-Means.

        km_centers : [n_clusters, n_features] — centros K-Means em espaço z-score.
        """
        gauss_idx = self.net.fuzzy._gauss_idx   # full feature indices of Gaussian features
        num_mfs   = self.net.fuzzy.num_mfs
        pcts      = np.linspace(100 / (num_mfs + 1), 100 * num_mfs / (num_mfs + 1), num_mfs)

        with torch.no_grad():
            for gi, fi in enumerate(gauss_idx):
                vals  = km_centers[:, fi]
                new_c = np.percentile(vals, pcts).astype(np.float32)
                self.net.fuzzy.centers.data[gi] = torch.from_numpy(new_c)

    def fit(
        self,
        X: torch.Tensor,
        y: torch.Tensor,
        epochs: int = 100,
        batch_size: int = 32,
        verbose: bool = True,
    ) -> list:
        self.net.train()
        X, y   = X.to(self.device), y.to(self.device)
        loader = DataLoader(TensorDataset(X, y), batch_size=batch_size, shuffle=True)
        history, start = [], time.time()

        n_mfs = self.net.fuzzy.num_mfs

        for epoch in range(1, epochs + 1):
            epoch_loss = 0.0
            for xb, yb in loader:
                self.optimizer.zero_grad()
                task_loss = self.criterion(self.net(xb), yb)

                # Separation penalty: push MF centers apart by at least σ_i + σ_j
                centers   = self.net.fuzzy.centers                      # [n_gaussian, n_mfs]
                variances = self.net.fuzzy.variances.clamp(min=1e-6)   # [n_gaussian, n_mfs]
                sep = torch.tensor(0.0, device=self.device)
                for i in range(n_mfs):
                    for j in range(i + 1, n_mfs):
                        dist    = (centers[:, i] - centers[:, j]).abs()
                        min_sep = variances[:, i] + variances[:, j]
                        sep     = sep + torch.relu(min_sep - dist).mean()
                loss = task_loss + 0.1 * sep

                loss.backward()
                self.optimizer.step()
                epoch_loss += task_loss.item()  # report task loss only
            avg = epoch_loss / len(loader)
            history.append(avg)
            if verbose and epoch % 10 == 0:
                print(f"[ANFIS] Época {epoch}/{epochs}  loss={avg:.6f}")

        self.training_time = time.time() - start
        return history

    def predict(self, X: torch.Tensor) -> torch.Tensor:
        self.net.eval()
        X = X.to(self.device)
        with torch.no_grad():
            out = self.net(X)
            return torch.sigmoid(out) if self.task == 'classification' else out
