# ANFIS Project

Projeto de apresentação semestral para a disciplina de **Lógica Fuzzy**.  
Implementa e compara três famílias de modelos — **MLP**, **FNN** e **ANFIS** — com foco no tradeoff entre acurácia preditiva e interpretabilidade.

---

## Modelos implementados

| Modelo | Descrição |
|--------|-----------|
| **MLP** | Perceptron multicamadas padrão, sem componentes fuzzy |
| **FNN** | Rede Neural Fuzzy — fuzzifica as entradas via funções de pertinência gaussianas e processa com camadas MLP |
| **ANFIS** | Adaptive Neuro-Fuzzy Inference System — usa fuzzificação, combinação por regras (produto T-norma) e defuzzificação Takagi-Sugeno |

---

## Dependências

### Python
Versão recomendada: **3.11**

### Pacotes

| Pacote | Uso |
|--------|-----|
| `torch` | Treinamento dos modelos (camadas, gradientes, otimizador) |
| `numpy` | Operações numéricas |
| `pandas` | Carregamento e manipulação dos datasets |
| `scikit-learn` | Normalização (`StandardScaler`) e divisão treino/teste |
| `requests` | Download do dataset Wine Quality (UCI) |
| `kagglehub` | Download dos datasets Kaggle com token KGAT_ |
| `openpyxl` | Exportação dos resultados em formato Excel (.xlsx) |
| `matplotlib` | Geração de gráficos nos experimentos |

Instale tudo de uma vez:

```bash
pip install torch numpy pandas scikit-learn requests kagglehub openpyxl matplotlib
```

---

## Configuração do ambiente

### Opção A — Conda (recomendado)

```bash
conda create -n ANFIS python=3.11 -y
conda activate ANFIS
pip install torch numpy pandas scikit-learn requests kagglehub openpyxl matplotlib
```

### Opção B — venv

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install torch numpy pandas scikit-learn requests kagglehub openpyxl matplotlib
```

---

## Obtenção dos datasets

Os três datasets precisam estar em `src/data/` antes de rodar os experimentos.

### 1. Configure o token do Kaggle

1. Acesse [kaggle.com](https://www.kaggle.com) → **Account** → **Settings** → **Create New Token**
2. Salve o token no arquivo:

```bash
# Linux/Mac
echo SEU_TOKEN_AQUI > ~/.kaggle/access_token

# Windows (PowerShell)
"SEU_TOKEN_AQUI" | Out-File -FilePath "$env:USERPROFILE\.kaggle\access_token" -Encoding utf8
```

### 2. Execute o coletor

```bash
python src/data/collector.py
```

Isso baixa automaticamente:

| Dataset | Fonte | Arquivo salvo |
|---------|-------|---------------|
| Pima Indians Diabetes | Kaggle (`uciml/pima-indians-diabetes-database`) | `src/data/pima_diabetes.csv` |
| Wine Quality (tinto) | UCI ML Repository | `src/data/winequality-red.csv` |
| Heart Failure | Kaggle (`fedesoriano/heart-failure-prediction`) | `src/data/heart_failure.csv` |

> Re-executar o coletor é seguro — ele pula arquivos já presentes.

---

## Como executar

Todos os comandos devem ser rodados a partir da **raiz do projeto** com o ambiente ativado.

### Rodar todos os experimentos

```bash
python src/main.py
```

### Rodar um experimento específico

```bash
python src/main.py --exp 1   # Comparação baseline
python src/main.py --exp 2   # Estudo de parâmetros ANFIS
python src/main.py --exp 3   # Arquitetura híbrida
```

### Mostrar o loss por época durante o treinamento

```bash
python src/main.py --verbose
python src/main.py --exp 1 --verbose
```

---

## Experimentos

### Experimento 1 — Comparação baseline
Treina MLP, FNN e ANFIS nos três datasets e reporta acurácia/RMSE, tempo de treinamento e número de parâmetros.

### Experimento 2 — Estudo de parâmetros ANFIS
Treina o ANFIS com `num_mfs ∈ {2, 3, 4}` e mostra o tradeoff entre número de regras e acurácia, ilustrando a explosão combinatória.

### Experimento 3 — Arquitetura híbrida
1. Treina o MLP até convergência
2. Extrai importância de features via gradiente
3. Seleciona as top-5 features
4. Inicializa os centros das funções de pertinência do ANFIS com estatísticas da distribuição das features
5. Treina o ANFIS para aproximar as saídas do MLP (targets suaves)
6. Compara a aproximação do ANFIS com o ground truth
7. Imprime as regras linguísticas aprendidas

---

## Saídas

Após a execução, os resultados são salvos automaticamente em `src/results/`:

| Arquivo | Conteúdo |
|---------|----------|
| `results.xlsx` | Métricas de avaliação — uma aba por dataset |
| `raw_train_test.xlsx` | Dados brutos de treino e teste antes da avaliação (abas `{dataset}_train` e `{dataset}_test`) |

Os arquivos ficam em subpastas nomeadas com a data e hora da execução, por exemplo:  
`src/results/experiment1/2026_06_09_14_30/`

---

## Estrutura do projeto

```
ANFIS-Project/
├── src/
│   ├── classes/
│   │   ├── fuzzy/
│   │   │   ├── FuzzyLayer.py        # Funções de pertinência gaussianas
│   │   │   ├── ANFISRuleLayer.py    # Combinação por regras (T-norma produto)
│   │   │   └── DefuzzyLayer.py      # Defuzzificação Takagi-Sugeno
│   │   └── models/
│   │       ├── MLP.py               # Arquitetura MLP (nn.Module)
│   │       └── ANFIS.PY             # Arquitetura ANFIS (nn.Module)
│   ├── models/
│   │   ├── MLP.py                   # Wrapper de treino/predição — MLP
│   │   ├── FNN.py                   # Wrapper de treino/predição — FNN
│   │   └── ANFIS.py                 # Wrapper de treino/predição — ANFIS
│   ├── data/
│   │   ├── collector.py             # Download dos datasets
│   │   ├── loader.py                # Carregamento, encoding e normalização
│   │   ├── pima_diabetes.csv
│   │   ├── winequality-red.csv
│   │   └── heart_failure.csv
│   ├── evaluation/
│   │   └── metrics.py               # Acurácia, RMSE, contagem de parâmetros
│   ├── experiments/
│   │   ├── auxiliary_functions/
│   │   │   └── aux_functions.py     # Salvamento de resultados em Excel
│   │   ├── experiment1.py
│   │   ├── experiment2.py
│   │   └── experiment3.py
│   ├── results/                     # Gerado automaticamente ao executar
│   │   ├── experiment1/
│   │   ├── experiment2/
│   │   └── experiment3/
│   └── main.py                      # Ponto de entrada com CLI
├── CLAUDE.md                        # Decisões de arquitetura e convenções
└── README.md
```
