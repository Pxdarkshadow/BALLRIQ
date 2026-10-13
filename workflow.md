# BALLRIQ: Multilingual Cricket Commentary Analysis and Information Retrieval System

### Subtitle

**A Hindi and Marathi NLP Pipeline with Hybrid Information Retrieval and Retrieval-Augmented Question Answering for Cricket Match Intelligence**

---

# 1. PROJECT OBJECTIVE

Build BALLRIQ as a complete academic project that simultaneously demonstrates concepts from:

## Natural Language Processing

and

## Information Retrieval

The project must not hide technical processes behind a chatbot or API.

Every major stage must be:

- Clearly labelled.
- Independently executable.
- Independently testable.
- Visually demonstrable.
- Documented.
- Evaluated using appropriate metrics.

The system must follow this complete pipeline:

```text
RAW DATASET
    ↓
DATA COLLECTION
    ↓
DATA UNDERSTANDING
    ↓
DATA PREPROCESSING
    ↓
NLP FEATURE EXTRACTION
    ↓
NLP MODEL TRAINING
    ↓
ENTITY / EVENT EXTRACTION
    ↓
STRUCTURED CRICKET KNOWLEDGE
    ↓
DOCUMENT CREATION
    ↓
LEXICAL INDEXING
    ↓
SEMANTIC INDEXING
    ↓
HYBRID INFORMATION RETRIEVAL
    ↓
RETRIEVAL EVALUATION
    ↓
RAG CONTEXT CONSTRUCTION
    ↓
LLM ANSWER GENERATION
    ↓
GROUNDED ANSWER WITH SOURCES
```

This pipeline must be reflected in:

1. Project source code.
2. Folder structure.
3. Database.
4. Jupyter notebooks or analysis scripts.
5. Frontend academic explorer pages.
6. Evaluation reports.
7. README documentation.

---

# 2. CRITICAL ACADEMIC REQUIREMENT

Do not treat the dataset as an afterthought.

The project must have a properly structured dataset pipeline.

Every dataset used must have:

- Dataset name.
- Source.
- Description.
- Number of records.
- Languages.
- Features/columns.
- Purpose in the project.
- Preprocessing applied.
- Train/validation/test split.
- Limitations.

Create:

```text
data/
│
├── raw/
│   ├── commentary/
│   ├── audio/
│   ├── matches/
│   └── player_data/
│
├── interim/
│   ├── cleaned/
│   ├── normalized/
│   └── language_detected/
│
├── processed/
│   ├── nlp/
│   ├── ir/
│   └── database/
│
├── annotations/
│   ├── event_labels.csv
│   ├── entity_labels.json
│   └── annotation_guidelines.md
│
├── evaluation/
│   ├── nlp_test_set.csv
│   └── ir_queries.json
│
└── README.md
```

Raw data must never be overwritten.

The pipeline should always be:

```text
RAW → INTERIM → PROCESSED
```

---

# 3. DATASET STRATEGY

Create a documented dataset called:

# BALLRIQ Cricket Commentary Dataset

The dataset should contain three categories.

---

## DATASET A — STRUCTURED CRICKET MATCH DATA

Purpose:

Provide match information for the FotMob-style platform.

Fields:

```text
match_id
date
format
tournament
venue
team_a
team_b
winner
result
```

Additional structured data:

```text
players
batting_statistics
bowling_statistics
innings
scores
```

This dataset is primarily used for:

- Match UI.
- Statistics.
- Player pages.
- Match summaries.
- RAG context.
- IR metadata.

---

## DATASET B — MULTILINGUAL CRICKET COMMENTARY DATASET

This is the core NLP dataset.

Fields:

```text
commentary_id
match_id
language
original_text
timestamp
over
ball
player_mentions
team_mentions
event_label
dismissal_type
```

Languages:

- Hindi.
- Marathi.
- English where necessary for cross-lingual retrieval.

Example:

```text
original_text:

"कोहली ने शानदार कवर ड्राइव खेला और गेंद सीमा रेखा के बाहर चली गई"

event_label:

FOUR
```

Marathi example:

```text
"कोहलीने अप्रतिम कव्हर ड्राइव्ह मारला आणि चेंडू सीमारेषेबाहेर गेला"

event_label:

FOUR
```

---

## DATASET C — CRICKET AUDIO DATASET

Fields:

```text
audio_id
match_id
language
audio_path
duration
transcript
start_time
end_time
```

This dataset is used for:

