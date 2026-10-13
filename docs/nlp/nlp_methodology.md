# NLP Methodology

The NLP pipeline in BALLRIQ involves comprehensive preprocessing, cross-lingual event classification, and structured entity/event extraction. This methodology handles Hindi, Marathi, English, and their code-mixed variants (Hinglish, Marathlish).

## Preprocessing Pipeline
Input commentary text is standardized through several steps located in `backend/app/nlp/preprocessing/`:
1. **Unicode Normalization** (`unicode_normalization.py`): Replaces irregular characters and standardized forms (e.g. NFKC normalization).
2. **Text Cleaning** (`text_cleaning.py`): Strips junk artifacts while preserving the semantic value of cricket terminology.
3. **Number Normalization** (`number_normalization.py`): Handles digits for runs, overs, and formats.
4. **Language Processing** (`language_processing.py`): Employs language labels and detects source language (Hindi, Marathi, English, or code-mixed variants) along with confidence metrics.
5. **Cricket Normalization** (`cricket_normalization.py`): Resolves cricket vocabulary to canonical concepts.
6. **Player Aliases** (`player_normalization.py`): Maps variations of player names to their canonical forms (via alias parser).
7. **Tokenization** (`tokenization.py`): Prepares cleaned and normalized text into machine-readable tokens.

## Event Classification
BALLRIQ assigns EXACTLY ONE of the defined cricket events (e.g., FOUR, SIX, WICKET) to each commentary line. Valid tags are defined in the taxonomy (`CENTURY`, `DOT`, `DOUBLE`, `FIFTY`, `FOUR`, `NO_BALL`, `OTHER`, `SINGLE`, `SIX`, `TRIPLE`, `WICKET`, `WIDE`).

Two models are supported for event classification:
- **Lexical/Statistical Baseline**: Uses TF-IDF features with Logistic Regression. Handled by `scripts/train_nlp_baseline.py`. Extremely fast (approx 1.2ms inference latency), achieving 99.61% precision on test data.
- **Neural Multilingual (XLM-RoBERTa)**: Handled by `scripts/train_xlmr.py` (model stored in `models/nlp/event_classifier_xlmr`). Deep multilingual approach boasting superior cross-lingual boundary disambiguation on code-mixed Hinglish and Marathlish. 99.86% f1 score, 14.2ms inference latency.
Evaluation metrics across both approaches are exported to `reports/nlp/`. 

When data relies on match grouping, `scripts/split_dataset.py` generates train/val/test splits, partitioned by match context to prevent sequence leakage.

## Entity and Event Structuring
While the overarching ML MODELS determine the high-level *Event Type*, deterministic rules structure the entities within the event explicitly.
- **Entity Extraction**: `backend/app/nlp/entity_extraction/entity_extractor.py` detects players (batter, bowler, fielder) and team entities. 
- **Event Structuring**: `backend/app/nlp/event_extraction/event_extractor.py` structures explicit attributes (wicket type, runs, boundary context) derived directly from the extracted NLP rules.