# Documentação Técnica — Projeto ANFIS
## Sistemas Neuro-Fuzzy para Classificação de Risco Cardíaco

---

## Sumário

1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [Dataset](#2-dataset)
3. [Arquitetura ANFIS](#3-arquitetura-anfis)
4. [Camadas Fuzzy](#4-camadas-fuzzy)
5. [Pipeline de Geração de Regras](#5-pipeline-de-geração-de-regras)
6. [Modelo MLP (Baseline)](#6-modelo-mlp-baseline)
7. [Pré-processamento](#7-pré-processamento)
8. [Experimentos e Resultados](#8-experimentos-e-resultados)
9. [Visualizações Geradas](#9-visualizações-geradas)
10. [Configuração e Execução](#10-configuração-e-execução)
11. [Estrutura de Arquivos](#11-estrutura-de-arquivos)

---

## 1. Visão Geral do Projeto

Este projeto investiga o tradeoff entre **acurácia preditiva** e **interpretabilidade** em modelos de aprendizado de máquina para classificação de risco cardíaco. O objetivo é demonstrar que o ANFIS (Adaptive Neuro-Fuzzy Inference System) consegue aproximar o desempenho de uma rede neural MLP enquanto produz regras linguísticas auditáveis.

### Hipótese central

> Um sistema ANFIS com fuzzificação mista (Gaussiana para numéricas, one-hot suavizado para categóricas) e regras inicializadas por K-Means pode atingir AUC comparável ao MLP com uma fração dos parâmetros treináveis, mantendo interpretabilidade por meio de regras SE-ENTÃO.

### Comparação realizada

| Modelo | Tipo | Interpretável | Parâmetros | AUC |
|--------|------|:---:|---:|---:|
| ANFIS  | Neuro-Fuzzy (Takagi-Sugeno) | ✓ | 228 | 0,903 |
| MLP    | Rede Neural Densa | ✗ | 2.881 | 0,910 |

---

## 2. Dataset

**Heart Failure Prediction Dataset**

| Atributo | Valor |
|----------|-------|
| Amostras | 918 |
| Features | 11 (5 numéricas + 6 categóricas) |
| Variável alvo | `HeartDisease` (0 = saudável, 1 = doença) |
| Prevalência positiva | ~55% |
| Split | 80% treino / 20% teste |

### Features

| Feature | Tipo | Descrição |
|---------|------|-----------|
| Age | Numérica | Idade em anos |
| RestingBP | Numérica | Pressão arterial em repouso (mmHg) |
| Cholesterol | Numérica | Colesterol sérico (mg/dl) |
| MaxHR | Numérica | Frequência cardíaca máxima |
| Oldpeak | Numérica | Depressão do segmento ST |
| Sex | Categórica | M / F |
| ChestPainType | Categórica | ATA / NAP / ASY / TA |
| FastingBS | Categórica | Glicemia em jejum > 120 mg/dl (0/1) |
| RestingECG | Categórica | Normal / ST / LVH |
| ExerciseAngina | Categórica | Y / N |
| ST_Slope | Categórica | Up / Flat / Down |

### Pré-processamento

- `Cholesterol` e `RestingBP`: valores 0 substituídos pela mediana das entradas não-nulas
- Features categóricas codificadas como inteiros (pd.Categorical.codes)
- **PartialScaler**: z-score aplicado **somente** às features numéricas; categóricas mantêm códigos inteiros originais

---

## 3. Arquitetura ANFIS

O ANFIS implementado segue o paradigma Takagi-Sugeno de ordem zero com fuzzificação mista para lidar com features numéricas e categóricas no mesmo pipeline.

### Fluxo de dados

```
[batch, n_features]
    ↓ MixedFuzzyLayer
[batch, n_features, max_mfs]
    ↓ ClusterRuleLayer
[batch, n_rules]
    ↓ DefuzzyLayer (nn.Linear)
[batch, 1]
    ↓ sigmoid (na predição)
P(HeartDisease)
```

### Função de perda

```
loss = BCEWithLogitsLoss(pred, y) + 0.1 × penalidade_separação
```

A penalidade de separação empurra centros de MFs adjacentes para que
a distância entre eles seja pelo menos `σ_i + σ_j`:

```
sep = Σ_{i<j} relu(σ_i + σ_j − |c_i − c_j|).mean()
```

---

## 4. Camadas Fuzzy

### 4.1 MixedFuzzyLayer

Fuzzificação que trata features numéricas e categóricas de forma diferente.

**Features numéricas** — MFs Gaussianas treináveis:

```
μ(x) = exp(−0.5 × ((x − center) / variance)²)
```

- Parâmetros: `centers [n_gaussian, num_mfs]`, `variances [n_gaussian, num_mfs]`
- `variances` clampeadas em `min=1e-6`
- Inicialização: `centers ~ N(0,1)`, `variances = |N(0,1)| + 0.1`

**Features categóricas** — one-hot suavizado (sem parâmetros):

```
out[categoria_correta] = 0.95
out[demais]            = 0.05 / (n_cats − 1)
```

Saída: `[batch, n_features, max_mfs]`, onde `max_mfs = max(num_mfs, max_n_cats)`

### 4.2 ClusterRuleLayer

Calcula a força de disparo de cada regra via T-norma produto.

```
w_k = ∏_i μ_{i, combo[k,i]}(x_i)
```

- Sem parâmetros treináveis
- `rule_idx [n_rules, n_features]` armazenado como `register_buffer` (move para GPU automaticamente)
- Implementação vetorizada com `gather(dim=3)`

### 4.3 DefuzzyLayer

Defuzzificação Takagi-Sugeno normalizada:

```
w_norm = w / (Σw + 1e-6)
output = nn.Linear(n_rules → 1)(w_norm)
```

O peso `c_k` de cada regra no `nn.Linear` é o consequente aprendido: o valor crisp que aquela regra "vota" para a saída.

---

## 5. Pipeline de Geração de Regras

### Visão geral

O conjunto de regras antecedentes do ANFIS é gerado de forma não supervisionada antes do treinamento, garantindo que as regras cubram regiões densas do espaço de entrada.

### Passo a passo

**1. Picos de MF por percentil**

Para cada feature numérica, os picos das MFs triangulares são os percentis da distribuição de treino:

```python
pcts  = np.linspace(100/(n_mfs+1), 100*n_mfs/(n_mfs+1), n_mfs)
peaks = np.percentile(X_train, pcts, axis=0).T   # [n_features, n_mfs]
```

Para `NUM_MFS=3`: percentis 25, 50, 75.

**2. K-Means clustering**

```python
km = KMeans(n_clusters=ANFIS_N_CLUSTERS, random_state=SEED)
km.fit(X_train)
```

200 clusters identificam as regiões densas do espaço de entrada.

**3. Mapeamento de MF dominante**

Para cada centro de cluster, determina qual MF "vence" em cada feature:

- **Numérica**: `argmax μ_triangular(centro, pico_j)` para j ∈ {0..n_mfs}
- **Categórica**: `round(centro_j)` → código inteiro original

**4. Deduplicação**

Clusters com o mesmo vetor de MFs dominantes são colapsados em uma única regra.
Resultado típico: 200 clusters → ~80–120 regras únicas.

**5. Inicialização das MFs Gaussianas**

Os centros Gaussianos do ANFIS são inicializados nos percentis dos centros K-Means:

```python
vals  = km_centers[:, fi]
new_c = np.percentile(vals, pcts)   # [n_mfs]
```

---

## 6. Modelo MLP (Baseline)

Rede neural densa com:

- Arquitetura: `Input → [64, 32] → 1`
- Ativação oculta: ReLU
- Saída: logit → sigmoid na predição
- Loss: BCEWithLogitsLoss
- Otimizador: Adam (lr=1e-3)

```
2881 parâmetros treináveis:
  11×64 + 64 = 768 (camada 1)
  64×32 + 32 = 2080 (camada 2)
  32×1  + 1  = 33   (saída)
```

---

## 7. Pré-processamento

### PartialScaler

Extensão do `StandardScaler` da sklearn que escala **somente** features numéricas.

**Motivação**: se as features categóricas (códigos 0, 1, 2, 3) forem z-scored, o `.long()` cast na `MixedFuzzyLayer` produziria códigos errados (ex: z=-0.45 → int 0 em vez de 1).

```python
class PartialScaler:
    def fit_transform(self, X, numeric_idx):
        # z-score somente em numeric_idx
        # mean_[cat] = 0, scale_[cat] = 1  (identidade)

    def transform(self, X):
        # aplica fit às colunas numéricas, passa categóricas sem alteração
```

`mean_` e `scale_` têm shape `[n_features]` para todas as features, permitindo que `plot_mf_anfis` use `scaler.mean_[fi]` / `scaler.scale_[fi]` uniformemente.

---

## 8. Experimentos e Resultados

### Métricas (Heart Failure, split 80/20)

| Modelo | Parâmetros | Treino (s) | Acurácia | F1-Score | AUC-ROC |
|--------|---:|---:|---:|---:|---:|
| ANFIS  | 228 | 13,8 | 83,2% | 84,7% | **0,903** |
| MLP    | 2.881 | 4,6 | 83,7% | 85,0% | 0,910 |

### Top-5 regras ANFIS (por força de disparo média)

```
Regra 1: SE Age=idoso E ChestPainType=ASY E RestingBP=normal
         E MaxHR=baixa E ExerciseAngina=Y E Oldpeak=elevado
         E ST_Slope=Flat  →  ENTÃO risco=ALTO

Regra 2: SE Age=jovem E ChestPainType=ATA E MaxHR=alta
         E ExerciseAngina=N E Oldpeak=normal E ST_Slope=Up
         →  ENTÃO risco=BAIXO

Regra 3: SE Age=idoso E ChestPainType=ASY E Cholesterol=desejável
         E MaxHR=baixa E ExerciseAngina=Y E Oldpeak=elevado
         E ST_Slope=Flat  →  ENTÃO risco=ALTO
```

### Análise

- **Eficiência paramétrica**: ANFIS usa 13× menos parâmetros para AUC praticamente idêntico (Δ=0,007).
- **Interpretabilidade**: centros Gaussianos após treino revelam os limiares clínicos aprendidos; `ST_Slope=Flat`, `ExerciseAngina=Y` e `Oldpeak=elevado` emergem como os marcadores de alto risco mais recorrentes.
- **Tradeoff de velocidade**: ANFIS treina em 13,8 s vs 4,6 s do MLP — aceitável para uso offline.

---

## 9. Visualizações Geradas

Cada execução salva em `src/results/YYYY_MM_DD_HH_MM/`:

| Arquivo | Conteúdo |
|---------|----------|
| `mfs_anfis.png` | MFs Gaussianas por feature numérica (pós-treino) + MFs de saída |
| `mfs_kmeans.png` | MFs triangulares da partição K-Means (pré-ANFIS) + centros K-Means como rug |
| `rule_comparison.png` | Heatmap das top-N regras ANFIS por força de disparo média |
| `risk_comparison.png` | Probabilidade predita por paciente (ANFIS vs MLP) com rótulo real |
| `confusion_matrix.png` | Matrizes de confusão lado a lado (ANFIS e MLP) |
| `regras.txt` | Top-N regras em linguagem natural |
| `results.xlsx` | Tabela de métricas por modelo |
| `heart_comparacao.png` | Gráfico de barras comparativo (acurácia, F1, AUC, tempo, parâmetros) |

---

## 10. Configuração e Execução

### Dependências

```
torch
numpy
pandas
scikit-learn
matplotlib
openpyxl
python-pptx
```

Instalação: `pip install -r requirements.txt`

### Parâmetros principais (`src/config.py`)

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `NUM_MFS` | 3 | MFs por feature numérica (baixo/médio/alto) |
| `ANFIS_N_CLUSTERS` | 200 | Clusters K-Means para geração do pool de regras |
| `TOP_RULES` | 10 | Regras exibidas no heatmap e salvas em regras.txt |
| `EPOCHS_ANFIS` | 200 | Épocas de treinamento ANFIS |
| `EPOCHS_MLP` | 200 | Épocas de treinamento MLP |
| `BATCH_SIZE` | 32 | Tamanho do mini-batch |
| `LR_ANFIS` | 1e-3 | Learning rate ANFIS (Adam) |
| `LR_MLP` | 1e-3 | Learning rate MLP (Adam) |
| `MLP_HIDDEN_DIMS` | [64, 32] | Neurônios por camada oculta |
| `TRAIN_RATIO` | 0.8 | Fração de treino |
| `RANDOM_SEED` | 42 | Semente para reprodutibilidade |

### Execução

```bash
# Rodar experimento completo
python src/main.py

# Gerar apresentação PPTX
python gerar_apresentacao.py
```

---

## 11. Estrutura de Arquivos

```
ANFIS-Project/
├── src/
│   ├── config.py                          # Parâmetros globais
│   ├── main.py                            # Ponto de entrada
│   ├── data/
│   │   ├── heart_failure.csv              # Dataset principal
│   │   └── loader.py                      # PartialScaler + load_dataset
│   ├── classes/
│   │   ├── fuzzy/
│   │   │   ├── MixedFuzzyLayer.py         # Fuzzificação mista (Gauss + one-hot)
│   │   │   ├── ClusterRuleLayer.py        # T-norma produto, rule_idx como buffer
│   │   │   ├── DefuzzyLayer.py            # nn.Linear normalizado (TS)
│   │   │   └── GaussianFuzzyLayer.py      # Fuzzificação só-Gaussiana (legado)
│   │   └── models/
│   │       ├── ANFIS.py                   # nn.Module completo
│   │       └── MLP.py                     # nn.Module MLP
│   ├── models/
│   │   ├── ANFIS.py                       # Wrapper treino/inferência ANFIS
│   │   └── MLP.py                         # Wrapper treino/inferência MLP
│   ├── evaluation/
│   │   └── metrics.py                     # accuracy, f1, auc, rmse, evaluate()
│   ├── experiments/
│   │   ├── experiment1.py                 # Pipeline Heart Failure
│   │   └── auxiliary_functions/
│   │       └── aux_functions.py           # Todos os gráficos e utilitários
│   └── clustering/
│       └── fcm.py                         # Implementação FCM (Bezdek, legado)
├── gerar_apresentacao.py                  # Gerador PPTX
├── documentacao_tecnica.md               # Este documento
├── requirements.txt
├── README.md
└── .gitignore
```

---

*Projeto desenvolvido para disciplina de Lógica Fuzzy — Mestrado, Junho 2026.*
