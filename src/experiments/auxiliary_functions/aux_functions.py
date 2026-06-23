import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Patch, Rectangle
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import confusion_matrix


# ---------------------------------------------------------------------------
# Gráfico de comparação entre modelos
# ---------------------------------------------------------------------------

def _graph_generation(results: dict, file_add: str, sheet: str = '') -> None:
    os.makedirs(file_add, exist_ok=True)
    try:
        models  = list(results.keys())
        colors  = ['#4C72B0', '#DD8452', '#55A868']
        first   = next(iter(results.values()))

        metric_keys = [k for k in ('accuracy', 'f1', 'auc') if k in first]
        ylim = (0, 1.18)

        fig, axes = plt.subplots(1, 3, figsize=(14, 5))
        fig.suptitle('Comparacao de Modelos', fontsize=13, fontweight='bold')

        x     = range(len(metric_keys))
        width = 0.25
        for mi, model in enumerate(models):
            vals = [results[model].get(k, 0) for k in metric_keys]
            bars = axes[0].bar(
                [xi + mi * width for xi in x], vals,
                width=width, label=model, color=colors[mi % len(colors)]
            )
            for bar, v in zip(bars, vals):
                axes[0].text(bar.get_x() + bar.get_width() / 2,
                             bar.get_height() * 1.02,
                             f'{v:.3f}', ha='center', va='bottom', fontsize=8)
        axes[0].set_xticks([xi + width for xi in x])
        axes[0].set_xticklabels([m.upper() for m in metric_keys])
        axes[0].set_ylim(*ylim)
        axes[0].set_ylabel('Valor')
        axes[0].set_title('Metricas de Classificacao')
        axes[0].legend(fontsize=8)

        times = [results[m].get('training_time_s', 0) for m in models]
        bars  = axes[1].bar(models, times, color=colors[:len(models)])
        axes[1].set_title('Tempo de Treino (s)')
        axes[1].set_ylabel('Segundos')
        max_t = max(times) if max(times) > 0 else 1
        for bar, v in zip(bars, times):
            axes[1].text(bar.get_x() + bar.get_width() / 2,
                         bar.get_height() + max_t * 0.02,
                         f'{v:.2f}s', ha='center', va='bottom', fontsize=9)

        params = [results[m].get('num_params', 0) for m in models]
        bars   = axes[2].bar(models, params, color=colors[:len(models)])
        axes[2].set_title('Parametros Treinaveis')
        axes[2].set_ylabel('No de Parametros')
        max_p = max(params) if max(params) > 0 else 1
        for bar, v in zip(bars, params):
            axes[2].text(bar.get_x() + bar.get_width() / 2,
                         bar.get_height() + max_p * 0.02,
                         str(v), ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        filename = f'{sheet}_comparacao.png' if sheet else 'comparacao.png'
        plt.savefig(os.path.join(file_add, filename), dpi=150, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"  [aviso] Falha ao gerar grafico de comparacao: {e}")


# ---------------------------------------------------------------------------
# Gráfico de comparação de risco — ANFIS vs MLP vs rótulo real
# ---------------------------------------------------------------------------

def plot_risk_comparison(
    preds: dict,
    y_true: np.ndarray,
    result_dir: str,
    title: str = 'Comparacao de Risco — Pacientes do Conjunto de Teste',
) -> None:
    os.makedirs(result_dir, exist_ok=True)
    try:
        colors_model = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']
        n = len(y_true)

        first_pred = next(iter(preds.values()))
        order      = np.argsort(first_pred)
        y_sorted   = y_true[order]

        fig, ax = plt.subplots(figsize=(min(18, max(10, n // 30)), 5))

        for i, label in enumerate(y_sorted):
            ax.axvspan(i - 0.5, i + 0.5,
                       color='#FFCCCC' if label == 1 else '#CCFFCC',
                       alpha=0.35, linewidth=0)

        xs = np.arange(n)
        for (name, pred), col in zip(preds.items(), colors_model):
            ax.plot(xs, pred[order], color=col, linewidth=1.2,
                    alpha=0.85, label=name, zorder=3)

        ax.axhline(0.5, color='gray', linewidth=1.2, linestyle='--',
                   alpha=0.7, label='limiar 0.5')

        legend_extra = [
            Patch(facecolor='#FFCCCC', alpha=0.7, label='Doenca cardiaca (real=1)'),
            Patch(facecolor='#CCFFCC', alpha=0.7, label='Sem doenca (real=0)'),
        ]
        handles, lbls = ax.get_legend_handles_labels()
        ax.legend(handles + legend_extra, lbls + [p.get_label() for p in legend_extra],
                  fontsize=8, loc='upper left', ncol=2)

        ax.set_xlim(-0.5, n - 0.5)
        ax.set_ylim(-0.05, 1.1)
        ax.set_xlabel('Paciente (ordenado por risco crescente)', fontsize=9)
        ax.set_ylabel('P(doenca cardiaca)', fontsize=9)
        ax.set_title(title, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, 'risk_comparison.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print('  [Risco] risk_comparison.png')
    except Exception as e:
        import traceback
        print(f'  [aviso] risk_comparison: {e}')
        traceback.print_exc()


# ---------------------------------------------------------------------------
# Heatmap de regras ANFIS
# ---------------------------------------------------------------------------

def plot_rule_heatmap(
    anfis_label_grid,  # list[list[(str, int|None)]]
    anfis_risks,       # list[float] in [0, 1]
    feature_names,     # list[str]
    n_mfs,             # int
    result_dir,        # str
) -> None:
    os.makedirs(result_dir, exist_ok=True)
    try:
        _MF_COLORS  = ['#90CAF9', '#FFF176', '#EF9A9A', '#CE93D8', '#A5D6A7']
        _CAT_COLOR  = '#CFD8DC'
        _HDR_ANFIS  = '#6A1B9A'
        _COL_HDR    = '#455A64'
        _MF_DEFAULT = ['baixo', 'medio', 'alto']

        risk_cmap = cm.get_cmap('RdYlGn_r')

        n_anfis = len(anfis_label_grid)
        n_feats = len(feature_names)
        n_cols  = n_feats + 1

        total_rows = 2 + n_anfis

        fig_w = max(16, n_cols * 1.55)
        fig_h = max(6,  total_rows * 0.52 + 1.2)
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        ax.set_xlim(0, n_cols)
        ax.set_ylim(total_rows, 0)
        ax.axis('off')

        def _cell(col, row, text, bg, fg='#212121', fs=6.5, bold=False):
            ax.add_patch(Rectangle([col, row], 1, 1, fc=bg, ec='white', lw=0.7, zorder=2))
            ax.text(col + 0.5, row + 0.5, str(text),
                    ha='center', va='center', fontsize=fs,
                    color=fg, fontweight='bold' if bold else 'normal',
                    zorder=3, clip_on=True)

        def _section_bar(row, title, color):
            ax.add_patch(Rectangle([0, row], n_cols, 1, fc=color, ec='none', zorder=1))
            ax.text(n_cols / 2, row + 0.5, title,
                    ha='center', va='center', fontsize=9,
                    color='white', fontweight='bold', zorder=3)

        def _rule_row(row_y, label_row, risk, row_label):
            for fi, (text, mf_idx) in enumerate(label_row):
                bg = (_MF_COLORS[mf_idx] if (mf_idx is not None and mf_idx < len(_MF_COLORS))
                      else _CAT_COLOR)
                _cell(fi, row_y, text, bg)
            rc = risk_cmap(float(risk))
            _cell(n_feats, row_y, f'{float(risk):.2f}', rc, fg='#111', fs=7)
            ax.text(-0.08, row_y + 0.5, row_label,
                    ha='right', va='center', fontsize=6, color='#555')

        for fi, fname in enumerate(feature_names):
            short = (fname[:9] + '.') if len(fname) > 10 else fname
            _cell(fi, 0, short, _COL_HDR, fg='white', fs=5.8, bold=True)
        _cell(n_feats, 0, 'Risco', _COL_HDR, fg='white', fs=6.5, bold=True)

        _section_bar(1, f'ANFIS — Top-{n_anfis} Regras Mais Ativadas  (forca de disparo media)', _HDR_ANFIS)
        for ri, (row_labels, risk) in enumerate(zip(anfis_label_grid, anfis_risks)):
            _rule_row(2 + ri, row_labels, risk, f'A{ri+1}')

        legend_handles = [
            Patch(fc=_MF_COLORS[mi],
                  label=f'MF{mi} ({_MF_DEFAULT[mi] if mi < len(_MF_DEFAULT) else mi})')
            for mi in range(min(n_mfs, len(_MF_COLORS)))
        ]
        legend_handles.append(Patch(fc=_CAT_COLOR, label='Categorico'))
        ax.legend(handles=legend_handles, fontsize=7, loc='lower right',
                  title='Funcao de pertinencia', title_fontsize=7, framealpha=0.9)

        ax.set_title('Regras ANFIS — Top-N por Forca de Disparo Media',
                     fontsize=12, fontweight='bold', pad=12)

        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, 'rule_comparison.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print('  [Regras] rule_comparison.png')
    except Exception as e:
        import traceback
        print(f'  [aviso] rule_comparison: {e}')
        traceback.print_exc()


# ---------------------------------------------------------------------------
# Matriz de confusão — ANFIS e MLP lado a lado
# ---------------------------------------------------------------------------

def plot_confusion_matrices(
    preds: dict,        # {'ModelName': np.ndarray [N] probabilities}
    y_true: np.ndarray, # [N] binary labels
    result_dir: str,
    threshold: float = 0.5,
) -> None:
    os.makedirs(result_dir, exist_ok=True)
    try:
        models  = list(preds.keys())
        n       = len(models)
        labels  = ['Sem doenca\n(0)', 'Doenca\ncardiaca (1)']
        colors  = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']

        fig, axes = plt.subplots(1, n, figsize=(5 * n, 4.5))
        if n == 1:
            axes = [axes]
        fig.suptitle('Matriz de Confusao', fontsize=13, fontweight='bold')

        for ax, (name, prob), color in zip(axes, preds.items(), colors):
            y_pred = (prob >= threshold).astype(int)
            cm_arr = confusion_matrix(y_true.astype(int), y_pred)

            im = ax.imshow(cm_arr, interpolation='nearest', cmap='Blues')
            ax.set_title(name, fontsize=12, fontweight='bold', color=color)
            ax.set_xticks([0, 1])
            ax.set_yticks([0, 1])
            ax.set_xticklabels(labels, fontsize=9)
            ax.set_yticklabels(labels, fontsize=9)
            ax.set_xlabel('Previsto', fontsize=10)
            ax.set_ylabel('Real', fontsize=10)

            thresh = cm_arr.max() / 2.0
            for i in range(2):
                for j in range(2):
                    ax.text(j, i, str(cm_arr[i, j]),
                            ha='center', va='center', fontsize=16, fontweight='bold',
                            color='white' if cm_arr[i, j] > thresh else '#333333')

            total = cm_arr.sum()
            acc   = cm_arr.trace() / total
            ax.set_xlabel(f'Previsto\n(acuracia: {acc:.1%})', fontsize=9)

        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, 'confusion_matrix.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print('  [CM] confusion_matrix.png')
    except Exception as e:
        import traceback
        print(f'  [aviso] confusion_matrix: {e}')
        traceback.print_exc()


# ---------------------------------------------------------------------------
# Salvar regras em arquivo de texto
# ---------------------------------------------------------------------------

def save_rules(anfis_rules: list, file_add: str) -> None:
    os.makedirs(file_add, exist_ok=True)
    path = os.path.join(file_add, 'regras.txt')
    sep  = '=' * 70

    lines = [
        sep,
        f'  TOP-{len(anfis_rules)} REGRAS ANFIS  (por forca de disparo media)',
        sep,
    ]
    for i, r in enumerate(anfis_rules, 1):
        lines.append(f'  Regra {i:>2}: {r}')

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('  [regras] regras.txt')


# ---------------------------------------------------------------------------
# Excel
# ---------------------------------------------------------------------------

def _xlsx_results(results: dict, file_add: str, sheet: str) -> None:
    os.makedirs(file_add, exist_ok=True)
    filepath   = os.path.join(file_add, 'results.xlsx')
    pd_results = (
        pd.DataFrame(results)
        .T.reset_index()
        .rename(columns={'index': 'model'})
    )
    mode  = 'a' if os.path.exists(filepath) else 'w'
    extra = {'if_sheet_exists': 'replace'} if mode == 'a' else {}
    with pd.ExcelWriter(filepath, engine='openpyxl', mode=mode, **extra) as writer:
        pd_results.to_excel(writer, sheet_name=sheet, index=False)


def result_processing(results: dict, file_add: str, sheet: str) -> None:
    _xlsx_results(results=results, file_add=file_add, sheet=sheet)
    _graph_generation(results=results, file_add=file_add, sheet=sheet)


# ---------------------------------------------------------------------------
# Visualização das funções de pertinência — ANFIS
# ---------------------------------------------------------------------------

_MF_PALETTE  = [
    '#2196F3', '#4CAF50', '#FF9800', '#E91E63', '#9C27B0',
    '#00BCD4', '#FF5722', '#8BC34A', '#FFC107', '#3F51B5',
]
_MF_LABELS_5 = ['baixo', 'baixo_medio', 'medio', 'medio_alto', 'alto']
_OUT_CTRS    = np.array([1/6, 2/6, 3/6, 4/6, 5/6])
_OUT_HW      = 1/6


def _plot_output_mfs(ax: plt.Axes) -> None:
    xs = np.linspace(0, 1, 400)
    for mi, (c, lbl) in enumerate(zip(_OUT_CTRS, _MF_LABELS_5)):
        col  = _MF_PALETTE[mi % len(_MF_PALETTE)]
        vals = np.maximum(0.0, 1.0 - np.abs(xs - c) / _OUT_HW)
        ax.plot(xs, vals, color=col, linewidth=2, label=lbl)
        ax.fill_between(xs, vals, alpha=0.08, color=col)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.05, 1.18)
    ax.set_xlabel('Risco', fontsize=8)
    ax.set_ylabel('u', fontsize=8)
    ax.set_title('Output — risco', fontweight='bold', fontsize=9)
    ax.legend(fontsize=6, loc='upper center', ncol=3)
    ax.grid(True, alpha=0.3)


def _hist_bg(ax: plt.Axes, col_data: np.ndarray) -> None:
    ax2 = ax.twinx()
    ax2.hist(col_data, bins=25, alpha=0.13, color='#607D8B', density=True)
    ax2.set_yticks([])


def plot_mf_anfis(
    anfis_net,
    feature_names: list,
    feature_types: list,
    X_train_np: np.ndarray,
    file_add: str,
    task: str = 'classification',
    scaler=None,
    feature_mf_labels: dict = None,
) -> None:
    os.makedirs(file_add, exist_ok=True)
    try:
        # MixedFuzzyLayer: centers/variances only cover Gaussian features [n_gaussian, n_mfs]
        g_ctr = anfis_net.fuzzy.centers.detach().cpu().numpy()
        g_var = anfis_net.fuzzy.variances.detach().cpu().numpy().clip(min=1e-6)
        n_mfs = g_ctr.shape[1]
        _default_labels = (
            ['baixo', 'medio', 'alto'] if n_mfs == 3
            else _MF_LABELS_5[:n_mfs]  if n_mfs <= 5
            else [f'MF{i}' for i in range(n_mfs)]
        )

        # Only Gaussian features get a MF plot; categoricals have no learnable MFs
        gauss_feat = [
            (fi, fname)
            for fi, (fname, ft) in enumerate(zip(feature_names, feature_types))
            if ft == 'gaussian'
        ]
        n_gauss = len(gauss_feat)

        show_output = (task == 'classification')
        n_plots = n_gauss + (1 if show_output else 0)
        n_cols  = min(4, n_plots)
        n_rows  = math.ceil(n_plots / n_cols)

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(5.0 * n_cols, 4.2 * n_rows))
        fig.suptitle('ANFIS — Funcoes de Pertinencia Gaussianas (pos-treinamento)',
                     fontsize=13, fontweight='bold')
        axf = np.array(axes).flatten() if n_rows * n_cols > 1 else [axes]

        # gi = index into g_ctr/g_var (Gaussian feature index)
        # fi = full feature index (for scaler and X_train_np columns)
        for gi, (fi, fname) in enumerate(gauss_feat):
            ax       = axf[gi]
            col_data = X_train_np[:, fi] if X_train_np is not None else None
            c        = g_ctr[gi]
            var      = g_var[gi]
            labels   = (feature_mf_labels or {}).get(fname, _default_labels)

            if scaler is not None and fi < len(scaler.mean_):
                m_fi     = float(scaler.mean_[fi])
                s_fi     = float(scaler.scale_[fi])
                c_plot   = c * s_fi + m_fi
                var_plot = var * s_fi
                col_plot = col_data * s_fi + m_fi if col_data is not None else None
                xlabel   = 'valor original'
            else:
                c_plot = c; var_plot = var
                col_plot = col_data
                xlabel = 'z-score'

            lo_d = float(col_plot.min()) if col_plot is not None else float(c_plot.min()) - 3 * float(var_plot.max())
            hi_d = float(col_plot.max()) if col_plot is not None else float(c_plot.max()) + 3 * float(var_plot.max())
            lo_g = float((c_plot - 3.0 * var_plot).min())
            hi_g = float((c_plot + 3.0 * var_plot).max())
            lo   = min(lo_d, lo_g)
            hi   = max(hi_d, hi_g)
            mg   = (hi - lo) * 0.06
            xs   = np.linspace(lo - mg, hi + mg, 500)

            if col_plot is not None:
                _hist_bg(ax, col_plot)

            for mi in range(n_mfs):
                col  = _MF_PALETTE[mi % len(_MF_PALETTE)]
                vals = np.exp(-0.5 * ((xs - c_plot[mi]) / var_plot[mi]) ** 2)
                lbl  = labels[mi] if mi < len(labels) else f'MF{mi}'
                ax.plot(xs, vals, color=col, linewidth=2, label=lbl)
                ax.fill_between(xs, vals, alpha=0.07, color=col)
                ax.axvline(c_plot[mi], color=col, linewidth=0.7, linestyle=':', alpha=0.5)

            ax.set_xlim(xs[0], xs[-1])
            ax.set_ylim(-0.05, 1.18)
            ax.set_xlabel(xlabel, fontsize=8)
            ax.set_ylabel('u(x)', fontsize=8)
            ax.set_title(fname, fontweight='bold', fontsize=9)
            ax.legend(fontsize=6, loc='upper right', ncol=2)
            ax.grid(True, alpha=0.3)

        if show_output:
            _plot_output_mfs(axf[n_gauss])

        for ax in axf[n_plots:]:
            ax.set_visible(False)

        plt.tight_layout()
        plt.savefig(os.path.join(file_add, 'mfs_anfis.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print('  [MFs] mfs_anfis.png')
    except Exception as e:
        import traceback
        print(f'  [aviso] mfs_anfis: {e}')
        traceback.print_exc()


# ---------------------------------------------------------------------------
# Visualização das funções de pertinência — FCM (triangulares)
# ---------------------------------------------------------------------------

def plot_mf_kmeans(
    peaks_np: np.ndarray,
    km_centers: np.ndarray,
    feature_names: list,
    feature_types: list,
    X_train_np: np.ndarray,
    file_add: str,
    scaler=None,
    feature_mf_labels: dict = None,
) -> None:
    """
    Plota as MFs triangulares usadas pelo FCM para mapear centros K-Means a índices
    de MF dominante. Cada MF cobre a região [peak_anterior, peak_próximo] com
    cobertura total (hw igual para todas).

    peaks_np   : [n_features, n_mfs] — posições dos picos em z-score
    km_centers : [n_clusters, n_features] — centros K-Means em z-score
    """
    os.makedirs(file_add, exist_ok=True)
    try:
        n_mfs = peaks_np.shape[1]
        _default_labels = (
            ['baixo', 'medio', 'alto'] if n_mfs == 3
            else _MF_LABELS_5[:n_mfs]  if n_mfs <= 5
            else [f'MF{i}' for i in range(n_mfs)]
        )

        gauss_feat = [
            (fi, fname)
            for fi, (fname, ft) in enumerate(zip(feature_names, feature_types))
            if ft == 'gaussian'
        ]
        n_gauss = len(gauss_feat)
        if n_gauss == 0:
            return

        n_cols = min(4, n_gauss)
        n_rows = math.ceil(n_gauss / n_cols)

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(5.0 * n_cols, 4.2 * n_rows))
        fig.suptitle('K-Means — Particao do Espaco de Entrada (pre-ANFIS)',
                     fontsize=13, fontweight='bold')
        axf = np.array(axes).flatten() if n_rows * n_cols > 1 else [axes]

        for gi, (fi, fname) in enumerate(gauss_feat):
            ax     = axf[gi]
            labels = (feature_mf_labels or {}).get(fname, _default_labels)
            peaks  = peaks_np[fi]   # [n_mfs] z-score peak positions
            hw     = (peaks[-1] - peaks[0]) / max(n_mfs - 1, 1)

            col_data    = X_train_np[:, fi] if X_train_np is not None else None
            clust_vals  = km_centers[:, fi]  # [n_clusters] z-score

            if scaler is not None and fi < len(scaler.mean_):
                s_fi        = float(scaler.scale_[fi])
                m_fi        = float(scaler.mean_[fi])
                peaks_plot  = peaks * s_fi + m_fi
                hw_plot     = hw * s_fi
                col_plot    = col_data * s_fi + m_fi if col_data is not None else None
                clust_plot  = clust_vals * s_fi + m_fi
                xlabel      = 'valor original'
            else:
                peaks_plot = peaks; hw_plot = hw
                col_plot   = col_data; clust_plot = clust_vals
                xlabel     = 'z-score'

            lo = float(peaks_plot[0])  - 1.5 * hw_plot
            hi = float(peaks_plot[-1]) + 1.5 * hw_plot
            if col_plot is not None:
                lo = min(lo, float(col_plot.min()))
                hi = max(hi, float(col_plot.max()))
            xs = np.linspace(lo, hi, 500)

            if col_plot is not None:
                _hist_bg(ax, col_plot)

            for mi in range(n_mfs):
                col  = _MF_PALETTE[mi % len(_MF_PALETTE)]
                vals = np.maximum(0.0, 1.0 - np.abs(xs - peaks_plot[mi]) / (hw_plot + 1e-9))
                lbl  = labels[mi] if mi < len(labels) else f'MF{mi}'
                ax.plot(xs, vals, color=col, linewidth=2, label=lbl)
                ax.fill_between(xs, vals, alpha=0.10, color=col)
                ax.axvline(peaks_plot[mi], color=col, linewidth=0.8, linestyle='--', alpha=0.6)

            # K-Means cluster centers for this feature as a rug plot
            for cv in clust_plot:
                ax.axvline(float(cv), color='#37474F', linewidth=0.6, alpha=0.35, ymin=0, ymax=0.07)

            ax.set_xlim(xs[0], xs[-1])
            ax.set_ylim(-0.05, 1.18)
            ax.set_xlabel(xlabel, fontsize=8)
            ax.set_ylabel('u(x)', fontsize=8)
            ax.set_title(fname, fontweight='bold', fontsize=9)
            ax.legend(fontsize=6, loc='upper right', ncol=2)
            ax.grid(True, alpha=0.3)

        for ax in axf[n_gauss:]:
            ax.set_visible(False)

        plt.tight_layout()
        plt.savefig(os.path.join(file_add, 'mfs_kmeans.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print('  [MFs] mfs_kmeans.png')
    except Exception as e:
        import traceback
        print(f'  [aviso] mfs_fcm: {e}')
        traceback.print_exc()
