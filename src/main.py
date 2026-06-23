"""
Heart Failure — Classificação de Risco Cardíaco

Uso:
    python src/main.py
    python src/main.py --verbose
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import argparse
from experiments import experiment1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true', help='Exibir o loss por época')
    args = parser.parse_args()
    experiment1.run_heart(verbose=args.verbose)


if __name__ == '__main__':
    main()
