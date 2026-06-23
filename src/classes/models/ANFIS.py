import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

import torch
import torch.nn as nn
from typing import List, Union

from classes.fuzzy.MixedFuzzyLayer  import MixedFuzzyLayer
from classes.fuzzy.ClusterRuleLayer import ClusterRuleLayer
from classes.fuzzy.DefuzzyLayer     import DefuzzyLayer


class ANFIS(nn.Module):
    """
    ANFIS com fuzzificação mista e regras compartilhadas com FCM/K-Means.

    - Features numéricas: MFs Gaussianas treináveis (3 por feature)
    - Features categóricas: one-hot suavizado (sem parâmetros aprendíveis)
    - T-norm produto: diferenciável em todos os pontos

    feature_types : list — 'gaussian' para numérica, int(n_cats) para categórica
    num_mfs       : MFs Gaussianas por feature numérica
    rule_combos   : [n_rules, n_features] — índice da MF por feature por regra

    Fluxo:
        [batch, n_features]
        → MixedFuzzyLayer  → [batch, n_features, max_mfs]
        → ClusterRuleLayer → [batch, n_rules]
        → DefuzzyLayer     → [batch, output_dim]
    """

    def __init__(
        self,
        feature_types: List[Union[str, int]],
        num_mfs: int,
        rule_combos: torch.Tensor,
        output_dim: int,
    ):
        super().__init__()
        self.fuzzy      = MixedFuzzyLayer(feature_types, num_mfs)
        self.rule_layer = ClusterRuleLayer(rule_combos)
        self.defuzz     = DefuzzyLayer(rule_combos.shape[0], output_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        assert x.dim() == 2, f"Esperado [batch, n_features], recebido {x.shape}"
        mfs = self.fuzzy(x)        # [batch, n_features, max_mfs]
        w   = self.rule_layer(mfs) # [batch, n_rules]
        return self.defuzz(w)      # [batch, output_dim]
