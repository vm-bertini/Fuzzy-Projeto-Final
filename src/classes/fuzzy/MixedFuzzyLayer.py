import torch
import torch.nn as nn
from typing import List, Union


class MixedFuzzyLayer(nn.Module):
    """
    Camada de fuzzificação mista:
    - Features numéricas ('gaussian'): MFs Gaussianas treináveis [n_gaussian, num_mfs]
    - Features categóricas (int n_cats): one-hot suavizado — 0.95 na categoria correta,
      0.05/(n_cats-1) nas demais. Sem parâmetros aprendíveis.

    Saída: [batch, n_features, max_mfs]
    max_mfs = max(num_mfs, max_n_cats) — garante que gather é válido para todas as features.

    O loop no forward itera sobre features (constante ≤ 20), não sobre o batch.
    """

    _EPS = 0.05   # suavização do one-hot categórico

    def __init__(self, feature_types: List[Union[str, int]], num_mfs: int):
        super().__init__()
        self.feature_types = feature_types
        self.num_mfs       = num_mfs

        self._gauss_idx = [fi for fi, t in enumerate(feature_types) if t == 'gaussian']
        self._cat_info  = [(fi, int(t)) for fi, t in enumerate(feature_types) if t != 'gaussian']

        max_cats    = max((n for _, n in self._cat_info), default=0)
        self.max_mfs = max(num_mfs, max_cats)

        n_gauss = len(self._gauss_idx)
        init_c  = torch.linspace(-1.0, 1.0, num_mfs)
        self.centers   = nn.Parameter(init_c.unsqueeze(0).expand(n_gauss, -1).clone())
        self.variances = nn.Parameter(torch.ones(n_gauss, num_mfs))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        assert x.dim() == 2, f"Esperado [batch, n_features], recebido {x.shape}"
        batch  = x.shape[0]
        n_feat = len(self.feature_types)
        out    = torch.zeros(batch, n_feat, self.max_mfs, device=x.device)

        # Gaussian features — totalmente vetorizado
        if self._gauss_idx:
            x_g  = x[:, self._gauss_idx].unsqueeze(-1)           # [batch, n_gauss, 1]
            c    = self.centers.unsqueeze(0)                       # [1, n_gauss, num_mfs]
            var  = self.variances.clamp(min=1e-6).unsqueeze(0)   # [1, n_gauss, num_mfs]
            mf   = torch.exp(-0.5 * ((x_g - c) / var) ** 2)     # [batch, n_gauss, num_mfs]
            out[:, self._gauss_idx, :self.num_mfs] = mf

        # Categorical features — loop sobre features (não sobre batch)
        for fi, n_cats in self._cat_info:
            xi   = x[:, fi].long().clamp(0, n_cats - 1)           # [batch]
            fill = self._EPS / max(n_cats - 1, 1)
            base = torch.full((batch, n_cats), fill, device=x.device)
            base.scatter_(1, xi.unsqueeze(1), 1.0 - self._EPS)
            out[:, fi, :n_cats] = base

        return out   # [batch, n_features, max_mfs]