- Speech-to-text.
- Audio preprocessing.
- Language detection.
- NLP pipeline demonstration.

---

# 4. DATA COLLECTION AND SOURCE DOCUMENTATION

Before implementing models, create:

```text
docs/dataset_documentation.md
```

For every dataset, document:

```text
Dataset Name:

Source:

Data Type:

Number of Records:

Languages:

Features:

Purpose:

License / Usage Consideration:

Known Limitations:
```

Do not scrape copyrighted commentary and present it as a freely reusable dataset without checking usage rights.

Prefer:

- Public datasets.
- Open cricket datasets.
- Structured ball-by-ball datasets.
- Self-created multilingual annotations.
- Synthetic augmentation clearly labelled as synthetic.

If Hindi and Marathi commentary data is insufficient:

Use a hybrid dataset strategy:

```text
PUBLIC CRICKET DATA
+
SELF-CREATED HINDI/MARATHI ANNOTATIONS
+
CLEARLY LABELLED TRANSLATION/AUGMENTATION
```

Never pretend translated data is naturally occurring commentary.

---

# 5. DATASET EXPLORATION

Before preprocessing, create:

```text
notebooks/
    01_dataset_exploration.ipynb
```

or an equivalent reproducible Python script.

Perform Exploratory Data Analysis.

Show:

- Number of matches.
- Number of commentary records.
- Number of records per language.
- Event distribution.
- Player distribution.
- Match distribution.
- Missing values.
- Duplicate records.
- Text length distribution.
- Class imbalance.

Generate labelled outputs.

Example:

```text
Dataset Summary

Total Commentary Records: 5,000

Hindi: 2,000

Marathi: 2,000

English: 1,000
```

Event distribution:

```text
FOUR: 1,200
SIX: 700
WICKET: 900
DOT_BALL: 1,500
OTHER: 700
```

Save all results.

---

# 6. DATA QUALITY CHECKING

Create:

```text
scripts/validate_dataset.py
```

This must check:

- Missing text.
- Invalid language values.
- Missing labels.
- Duplicate commentary.
- Invalid timestamps.
- Invalid match IDs.
- Invalid event labels.
- Encoding problems.

The script should produce:

```text
reports/data_quality_report.json
```

Example:

```text
Total Records: 5000

Valid Records: 4920

Duplicate Records Removed: 35

Missing Text Records: 12

Invalid Labels: 8

Final Records: 4920
```

---

# 7. NLP PREPROCESSING PIPELINE

Create:

```text
backend/app/nlp/preprocessing/
```

Structure:

```text
preprocessing/

    unicode_normalization.py

    text_cleaning.py

    language_processing.py

    number_normalization.py

    cricket_normalization.py

    transliteration.py

    tokenization.py

    pipeline.py
```

Every preprocessing step must be individually labelled.

---

# 8. PREPROCESSING STEP 1 — UNICODE NORMALIZATION

Normalize:

- Hindi Unicode variants.
- Marathi Unicode variants.
- Extra whitespace.
- Repeated punctuation.
- Invalid encoding characters.

Example:

```text
Input:

"कोहली   ने  शानदार!!!  चौका मारा"

Output:

"कोहली ने शानदार चौका मारा"
```

Document:

Input → Transformation → Output

---

# 9. PREPROCESSING STEP 2 — TEXT CLEANING

Remove:

- Unnecessary symbols.
- URLs.
- HTML artifacts.
- Broken encoding.
- Excessive punctuation.

Do not remove meaningful cricket symbols before analysis.

Example:

```text
"4 runs!!!"

↓

"4 runs"
```

---

# 10. PREPROCESSING STEP 3 — LANGUAGE IDENTIFICATION

For each record assign:

```text
hi
mr
en
code_mixed_hi_en
code_mixed_mr_en
```

Store:

```text
detected_language

language_confidence

is_code_mixed
```

Evaluate language detection separately.

Metrics:

```text
Accuracy

Precision

Recall

F1 Score
```

---

# 11. PREPROCESSING STEP 4 — NUMBER NORMALIZATION

Normalize:

Hindi:

```text
चार → 4
छह → 6
```

Marathi:

```text
चार → 4
सहा → 6
```

English:

```text
four → 4
six → 6
```

Cricket meaning:

```text
4 → FOUR

6 → SIX
```

Preserve original text.

Store normalized representation separately.

---

# 12. PREPROCESSING STEP 5 — CRICKET VOCABULARY NORMALIZATION

