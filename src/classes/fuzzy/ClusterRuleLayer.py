import torch
import torch.nn as nn


class ClusterRuleLayer(nn.Module):
    """
    Dispara k regras definidas por combinações de MF selecionadas (K-Means).

    rule_combos : [n_rules, n_features] — índice da MF dominante por feature por regra.

    Para a regra k:  fire_k(x) = ∏ᵢ μ_{combos[k,i]}(xᵢ)

    O gather vetorizado evita loops Python na inferência.

    Entrada : [batch, n_features, n_mfs]  ← TriangularFuzzyLayer
    Saída   : [batch, n_rules]
    """

    def __init__(self, rule_combos: torch.Tensor):
        super().__init__()
        self.register_buffer('rule_combos', rule_combos)  # [n_rules, n_features]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        assert x.dim() == 3, f"Esperado [batch, n_features, n_mfs], recebido {x.shape}"
        batch   = x.shape[0]
        n_rules = self.rule_combos.shape[0]

        # [batch, n_features, n_mfs] → [batch, n_rules, n_features, n_mfs]
        x_exp = x.unsqueeze(1).expand(-1, n_rules, -1, -1)

        # [n_rules, n_features] → [batch, n_rules, n_features, 1]
        idx = (self.rule_combos
               .unsqueeze(0).unsqueeze(-1)
               .expand(batch, -1, -1, 1))

        # Seleciona μ_{combo[k,i]}(x_i) para cada (b, k, i) → [batch, n_rules, n_features]
        selected = x_exp.gather(3, idx).squeeze(-1)

        # T-norm produto: diferenciável em todos os pontos (min tem gradiente zero q.s.)
        w = selected.prod(dim=2)                               # [batch, n_rules]
        return w / (w.sum(dim=1, keepdim=True) + 1e-6)        # [batch, n_rules], soma = 1
