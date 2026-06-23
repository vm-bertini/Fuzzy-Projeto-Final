import torch
import torch.nn as nn


class GaussianFuzzyLayer(nn.Module):
    """
    Funções de pertinência Gaussianas treináveis para features numéricas.

    Saída compatível com ClusterRuleLayer (tensor 3-D, não lista).

    Entrada : [batch, num_inputs]
    Saída   : [batch, num_inputs, num_mfs]
    """

    def __init__(self, num_inputs: int, num_mfs: int):
        super().__init__()
        init_c = torch.linspace(-1.0, 1.0, num_mfs)
        self.centers   = nn.Parameter(init_c.unsqueeze(0).expand(num_inputs, -1).clone())
        self.variances = nn.Parameter(torch.ones(num_inputs, num_mfs))
        self.num_mfs   = num_mfs

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        assert x.dim() == 2, f"Esperado [batch, num_inputs], recebido {x.shape}"
        x_exp = x.unsqueeze(-1)                                  # [batch, num_inputs, 1]
        c     = self.centers.unsqueeze(0)                        # [1, num_inputs, num_mfs]
        var   = self.variances.clamp(min=1e-6).unsqueeze(0)     # [1, num_inputs, num_mfs]
        return torch.exp(-0.5 * ((x_exp - c) / var) ** 2)      # [batch, num_inputs, num_mfs]