Create:

```text
data/cricket_vocabulary.json
```

Example:

```json
{
    "FOUR": [
        "चौका",
        "चार रन",
        "फोर",
        "four"
    ],
    "SIX": [
        "छक्का",
        "सहा धावा",
        "सिक्स",
        "six"
    ],
    "WICKET": [
        "बाद",
        "आउट",
        "विकेट",
        "बाद झाला",
        "out"
    ]
}
```

Use this vocabulary as a documented domain-specific preprocessing resource.

---

# 13. PREPROCESSING STEP 6 — PLAYER NAME NORMALIZATION

Player names may appear in multiple forms.

Example:

```text
विराट

कोहली

विराट कोहली

Virat

Virat Kohli
```

Map to:

```text
Virat Kohli
```

Use:

- Player dictionary.
- Alias mapping.
- Fuzzy matching.

Create:

```text
data/player_aliases.json
```

---

# 14. PREPROCESSING STEP 7 — CODE-MIXED TEXT

Examples:

```text
"Virat ne शानदार four maara"
```

```text
"कोहलीने amazing six मारला"
```

Do not destroy code-mixed information.

Preserve:

```text
original_text
```

Create:

```text
normalized_text
```

Use multilingual models capable of handling mixed language.

---

# 15. PREPROCESSING REPORT

For every dataset preprocessing run generate:

```text
reports/preprocessing_report.json
```

Include:

```text
Original Records

Records Removed

Duplicates Removed

Missing Values Handled

Language Distribution

Normalization Operations

Final Dataset Size
```

This should be viewable during evaluation.

---

# 16. DATA ANNOTATION

Create:

```text
docs/annotation_guidelines.md
```

Define every event label.

Example:

## FOUR

The event is labelled FOUR if the commentary explicitly states that four runs were scored as a boundary.

## SIX

The event is labelled SIX if six runs were scored directly from the shot.

## WICKET

The event is labelled WICKET if a batter is dismissed.

Define all labels.

Recommended classification labels:

```text
FOUR

SIX

WICKET

DOT

SINGLE

DOUBLE

TRIPLE

WIDE

NO_BALL

FIFTY

CENTURY

OTHER
```

Avoid excessive labels initially.

A smaller, high-quality labelled dataset is better than a large unreliable one.

---

# 17. NLP TRAIN / VALIDATION / TEST SPLIT

Create:

```text
data/processed/nlp/

    train.csv

    validation.csv

    test.csv
```

Recommended split:

```text
Train: 70%

Validation: 15%

Test: 15%
```

Important:

Do not randomly split near-duplicate records into train and test.

Prefer splitting by:

```text
MATCH ID
```

where possible.

This prevents data leakage.

Document the split.

---

# 18. NLP MODEL

Implement a distinct trained NLP model.

Task:

# Cricket Commentary Event Classification

Input:

```text
Hindi or Marathi cricket commentary
```

Output:

```text
FOUR

SIX

WICKET

DOT

OTHER
```

Start with a baseline model.

---

# 19. NLP BASELINE MODEL

Implement:

```text
TF-IDF

+

Logistic Regression
```

This is important academically.

Evaluate:

```text
Accuracy

Precision

Recall

F1
```

Save results.

---

# 20. ADVANCED NLP MODEL

Fine-tune a multilingual transformer.

Recommended:

```text
XLM-RoBERTa
```

Task:

Multiclass cricket event classification.

Pipeline:

```text
Preprocessed Text

↓

Tokenizer

↓

XLM-R

↓

Classification Head

↓

Event Label
```

Train using:

```text
Training Set

↓

Validation

↓

Hyperparameter Selection

↓

Final Test Evaluation
```

Save:

```text
models/nlp/event_classifier/
```

---

# 21. NLP MODEL COMPARISON

This must be visible.

Create:

```text
reports/nlp_model_comparison.json
```

Compare:

| Model | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| TF-IDF + Logistic Regression | | | | |
| XLM-RoBERTa | | | | |

Do not fabricate values.

Generate them from actual testing.

---

# 22. NLP ENTITY EXTRACTION

Entity categories:

```text
PLAYER

TEAM

EVENT

CRICKET_TERM
```

Implement a hybrid approach:

```text
Dictionary Matching

+

Fuzzy Matching

+

Rule-based Patterns

+

Optional NER Model
```

Evaluate entity extraction.

Metrics:

```text
Precision

Recall

F1
```

---

