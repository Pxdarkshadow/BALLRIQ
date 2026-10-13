#!/usr/bin/env python3
"""
Train/Val/Test split by match_id for BALLRIQ NLP dataset.
Prevents data leakage by keeping all records from same match in same split.
"""

import json
import csv
import random
from pathlib import Path
from collections import Counter

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.nlp.preprocessing.pipeline import NLPPreprocessingPipeline


def load_commentary(commentary_path):
    """Load commentary records from JSONL."""
    records = []
    with open(commentary_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def split_by_match_id(records, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, seed=42):
    """Split records by match_id."""
    # Get unique match_ids
    match_ids = list(set(r['match_id'] for r in records))

    # Shuffle with seed
    random.seed(seed)
    random.shuffle(match_ids)

    # Calculate split sizes
    n_total = len(match_ids)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    train_match_ids = set(match_ids[:n_train])
    val_match_ids = set(match_ids[n_train:n_train + n_val])
    test_match_ids = set(match_ids[n_train + n_val:])

    # Assign records to splits
    train_records = []
    val_records = []
    test_records = []

    for record in records:
        mid = record['match_id']
        if mid in train_match_ids:
            train_records.append(record)
        elif mid in val_match_ids:
            val_records.append(record)
        else:
            test_records.append(record)

    return {
        'train': {'match_ids': train_match_ids, 'records': train_records},
        'val': {'match_ids': val_match_ids, 'records': val_records},
        'test': {'match_ids': test_match_ids, 'records': test_records}
    }


def preprocess_records(records, pipeline):
    """Run preprocessing pipeline on records."""
    print(f"Preprocessing {len(records)} records...")
    processed = []
    for i, record in enumerate(records):
        text = record.get('original_text', '')
        result = pipeline.process(text)
        record['preprocessed_text'] = result.final_text
        record['detected_language'] = result.detected_language
        record['language_confidence'] = result.language_confidence
        record['is_code_mixed'] = result.is_code_mixed
        record['tokens'] = result.tokens
        record['token_count'] = result.token_count
        record['entities'] = result.entities
        record['cricket_events'] = result.cricket_events
        processed.append(record)
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{len(records)}")
    return processed


def save_split_csv(records, output_path, fieldnames):
    """Save records to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for record in records:
            # Convert lists to JSON strings for CSV
            row = dict(record)
            for key in ['player_mentions', 'team_mentions', 'tokens', 'entities', 'cricket_events']:
                if key in row and isinstance(row[key], (list, dict)):
                    row[key] = json.dumps(row[key], ensure_ascii=False)
            writer.writerow(row)


def print_split_stats(splits):
    """Print statistics for each split."""
    for split_name, split_data in splits.items():
        records = split_data['records']
        match_ids = split_data['match_ids']

        print(f"\n=== {split_name.upper()} ===")
        print(f"  Matches: {len(match_ids)}")
        print(f"  Records: {len(records)}")

        # Language distribution
        lang_dist = Counter(r.get('language', 'unknown') for r in records)
        print(f"  Languages: {dict(lang_dist)}")

        # Event distribution
        event_dist = Counter(r.get('event_label', 'unknown') for r in records)
        print(f"  Events: {dict(event_dist)}")


def save_split_info(splits, output_path):
    """Save split information to JSON."""
    info = {}
    for split_name, split_data in splits.items():
        records = split_data['records']
        match_ids = split_data['match_ids']

        lang_dist = Counter(r.get('language', 'unknown') for r in records)
        event_dist = Counter(r.get('event_label', 'unknown') for r in records)

        info[split_name] = {
            'match_ids': sorted(list(match_ids)),
            'num_matches': len(match_ids),
            'num_records': len(records),
            'language_distribution': dict(lang_dist),
            'event_distribution': dict(event_dist)
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print(f"\nSplit info saved to {output_path}")


def main():
    base_path = Path(__file__).parent.parent
    commentary_path = base_path / "data" / "raw" / "commentary" / "commentary.jsonl"
    output_dir = base_path / "data" / "processed" / "nlp"

    print("Loading commentary data...")
    records = load_commentary(commentary_path)
    print(f"Loaded {len(records)} records")

    # Initialize preprocessing pipeline
    print("Initializing preprocessing pipeline...")
    pipeline = NLPPreprocessingPipeline()

    # Split by match_id
    print("Splitting by match_id...")
    splits = split_by_match_id(records)

    # Print raw split stats
    print_split_stats(splits)

    # Preprocess each split
    print("\nPreprocessing splits...")
    for split_name in ['train', 'val', 'test']:
        splits[split_name]['records'] = preprocess_records(splits[split_name]['records'], pipeline)

    # Fieldnames for CSV
    fieldnames = [
        'commentary_id', 'match_id', 'language', 'original_text', 'preprocessed_text',
        'detected_language', 'language_confidence', 'is_code_mixed',
        'event_label', 'dismissal_type', 'over', 'ball', 'timestamp',
        'player_mentions', 'team_mentions', 'tokens', 'token_count',
        'entities', 'cricket_events', 'confidence', 'translator_id', 'is_synthetic'
    ]

    # Save CSVs
    for split_name in ['train', 'val', 'test']:
        output_path = output_dir / f"{split_name}.csv"
        save_split_csv(splits[split_name]['records'], output_path, fieldnames)
        print(f"Saved {len(splits[split_name]['records'])} records to {output_path}")

    # Save split info
    save_split_info(splits, output_dir / "split_info.json")

    print("\nDone!")


if __name__ == "__main__":
    main()