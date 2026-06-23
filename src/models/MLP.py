import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from typing import List

from classes.models.MLP import MLP


class MLPModel:
    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int],
        output_dim: int = 1,
        dropout: float = 0.0,
        task: str = 'regression',
        lr: float = 1e-3,
        device: str = 'cpu',
    ):
        self.task = task
        self.device = torch.device(device)
        self.net = MLP(input_dim, hidden_dims, output_dim, dropout).to(self.device)
        self.optimizer = optim.Adam(self.net.parameters(), lr=lr)
        self.criterion = nn.BCEWithLogitsLoss() if task == 'classification' else nn.MSELoss()
        self.training_time: float = 0.0

    def fit(
        self,
        X: torch.Tensor,
        y: torch.Tensor,
        epochs: int = 100,
        batch_size: int = 32,
        verbose: bool = True,
    ) -> List[float]:
        self.net.train()
        X, y = X.to(self.device), y.to(self.device)
        loader = DataLoader(TensorDataset(X, y), batch_size=batch_size, shuffle=True)
        history = []
        start = time.time()
        for epoch in range(1, epochs + 1):
            epoch_loss = 0.0
            for xb, yb in loader:
                self.optimizer.zero_grad()
                loss = self.criterion(self.net(xb), yb)
                loss.backward()
                self.optimizer.step()
                epoch_loss += loss.item()
            avg_loss = epoch_loss / len(loader)
            history.append(avg_loss)
            if verbose and epoch % 10 == 0:
                print(f"[MLP] Época {epoch}/{epochs}  loss={avg_loss:.6f}")
        self.training_time = time.time() - start
        return history

    def predict(self, X: torch.Tensor) -> torch.Tensor:
        self.net.eval()
        X = X.to(self.device)
        with torch.no_grad():
            out = self.net(X)
            return torch.sigmoid(out) if self.task == 'classification' else out
