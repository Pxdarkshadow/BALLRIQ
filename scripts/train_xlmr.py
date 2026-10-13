#!/usr/bin/env python3
"""Train and save a local XLM-R cricket-event classifier.

This command deliberately never runs during application startup. It downloads
the requested base model only when necessary; pass ``--local-files-only`` for
offline/reproducible runs after the base model is cached.
"""

from __future__ import annotations

import argparse
import csv
import inspect
import json
import sys
from pathlib import Path
from typing import List, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def read_split(path: Path) -> Tuple[List[str], List[str]]:
    with path.open(encoding="utf-8", newline="") as file:
        pairs = [((row.get("preprocessed_text") or row.get("original_text") or ""),
                  (row.get("event_label") or "OTHER")) for row in csv.DictReader(file)]
    return [text for text, _ in pairs], [label for _, label in pairs]


def make_training_arguments(TrainingArguments, **kwargs):
    """Bridge the evaluation-strategy rename across transformers releases."""
    names = inspect.signature(TrainingArguments.__init__).parameters
    if "eval_strategy" not in names and "evaluation_strategy" in names:
        kwargs["evaluation_strategy"] = kwargs.pop("eval_strategy")
    if "use_cpu" in names:
        kwargs["use_cpu"] = not kwargs.pop("has_cuda")
    else:
        kwargs.pop("has_cuda")
    return TrainingArguments(**kwargs)


def main() -> int:
    parser = argparse.ArgumentParser(description="Train XLM-RoBERTa for cricket commentary event classification")
    parser.add_argument("--data-dir", type=Path, default=PROJECT_ROOT / "data" / "processed" / "nlp")
    parser.add_argument("--model-dir", type=Path, default=PROJECT_ROOT / "models" / "nlp" / "event_classifier_xlmr")
    parser.add_argument("--model-name", default="xlm-roberta-base")
    parser.add_argument("--epochs", type=float, default=3)
    parser.add_argument("--train-batch-size", type=int, default=8)
    parser.add_argument("--eval-batch-size", type=int, default=16)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--no-fp16", action="store_true")
    args = parser.parse_args()

    try:
        import numpy as np
        import torch
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support
        from torch.utils.data import Dataset
        from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
    except ImportError as exc:
        parser.error(f"XLM-R training requires optional dependencies: {exc}")

    splits = {name: args.data_dir / f"{name}.csv" for name in ("train", "val", "test")}
    missing = [str(path) for path in splits.values() if not path.is_file()]
    if missing:
        parser.error("Missing data split(s): " + ", ".join(missing))
    train_texts, train_raw = read_split(splits["train"])
    val_texts, val_raw = read_split(splits["val"])
    test_texts, test_raw = read_split(splits["test"])
    labels = sorted(set(train_raw))
    label2id = {label: index for index, label in enumerate(labels)}
    unknown = set(val_raw + test_raw) - set(labels)
    if unknown:
        parser.error(f"Labels absent from training data: {sorted(unknown)}")
    print(f"Train: {len(train_texts)}, Val: {len(val_texts)}, Test: {len(test_texts)}; labels: {labels}")

    tokenizer = AutoTokenizer.from_pretrained(args.model_name, local_files_only=args.local_files_only)

    class CricketDataset(Dataset):
        def __init__(self, texts: Sequence[str], raw_labels: Sequence[str]):
            self.encodings = tokenizer(list(texts), truncation=True, max_length=args.max_length, padding=True)
            self.labels = [label2id[label] for label in raw_labels]
        def __len__(self):
            return len(self.labels)
        def __getitem__(self, index):
            item = {key: torch.tensor(value[index]) for key, value in self.encodings.items()}
            item["labels"] = torch.tensor(self.labels[index], dtype=torch.long)
            return item

    id2label = {index: label for label, index in label2id.items()}
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name, num_labels=len(labels), label2id=label2id, id2label=id2label,
        local_files_only=args.local_files_only, ignore_mismatched_sizes=True,
    )
    has_cuda = torch.cuda.is_available()
    args.model_dir.mkdir(parents=True, exist_ok=True)

    def metrics(prediction):
        logits, actual = prediction
        predicted = np.argmax(logits, axis=-1)
        precision, recall, f1, _ = precision_recall_fscore_support(actual, predicted, average="macro", zero_division=0)
        return {"accuracy": accuracy_score(actual, predicted), "f1": f1, "precision": precision, "recall": recall}

    training_args = make_training_arguments(
        TrainingArguments, output_dir=str(args.model_dir), num_train_epochs=args.epochs,
        per_device_train_batch_size=args.train_batch_size, per_device_eval_batch_size=args.eval_batch_size,
        weight_decay=0.01, logging_steps=50, eval_strategy="epoch", save_strategy="epoch",
        load_best_model_at_end=True, metric_for_best_model="f1", greater_is_better=True,
        fp16=has_cuda and not args.no_fp16, report_to="none", has_cuda=has_cuda,
    )
    trainer = Trainer(model=model, args=training_args, train_dataset=CricketDataset(train_texts, train_raw),
                      eval_dataset=CricketDataset(val_texts, val_raw), compute_metrics=metrics)
    trainer.train()
    test_metrics = trainer.evaluate(CricketDataset(test_texts, test_raw), metric_key_prefix="test")
    trainer.save_model(args.model_dir)
    tokenizer.save_pretrained(args.model_dir)
    metadata = {"model_type": "xlm-roberta", "base_model": args.model_name, "max_length": args.max_length,
                "labels": labels, "test_metrics": test_metrics}
    (args.model_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved XLM-R artifacts to {args.model_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