# 23. NLP EVENT EXTRACTION

The NLP model predicts event type.

Rule-based logic extracts structured context.

Example:

```text
Input:

"बुमराहने कोहलीला शानदार यॉर्करवर बोल्ड केले"

Model Prediction:

WICKET

Rule Extraction:

Bowler = Bumrah

Batter = Kohli

Dismissal = Bowled
```

Structured output:

```json
{
    "event": "WICKET",
    "bowler": "Jasprit Bumrah",
    "batter": "Virat Kohli",
    "dismissal": "BOWLED"
}
```

Clearly explain:

```text
MODEL → EVENT CLASSIFICATION

RULE SYSTEM → STRUCTURED ATTRIBUTE EXTRACTION
```

---

# 24. NLP PIPELINE FINAL OUTPUT

Every processed commentary record should have:

```text
original_text

detected_language

language_confidence

normalized_text

tokens

entities

predicted_event

prediction_confidence

structured_event
```

This should be visible on:

```text
/nlp-explorer
```

---

# 25. INFORMATION RETRIEVAL DATASET

The IR system needs its own dataset.

Create:

```text
data/processed/ir/
```

Files:

```text
documents.jsonl

queries.json

qrels.json
```

---

# 26. IR DOCUMENT COLLECTION

Every document should contain:

```json
{
    "document_id": "M001_C_018",
    "content": "Virat Kohli scored a boundary through cover.",
    "language": "en",
    "match_id": "M001",
    "over": 18,
    "ball": 2,
    "players": ["Virat Kohli"],
    "event_type": "FOUR",
    "source": "commentary"
}
```

Documents should come from:

```text
Commentary

NLP Transcripts

Structured Events

Player Statistics

Match Summaries
```

Document creation must be a separate labelled stage.

---

# 27. IR PREPROCESSING

Create:

```text
backend/app/ir/preprocessing.py
```

Perform:

```text
Document Cleaning

Tokenization

Lowercasing where appropriate

Stopword handling

Metadata extraction
```

Do not blindly remove Hindi and Marathi stopwords without evaluating impact.

Maintain separate preprocessing for:

```text
Lexical Retrieval
```

and

```text
Semantic Retrieval
```

Semantic embedding models should generally receive cleaner natural text rather than aggressively stripped token sequences.

Document this distinction.

---

# 28. IR BASELINE

Implement:

# TF-IDF Retrieval

Create:

```text
ir/tfidf_search.py
```

This provides an academic baseline.

Evaluate it.

---

# 29. BM25 RETRIEVAL

Implement:

```text
ir/bm25_search.py
```

Pipeline:

```text
Documents

↓

Tokenization

↓

BM25 Index

↓

Query

↓

BM25 Score

↓

Ranked Documents
```

Store and load index.

---

# 30. SEMANTIC RETRIEVAL

Use a multilingual sentence embedding model.

Pipeline:

```text
Documents

↓

Multilingual Embedding Model

↓

Vector Embeddings

↓

FAISS Index

↓

Query Embedding

↓

Similarity Search

↓

Ranked Documents
```

The model must support:

```text
Hindi

Marathi

English
```

---

# 31. HYBRID RETRIEVAL

Combine:

```text
Lexical Score

+

Semantic Score
```

Use normalized scores.

Formula:

```text
Hybrid Score

=

α × BM25 Score

+

(1 − α) × Semantic Score
```

Make alpha configurable.

Example:

```text
α = 0.5
```

---

# 32. IR QUERY DATASET

Create:

```text
data/evaluation/ir_queries.json
```

Include queries in:

Hindi.

Marathi.

English.

Example:

```json
{
    "query_id": "Q001",
    "query": "कोहली ने कितने रन बनाए?",
    "language": "hi",
    "match_id": "M001"
}
```

---

# 33. RELEVANCE JUDGEMENTS

Create:

```text
data/evaluation/qrels.json
```

Example:

```json
{
    "query_id": "Q001",
    "relevant_documents": [
        "M001_STATS_KOHLI",
        "M001_C_018"
    ]
}
```

This is essential.

Without relevance judgments, proper IR evaluation is impossible.

---

# 34. IR EVALUATION

Evaluate:

```text
Precision@K

Recall@K

MRR

nDCG
```

Compare:

```text
TF-IDF

BM25

Semantic Search

Hybrid Search
```

Final comparison:

| Retrieval Model | Precision@5 | Recall@5 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|
| TF-IDF | | | | |
| BM25 | | | | |
| Semantic | | | | |
| Hybrid | | | | |

