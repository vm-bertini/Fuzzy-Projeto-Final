"""
Heart Failure — Classificação de Risco Cardíaco

Fluxo:
  Passo 0  K-Means      → pool de regras + visualização da partição do espaço
  Passo 1  ANFIS        → treina end-to-end sobre o pool gerado pelo K-Means
  Passo 2  MLP          → baseline caixa-preta
  Passo 3  Gráficos     → mfs_kmeans.png, mfs_anfis.png, rule_comparison.png,
                          risk_comparison.png, confusion_matrix.png
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import numpy as np
import torch
from datetime import datetime
from sklearn.cluster import KMeans

import config
from data.loader import load_dataset
from models.MLP import MLPModel
from models.ANFIS import ANFISModel
from evaluation.metrics import evaluate
from experiments.auxiliary_functions.aux_functions import (
    result_processing, save_rules, plot_mf_anfis, plot_mf_kmeans,
    plot_risk_comparison, plot_rule_heatmap, plot_confusion_matrices,
)


# ---------------------------------------------------------------------------
# Rótulos linguísticos
# ---------------------------------------------------------------------------

_MF_LABELS = ['baixo', 'baixo_medio', 'medio', 'medio_alto', 'alto']

_OUT_CENTERS = np.array([1/6, 2/6, 3/6, 4/6, 5/6])
_OUT_HW      = 1/6

_HEART_MF_LABELS = {
    'Age':         ['jovem',      'meia_idade',  'idoso'],
    'RestingBP':   ['otimo',      'normal',      'elevado'],
    'Cholesterol': ['desejavel',  'limitrofe',   'alto'],
    'MaxHR':       ['baixa',      'moderada',    'alta'],
    'Oldpeak':     ['normal',     'leve',        'elevado'],
}


def _label_output(risk: float) -> str:
    memberships = np.maximum(0.0, 1.0 - np.abs(risk - _OUT_CENTERS) / _OUT_HW)
    return _MF_LABELS[int(np.argmax(memberships))]


# ---------------------------------------------------------------------------
# Helpers compartilhados
# ---------------------------------------------------------------------------

def _rule_str(dominant, feature_names, feature_types, cat_mappings,
              consequence, n_mfs, feature_mf_labels=None) -> str:
    _default_mf = _MF_LABELS[:n_mfs] if n_mfs <= len(_MF_LABELS) else [f'MF{i}' for i in range(n_mfs)]
    parts = []
    for fi, fname in enumerate(feature_names):
        ftype = feature_types[fi]
        if ftype == 'gaussian':
            mf_lbl = (feature_mf_labels or {}).get(fname, _default_mf)
            label  = mf_lbl[int(dominant[fi])] if int(dominant[fi]) < len(mf_lbl) else f'MF{dominant[fi]}'
        else:
            mapping = cat_mappings.get(fname, {})
            label   = mapping.get(int(dominant[fi]), str(int(dominant[fi])))
        parts.append(f"{fname} e {label}")
    ante     = '  E  '.join(parts)
    risk_lbl = _label_output(float(consequence))
    return f"SE {ante}  ENTAO risco e {risk_lbl}"


def _dominant_from_kmeans(km_centers, peaks, feature_types, scaler, n_mfs):
    hw       = (peaks[:, -1] - peaks[:, 0]) / max(n_mfs - 1, 1)
    diff     = km_centers[:, :, None] - peaks[None, :, :]
    mu_map   = np.maximum(0.0, 1.0 - np.abs(diff) / (hw[None, :, None] + 1e-6))
    dominant = mu_map.argmax(axis=2)

    for fi, ftype in enumerate(feature_types):
        if ftype != 'gaussian':
            n_cats    = int(ftype)
            vals_orig = km_centers[:, fi] * scaler.scale_[fi] + scaler.mean_[fi]
            dominant[:, fi] = np.clip(np.round(vals_orig).astype(int), 0, n_cats - 1)

    return dominant


def _compute_rule_labels(combos_arr, feature_names, feature_types,
                          cat_mappings, n_mfs, feature_mf_labels=None):
    _default_mf = _MF_LABELS[:n_mfs] if n_mfs <= len(_MF_LABELS) else [f'MF{i}' for i in range(n_mfs)]
    result = []
    for ri in range(len(combos_arr)):
        row = []
        for fi, fname in enumerate(feature_names):
            ftype = feature_types[fi]
            dom   = int(combos_arr[ri, fi])
            if ftype == 'gaussian':
                mf_lbl = (feature_mf_labels or {}).get(fname, _default_mf)
                label  = mf_lbl[dom] if dom < len(mf_lbl) else f'MF{dom}'
                row.append((label, dom))
            else:
                mapping = cat_mappings.get(fname, {})
                row.append((mapping.get(dom, str(dom)), None))
        result.append(row)
    return result


# ---------------------------------------------------------------------------
# K-Means — pool de regras para o ANFIS
# ---------------------------------------------------------------------------

def _make_anfis_combos(X_np, feature_names, feature_types, cat_mappings, scaler,
                        n_mfs, feature_mf_labels=None):
    n_clusters = config.ANFIS_N_CLUSTERS
    pcts       = np.linspace(100 / (n_mfs + 1), 100 * n_mfs / (n_mfs + 1), n_mfs)
    peaks      = np.percentile(X_np, pcts, axis=0).T   # [n_features, n_mfs]

    km = KMeans(n_clusters=n_clusters, random_state=config.RANDOM_SEED, n_init=10)
    km.fit(X_np)
    km_centers = km.cluster_centers_.copy()

    dominant = _dominant_from_kmeans(km_centers, peaks, feature_types, scaler, n_mfs)

    seen = {}
    u_combos, u_centers = [], []
    for k in range(n_clusters):
        key = tuple(dominant[k])
        if key not in seen:
            seen[key] = True
            u_combos.append(list(dominant[k]))
            u_centers.append(km_centers[k])

    combos_arr = np.array(u_combos, dtype=int)
    km_unique  = np.array(u_centers, dtype=float)

    rule_strings = [
        _rule_str(combos_arr[ri], feature_names, feature_types, cat_mappings,
                  0.5, n_mfs, feature_mf_labels=feature_mf_labels)
        for ri in range(len(combos_arr))
    ]

    peaks_t = torch.tensor(peaks, dtype=torch.float32)
    return torch.tensor(combos_arr, dtype=torch.long), km_unique, combos_arr, rule_strings, peaks, km_centers


def _get_top_rule_idx_by_activation(anfis_net, X: torch.Tensor, top_k: int) -> list:
    anfis_net.eval()
    with torch.no_grad():
        mfs = anfis_net.fuzzy(X)
        w   = anfis_net.rule_layer(mfs)
    avg = w.mean(dim=0)
    return avg.argsort(descending=True)[:min(top_k, avg.numel())].tolist()


def _extract_anfis_rules(anfis_net, rule_strings: list, indices: list) -> list:
    weight = anfis_net.defuzz.consequence.weight.detach().cpu()
    bias   = anfis_net.defuzz.consequence.bias.detach().cpu()
    rules  = []
    for k in indices:
        ante = rule_strings[k].split('ENTAO')[0]
        prob = torch.sigmoid(weight[0, k] + bias[0]).item()
        rules.append(f"{ante}ENTAO risco e {_label_output(prob)}")
    return rules


def _print_anfis_rules(rules: list, n_rules_total: int) -> None:
    print(f"\n{'='*70}")
    print(f"  Top-{len(rules)} regras ANFIS  ({n_rules_total} no pool total)")
    print(f"{'='*70}")
    for i, r in enumerate(rules, 1):
        print(f"  Regra {i:>2}: {r}")
    print()


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def _run_pipeline(
    X_train, X_test, y_train, y_test,
    feature_names, task, scaler, feature_types, cat_mappings,
    result_dir,
    target_name='target',
    verbose=False,
    feature_mf_labels=None,
) -> dict:
    X_np       = X_train.numpy()
    n_mfs      = config.NUM_MFS

    os.makedirs(result_dir, exist_ok=True)

    # ---- Passo 0: K-Means — pool de regras + visualização -------------------
    print(f"\n{'#'*70}")
    print(f"  Passo 0: K-Means — {config.ANFIS_N_CLUSTERS} clusters  |  NUM_MFS={n_mfs}")
    print(f"{'#'*70}\n")

    t_combos, km_unique, combos_arr, rule_strings, peaks, km_centers = _make_anfis_combos(
        X_np, feature_names, feature_types, cat_mappings, scaler, n_mfs,
        feature_mf_labels=feature_mf_labels,
    )
    n_rules = len(combos_arr)
    N_TOP   = min(config.TOP_RULES, n_rules)
    print(f"  {n_rules} combos unicos no pool de regras.")

    plot_mf_kmeans(
        peaks, km_centers,
        feature_names, feature_types, X_np, result_dir,
        scaler=scaler, feature_mf_labels=feature_mf_labels,
    )

    # ---- Passo 1: ANFIS ------------------------------------------------------
    print(f"\n{'#'*70}")
    print(f"  Passo 1: ANFIS  (pool={n_rules} regras)")
    print(f"{'#'*70}")

    anfis = ANFISModel(
        feature_types = feature_types,
        num_mfs       = n_mfs,
        rule_combos   = t_combos,
        task          = task,
        lr            = config.LR_ANFIS,
        output_dim    = 1,
    )
    anfis.init_centers_from_fcm(km_unique)
    anfis.fit(X_train, y_train, epochs=config.EPOCHS_ANFIS,
              batch_size=config.BATCH_SIZE, verbose=verbose)
    anfis_result = evaluate(anfis, X_test, y_test, task)
    print(f"[ANFIS]  {anfis_result}")

    top_idx         = _get_top_rule_idx_by_activation(anfis.net, X_train, N_TOP)
    anfis_rules_top = _extract_anfis_rules(anfis.net, rule_strings, top_idx)
    _print_anfis_rules(anfis_rules_top, n_rules)

    plot_mf_anfis(anfis.net, feature_names, feature_types, X_np, result_dir,
                  task=task, scaler=scaler, feature_mf_labels=feature_mf_labels)

    anfis_weight = anfis.net.defuzz.consequence.weight.detach().cpu()
    anfis_bias   = anfis.net.defuzz.consequence.bias.detach().cpu()
    anfis_risks  = [torch.sigmoid(anfis_weight[0, k] + anfis_bias[0]).item() for k in top_idx]

    anfis_label_grid = _compute_rule_labels(
        combos_arr[top_idx], feature_names, feature_types, cat_mappings, n_mfs, feature_mf_labels,
    )

    save_rules(anfis_rules_top, result_dir)
    plot_rule_heatmap(
        anfis_label_grid, anfis_risks,
        feature_names, n_mfs, result_dir,
    )

    # ---- Passo 2: MLP --------------------------------------------------------
    print(f"{'#'*70}")
    print("  Passo 2: MLP")
    print(f"{'#'*70}")

    mlp = MLPModel(
        input_dim   = X_train.shape[1],
        hidden_dims = config.MLP_HIDDEN_DIMS,
        output_dim  = 1,
        task        = task,
        lr          = config.LR_MLP,
    )
    mlp.fit(X_train, y_train, epochs=config.EPOCHS_MLP,
            batch_size=config.BATCH_SIZE, verbose=verbose)
    mlp_result = evaluate(mlp, X_test, y_test, task)
    print(f"[MLP]  {mlp_result}")

    # ---- Passo 3: Comparação -------------------------------------------------
    preds_cls = {
        'ANFIS': anfis.predict(X_test).cpu().numpy().ravel(),
        'MLP':   mlp.predict(X_test).cpu().numpy().ravel(),
    }
    plot_risk_comparison(preds_cls, y_test.cpu().numpy().ravel(), result_dir=result_dir)
    plot_confusion_matrices(preds_cls, y_test.cpu().numpy().ravel(), result_dir=result_dir)

    return {'ANFIS': anfis_result, 'MLP': mlp_result}


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def run_heart(verbose: bool = False) -> None:
    curr_date  = datetime.now().strftime("%Y_%m_%d_%H_%M")
    result_dir = os.path.join(config.RESULT_DIR, curr_date)

    print(f"\n{'#'*70}")
    _tr = int(config.TRAIN_RATIO * 100)
    print(f"  HEART FAILURE — Classificacao de Risco Cardiaco")
    print(f"  Split: {_tr}/{100-_tr}  |  NUM_MFS={config.NUM_MFS}"
          f"  |  ANFIS pool={config.ANFIS_N_CLUSTERS}")
    print(f"{'#'*70}")

    X_train, X_test, y_train, y_test, feature_names, task, scaler, feature_types, cat_mappings = (
        load_dataset('heart')
    )

    numeric   = [f for f, t in zip(feature_names, feature_types) if t == 'gaussian']
    categoric = [f for f in feature_names if f not in numeric]
    print(f"  Features ({len(feature_names)}): {feature_names}")
    print(f"  Numericas (z-score):     {numeric}")
    print(f"  Categoricas (cod. orig): {categoric}\n")

    results = _run_pipeline(
        X_train, X_test, y_train, y_test,
        feature_names, task, scaler, feature_types, cat_mappings,
        result_dir      = result_dir,
        target_name     = 'HeartDisease',
        verbose         = verbose,
        feature_mf_labels = _HEART_MF_LABELS,
    )
    result_processing(results=results, file_add=result_dir, sheet='heart')
    print(f"\n  Resultados salvos em: {result_dir}")
