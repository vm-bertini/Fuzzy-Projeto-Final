import torch
import torch.nn as nn

class DefuzzyLayer(nn.Module):
    def __init__(self, num_rules, output_dim):
        super().__init__()
        self.consequence = nn.Linear(num_rules, output_dim)

    def forward(self, firing_strengths: torch.Tensor):
        assert firing_strengths.dim() == 2, f"Esperado [batch, num_rules], recebido {firing_strengths.shape}"
        assert firing_strengths.shape[1] == self.consequence.in_features

        normalized_strengths = self._normalize_firing_strengths(firing_strengths)  # [batch, num_rules]
        return self.consequence(normalized_strengths)  # [batch, output_dim]

    def _normalize_firing_strengths(self, firing_strengths: torch.Tensor):
        sum_strengths = firing_strengths.sum(dim=1, keepdim=True) + 1e-6  # Evita divisão por zero
        return firing_strengths / sum_strengths