Metrics must be generated automatically.

---

# 35. CROSS-LINGUAL IR EXPERIMENT

This is a major academic experiment.

Use equivalent queries.

Example:

Hindi:

```text
कोहली ने कितने रन बनाए?
```

Marathi:

```text
कोहलीने किती धावा केल्या?
```

English:

```text
How many runs did Kohli score?
```

Evaluate whether the same relevant document appears in top K.

Document results.

---

# 36. RAG SYSTEM

The RAG system must NOT create a separate hidden retrieval pipeline.

It must consume:

```text
HYBRID IR RESULTS
```

Pipeline:

```text
USER QUESTION

↓

LANGUAGE DETECTION

↓

QUERY PREPROCESSING

↓

HYBRID RETRIEVAL

↓

TOP-K DOCUMENTS

↓

CONTEXT CONSTRUCTION

↓

LLM

↓

ANSWER
```

The response must include:

```text
Answer

Retrieved Documents

Scores

Metadata

Timeline References
```

---

# 37. RAG GROUNDING

Implement source grounding.

The LLM should receive:

```text
ONLY RETRIEVED CONTEXT
```

If the answer is not present:

```text
"I could not find sufficient evidence in the available match data."
```

Do not allow unsupported statistics.

---

# 38. PROJECT FOLDER STRUCTURE

Final project structure:

```text
ballriq/

├── backend/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       │
│       ├── nlp/
│       │   ├── preprocessing/
│       │   ├── models/
│       │   ├── entity_extraction/
│       │   ├── event_extraction/
│       │   └── pipeline.py
│       │
│       ├── ir/
│       │   ├── preprocessing.py
│       │   ├── tfidf_search.py
│       │   ├── bm25_search.py
│       │   ├── semantic_search.py
│       │   ├── hybrid_search.py
│       │   └── evaluation.py
│       │
│       └── rag/
│
├── frontend/
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   ├── annotations/
│   └── evaluation/
│
├── models/
│   └── nlp/
│
├── notebooks/
│   ├── 01_dataset_exploration.ipynb
│   ├── 02_preprocessing_analysis.ipynb
│   ├── 03_nlp_model_training.ipynb
│   └── 04_ir_evaluation.ipynb
│
├── scripts/
│   ├── validate_dataset.py
│   ├── preprocess_data.py
│   ├── train_nlp_model.py
│   ├── build_ir_index.py
│   └── evaluate_all.py
│
├── reports/
│   ├── data_quality/
│   ├── preprocessing/
│   ├── nlp/
│   └── ir/
│
├── docs/
│   ├── dataset_documentation.md
│   ├── annotation_guidelines.md
│   ├── nlp_methodology.md
│   ├── ir_methodology.md
│   └── system_architecture.md
│
└── tests/
```

---

# 39. ACADEMIC UI PAGES

In addition to the main cricket platform, create dedicated demonstration pages.

---

## /dataset-explorer

Show:

```text
Dataset Name

Dataset Source

Number of Records

Language Distribution

Event Distribution

Class Distribution

Sample Records

Missing Data Report
```

---

## /preprocessing-explorer

Allow selecting a record.

Show:

```text
RAW TEXT

↓

UNICODE NORMALIZATION

↓

TEXT CLEANING

↓

LANGUAGE DETECTION

↓

NUMBER NORMALIZATION

↓

CRICKET TERM NORMALIZATION

↓

PLAYER NORMALIZATION

↓

FINAL PREPROCESSED TEXT
```

This should be visually step-by-step.

---

## /nlp-explorer

Show:

```text
Input Text / Audio

↓

Language Detection

↓

Transcription

↓

Preprocessing

↓

Entity Extraction

↓

NLP Event Classification Model

↓

Structured Event
```

Display model confidence.

---

## /ir-explorer

Show four retrieval methods side-by-side:

```text
TF-IDF

BM25

Semantic Search

Hybrid Search
```

For every query show:

```text
Rank

Document

Score

Metadata
```

---

## /evaluation

Show:

### Dataset

Records.

Languages.

Class distribution.

### NLP

Baseline vs Transformer.

Accuracy.

Precision.

Recall.

F1.

### IR

TF-IDF.

BM25.

Semantic.

Hybrid.

Precision@K.

Recall@K.

MRR.

nDCG.

All metrics must come from generated report files.

---

