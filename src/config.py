"""
Parâmetros globais — edite aqui para alterar o comportamento dos experimentos.
"""
import os

DATASET     = 'heart'
TRAIN_RATIO = 0.8
RANDOM_SEED = 42

# Partição fuzzy — número de MFs por feature numérica
NUM_MFS = 3

# K-Means — pool de regras para o ANFIS
ANFIS_N_CLUSTERS = 200

# Heatmap — quantas regras exibir
TOP_RULES = 10

# Treinamento
EPOCHS_MLP   = 200
EPOCHS_ANFIS = 200
BATCH_SIZE   = 32
LR_MLP       = 1e-3
LR_ANFIS     = 1e-3
MLP_HIDDEN_DIMS = [64, 32]

RESULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
