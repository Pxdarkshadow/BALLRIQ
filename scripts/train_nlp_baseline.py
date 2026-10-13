#!/usr/bin/env python3
"""
CLI script to train NLP baseline model (TF-IDF + Logistic Regression).
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.nlp.models.baseline import train_baseline


def main():
    parser = argparse.ArgumentParser(description="Train TF-IDF + Logistic Regression baseline for cricket event classification")
    parser.add_argument('--data-dir', type=str, default='data/processed/nlp', help='Directory with train/val/test CSVs')
    parser.add_argument('--model-dir', type=str, default='models/nlp/event_classifier_baseline', help='Output model directory')
    parser.add_argument('--max-features', type=int, default=10000, help='TF-IDF max features')
    parser.add_argument('--C', type=float, default=1.0, help='Logistic Regression C parameter')

    args = parser.parse_args()

    base_path = Path(__file__).parent.parent
    data_dir = base_path / args.data_dir
    model_dir = base_path / args.model_dir

    if not data_dir.exists():
        print(f"Error: Data directory {data_dir} does not exist")
        print("Run split_dataset.py first to create train/val/test splits")
        sys.exit(1)

    train_baseline(data_dir, model_dir, args.max_features, args.C)


if __name__ == "__main__":
    main()