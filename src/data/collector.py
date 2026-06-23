"""
Baixa o dataset Heart Failure para src/data/.

Configuração do Kaggle (uma única vez):
  1. kaggle.com → Account → Settings → Create New Token
  2. echo <seu_token> > ~/.kaggle/access_token

Execução:
  python src/data/collector.py
"""
import os
import shutil
import sys
from pathlib import Path

DATA_DIR    = Path(__file__).resolve().parent
KAGGLE_SLUG = "fedesoriano/heart-failure-prediction"
CSV_PATTERN = "heart"
SAVE_AS     = "heart_failure.csv"


def _load_token() -> str:
    token_file = Path.home() / ".kaggle" / "access_token"
    json_file  = Path.home() / ".kaggle" / "kaggle.json"
    if token_file.exists():
        return token_file.read_text().strip()
    if json_file.exists():
        import json
        return json.loads(json_file.read_text())["key"]
    print(
        "\n[ERRO] Nenhuma credencial do Kaggle encontrada.\n"
        "  Execute:  echo <seu_token> > ~/.kaggle/access_token\n"
        "  Token:  kaggle.com → Account → Settings → Create New Token\n"
    )
    sys.exit(1)


def run() -> None:
    print(f"\nColetando dataset em {DATA_DIR}\n")
    dest = DATA_DIR / SAVE_AS
    if dest.exists():
        print(f"  [pular] {SAVE_AS} já está presente")
        print("\nDataset pronto.")
        return

    try:
        import kagglehub
    except ImportError:
        print("\n[ERRO] kagglehub não instalado.\n  Execute: pip install kagglehub\n")
        sys.exit(1)

    token = _load_token()
    os.environ["KAGGLE_TOKEN"] = token
    print(f"  Baixando {KAGGLE_SLUG} via kagglehub ...")
    cached_path = Path(kagglehub.dataset_download(KAGGLE_SLUG))

    candidates = sorted(cached_path.glob(f"*{CSV_PATTERN}*.csv")) or sorted(cached_path.glob("*.csv"))
    if not candidates:
        print(f"  [ERRO] Nenhum CSV encontrado em {cached_path}")
        return

    shutil.copy(candidates[0], dest)
    print(f"  Salvo  → {SAVE_AS}")
    print("\nDataset pronto.")


if __name__ == "__main__":
    run()