# 40. FINAL TEACHER EXPLANATION FLOW

The application must allow us to explain the project in exactly this order:

## STEP 1 — DATASET

"What data are you using?"

Show:

```text
/dataset-explorer
```

Explain:

Structured match data.

Hindi commentary.

Marathi commentary.

Audio.

Annotations.

---

## STEP 2 — PREPROCESSING

"How did you preprocess the data?"

Show:

```text
/preprocessing-explorer
```

Explain every transformation.

---

## STEP 3 — NLP

"What NLP technique/model did you use?"

Show:

```text
/nlp-explorer
```

Explain:

Language Detection.

Normalization.

Entity Extraction.

Event Classification.

Baseline Model.

Transformer Model.

Metrics.

---

## STEP 4 — INFORMATION RETRIEVAL

"Where is IR?"

Show:

```text
/ir-explorer
```

Explain:

TF-IDF.

BM25.

Vector Embeddings.

FAISS.

Semantic Search.

Hybrid Ranking.

---

## STEP 5 — EVALUATION

"How did you evaluate it?"

Show:

```text
/evaluation
```

Explain:

NLP metrics.

IR metrics.

Model comparison.

---

## STEP 6 — FINAL PRODUCT

Open:

```text
/matches/{id}
```

Show:

Match UI.

Timeline.

Commentary.

Stats.

Ask BALLRIQ.

---

# 41. FINAL DEVELOPMENT RULE

Do not skip directly from:

```text
DATA → LLM
```

The project must demonstrate the full academic pipeline:

```text
DATASET
↓
DATA VALIDATION
↓
EDA
↓
PREPROCESSING
↓
TRAIN/VALIDATION/TEST SPLIT
↓
BASELINE NLP MODEL
↓
ADVANCED NLP MODEL
↓
MODEL EVALUATION
↓
DOCUMENT CREATION
↓
TF-IDF BASELINE
↓
BM25
↓
SEMANTIC RETRIEVAL
↓
HYBRID RETRIEVAL
↓
IR EVALUATION
↓
RAG
↓
FINAL APPLICATION
```

Every arrow in this architecture must correspond to actual implemented code and not merely a diagram.

---

# SUCCESS CRITERIA

The project is complete only when a teacher can independently verify:

### Dataset

[ ] Raw dataset exists.

[ ] Dataset sources are documented.

[ ] Dataset statistics are available.

[ ] Data quality checks exist.

### Preprocessing

[ ] Each preprocessing step is labelled.

[ ] Raw and processed data are preserved separately.

[ ] Preprocessing reports exist.

### NLP

[ ] A baseline model exists.

[ ] A trained multilingual NLP model exists.

[ ] Train/validation/test data exists.

[ ] NLP metrics are generated.

[ ] Entity/event extraction works.

### IR

[ ] TF-IDF baseline works.

[ ] BM25 works.

[ ] Semantic retrieval works.

[ ] FAISS index works.

[ ] Hybrid retrieval works.

[ ] Query relevance judgments exist.

[ ] IR metrics are generated.

### RAG

[ ] RAG uses Hybrid IR.

[ ] Sources are visible.

[ ] Unsupported questions are handled safely.

### Frontend

[ ] Main cricket platform works.

[ ] Dataset Explorer works.

[ ] Preprocessing Explorer works.

[ ] NLP Explorer works.

[ ] IR Explorer works.

[ ] Evaluation Dashboard works.

---

# ABSOLUTE RULE

This must look and behave like two legitimate academic systems integrated into one product:

# SYSTEM 1

## Multilingual Cricket NLP System

```text
Hindi / Marathi Audio or Text
        ↓
Language Detection
        ↓
Preprocessing
        ↓
Entity Extraction
        ↓
Trained Event Classification Model
        ↓
Structured Cricket Events
```

# SYSTEM 2

## Cricket Information Retrieval System

```text
Cricket Documents
        ↓
TF-IDF
        ↓
BM25
        ↓
Multilingual Embeddings
        ↓
FAISS Vector Search
        ↓
Hybrid Ranking
        ↓
Relevant Documents
```

# INTEGRATION

```text
NLP OUTPUT
    ↓
CRICKET KNOWLEDGE BASE
    ↓
INFORMATION RETRIEVAL
    ↓
RAG
    ↓
CRICBHASHA
```

The main product should look like a professional cricket intelligence platform, while the underlying academic pages make the NLP and Information Retrieval work transparent, measurable, and easy to explain during project evaluation.