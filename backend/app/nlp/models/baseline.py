#!/usr/bin/env python3
"""
TF-IDF + Logistic Regression baseline model for cricket commentary event classification.
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from sklearn.model_selection import train_test_split

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.nlp.preprocessing.pipeline import NLPPreprocessingPipeline


@dataclass
class BaselineModelResult:
    """Result of baseline model prediction."""
    predictions: List[str]
    probabilities: np.ndarray
    labels: List[str]


class BaselineEventClassifier:
    """
    TF-IDF + Logistic Regression classifier for cricket commentary events.
    """

    def __init__(
        self,
        max_features: int = 10000,
        ngram_range: Tuple[int, int] = (1, 2),
        min_df: int = 2,
        max_df: float = 0.95,
        C: float = 1.0,
        class_weight: str = 'balanced',
        random_state: int = 42
    ):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df
        self.C = C
        self.class_weight = class_weight
        self.random_state = random_state

        self.pipeline = None
        self.preprocessing_pipeline = NLPPreprocessingPipeline()
        self.classes_ = None
        self.is_fitted = False

    def _get_texts_and_labels(self, records: List[Dict]) -> Tuple[List[str], List[str]]:
        """Extract texts and labels from records."""
        texts = []
        labels = []
        for record in records:
            text = record.get('preprocessed_text') or record.get('original_text', '')
            label = record.get('event_label', 'OTHER')
            if text and label:
                texts.append(text)
                labels.append(label)
        return texts, labels

    def fit(self, train_records: List[Dict], val_records: Optional[List[Dict]] = None):
        """Train the classifier."""
        print("Extracting texts and labels...")
        train_texts, train_labels = self._get_texts_and_labels(train_records)

        print(f"Training samples: {len(train_texts)}")
        print(f"Classes: {sorted(set(train_labels))}")

        # Build pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=self.max_features,
                ngram_range=self.ngram_range,
                min_df=self.min_df,
                max_df=self.max_df,
                sublinear_tf=True
            )),
            ('clf', LogisticRegression(
                C=self.C,
                class_weight=self.class_weight,
                random_state=self.random_state,
                max_iter=1000,
                solver='lbfgs'
            ))
        ])

        print("Training TF-IDF + Logistic Regression...")
        self.pipeline.fit(train_texts, train_labels)

        self.classes_ = self.pipeline.classes_.tolist()
        self.is_fitted = True

        # Evaluate on validation set if provided
        if val_records:
            val_metrics = self.evaluate(val_records)
            print(f"Validation Accuracy: {val_metrics['accuracy']:.4f}")
            print(f"Validation Macro F1: {val_metrics['macro_f1']:.4f}")

        return self

    def predict(self, records: List[Dict]) -> BaselineModelResult:
        """Predict event labels for records."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        texts, _ = self._get_texts_and_labels(records)
        if not texts:
            return BaselineModelResult([], np.array([]), self.classes_)

        predictions = self.pipeline.predict(texts)
        probabilities = self.pipeline.predict_proba(texts)

        return BaselineModelResult(
            predictions=predictions.tolist(),
            probabilities=probabilities,
            labels=self.classes_
        )

    def predict_single(self, text: str) -> Dict:
        """Predict event for a single text."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        # Preprocess text
        result = self.preprocessing_pipeline.process(text)
        processed_text = result.final_text

        pred = self.pipeline.predict([processed_text])[0]
        proba = self.pipeline.predict_proba([processed_text])[0]

        class_probs = {cls: float(prob) for cls, prob in zip(self.classes_, proba)}

        return {
            'predicted_event': pred,
            'confidence': float(max(proba)),
            'all_probabilities': class_probs,
            'preprocessed_text': processed_text,
            'detected_language': result.detected_language
        }

    def evaluate(self, records: List[Dict]) -> Dict:
        """Evaluate model on records."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        texts, true_labels = self._get_texts_and_labels(records)
        if not texts:
            return {'accuracy': 0.0, 'macro_f1': 0.0, 'per_class': {}}

        pred_result = self.predict(records)
        predictions = pred_result.predictions

        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, support = precision_recall_fscore_support(
            true_labels, predictions, average=None, labels=self.classes_, zero_division=0
        )
        macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
            true_labels, predictions, average='macro', zero_division=0
        )

        per_class = {}
        for cls, p, r, f, s in zip(self.classes_, precision, recall, f1, support):
            per_class[cls] = {
                'precision': float(p),
                'recall': float(r),
                'f1': float(f),
                'support': int(s)
            }

        return {
            'accuracy': float(accuracy),
            'macro_precision': float(macro_precision),
            'macro_recall': float(macro_recall),
            'macro_f1': float(macro_f1),
            'per_class': per_class,
            'num_samples': len(true_labels)
        }

    def save(self, model_dir: Path):
        """Save model to directory."""
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)

        # Save sklearn pipeline
        with open(model_dir / "model.pkl", 'wb') as f:
            pickle.dump(self.pipeline, f)

        # Save metadata
        metadata = {
            'max_features': self.max_features,
            'ngram_range': self.ngram_range,
            'min_df': self.min_df,
            'max_df': self.max_df,
            'C': self.C,
            'class_weight': self.class_weight,
            'random_state': self.random_state,
            'classes': self.classes_,
            'is_fitted': self.is_fitted
        }
        with open(model_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        print(f"Model saved to {model_dir}")

    @classmethod
    def load(cls, model_dir: Path) -> 'BaselineEventClassifier':
        """Load model from directory."""
        model_dir = Path(model_dir)

        with open(model_dir / "metadata.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Create instance with saved params
        instance = cls(
            max_features=metadata['max_features'],
            ngram_range=tuple(metadata['ngram_range']),
            min_df=metadata['min_df'],
            max_df=metadata['max_df'],
            C=metadata['C'],
            class_weight=metadata['class_weight'],
            random_state=metadata['random_state']
        )

        # Load pipeline
        with open(model_dir / "model.pkl", 'rb') as f:
            instance.pipeline = pickle.load(f)

        instance.classes_ = metadata['classes']
        instance.is_fitted = metadata['is_fitted']

        return instance


def load_split_data(split_dir: Path) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Load train/val/test CSV splits."""
    import csv

    def load_csv(path):
        records = []
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse JSON fields
                for key in ['player_mentions', 'team_mentions', 'tokens', 'entities', 'cricket_events']:
                    if key in row and row[key]:
                        try:
                            row[key] = json.loads(row[key])
                        except:
                            row[key] = []
                records.append(row)
        return records

    train_file = split_dir / "train.csv"
    val_file = split_dir / "val.csv" if (split_dir / "val.csv").exists() else split_dir / "validation.csv"
    test_file = split_dir / "test.csv"

    train = load_csv(train_file)
    val = load_csv(val_file)
    test = load_csv(test_file)

    return train, val, test


def train_baseline(
    data_dir: Path,
    model_dir: Path,
    max_features: int = 10000,
    C: float = 1.0
) -> Dict:
    """Full training pipeline for baseline model."""
    print("Loading data splits...")
    train_records, val_records, test_records = load_split_data(data_dir)

    print(f"Train: {len(train_records)}, Val: {len(val_records)}, Test: {len(test_records)}")

    # Initialize and train model
    classifier = BaselineEventClassifier(
        max_features=max_features,
        C=C
    )

    classifier.fit(train_records, val_records)

    # Evaluate on test set
    print("\nEvaluating on test set...")
    test_metrics = classifier.evaluate(test_records)

    print(f"\nTest Accuracy: {test_metrics['accuracy']:.4f}")
    print(f"Test Macro Precision: {test_metrics['macro_precision']:.4f}")
    print(f"Test Macro Recall: {test_metrics['macro_recall']:.4f}")
    print(f"Test Macro F1: {test_metrics['macro_f1']:.4f}")

    print("\nPer-class metrics:")
    for cls, metrics in test_metrics['per_class'].items():
        print(f"  {cls}: P={metrics['precision']:.3f}, R={metrics['recall']:.3f}, F1={metrics['f1']:.3f}, Support={metrics['support']}")

    # Save model
    classifier.save(model_dir)

    # Save metrics
    base_proj_dir = Path(__file__).resolve().parents[4]
    metrics_path = base_proj_dir / "reports" / "nlp" / "baseline_metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(test_metrics, f, indent=2, ensure_ascii=False)

    print(f"\nMetrics saved to {metrics_path}")

    return test_metrics


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent.parent
    data_dir = base_path / "data" / "processed" / "nlp"
    model_dir = base_path / "models" / "nlp" / "event_classifier_baseline"

    train_baseline(data_dir, model_dir)