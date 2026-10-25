# BALLRIQ

**A multilingual cricket intelligence and retrieval platform**

BALLRIQ brings cricket match data, multilingual commentary processing,
search, question answering, and analytics into one application. Built
with **React** and **FastAPI**, it is designed to help developers and
researchers explore how raw cricket commentary can be transformed into
structured events, searchable documents, evidence-backed answers, and
match-level insights.

The project supports **English, Hindi, Marathi, and selected code-mixed
commentary**.

## Features

-   **Match Center:** Explore matches, innings, scorecards, players,
    statistics, commentary, and extracted event counts.
-   **Dataset Explorer:** Inspect available dataset records and
    commentary.
-   **Preprocessing:** Follow the multilingual text-processing pipeline,
    including Unicode normalization, language detection, cricket-term
    and player-name normalization, and tokenization.
-   **NLP:** Classify cricket events and extract cricket entities and
    events. A trained classifier is used when compatible model files are
    available; otherwise, the application falls back to rule-based
    processing.
-   **Information Retrieval (IR):** Search commentary using TF-IDF,
    BM25, semantic, or hybrid retrieval, depending on which index assets
    are available.
-   **Grounded question answering (RAG):** Retrieve relevant commentary
    before answering and return supporting source references. If no LLM
    provider is configured, BALLRIQ uses deterministic evidence
    synthesis.
-   **Big Data Analytics (BDA):** Query Parquet-based analytical data
    with DuckDB, explore phase analytics and leaderboards, and inspect
    simulated streaming metrics.
-   **Evaluation Dashboard:** View dataset, preprocessing, NLP, and IR
    reports when generated reports are available.
-   **Transcript analysis:** Analyze a supplied transcript. Acoustic
    speech-to-text is not installed by default.

> **Project status:** BALLRIQ is a developer-oriented demo. Some
> features depend on datasets, generated reports, trained models,
> semantic indexes, or Parquet files that may not be included in a fresh
> clone. The streaming analytics view simulates event flow from stored
> data; it is not a live cricket feed.

## How it works

1.  The React/Vite frontend sends API requests to the FastAPI backend.
2.  FastAPI routes requests to the match, NLP, IR, RAG, evaluation,
    audio, and BDA modules.
3.  The NLP pipeline prepares commentary for classification,
    entity/event extraction, and retrieval.
4.  The retrieval layer searches prepared documents with lexical,
    semantic, or hybrid methods, depending on the available assets.
5.  The RAG module retrieves relevant commentary and uses that evidence
    to produce an answer with source references.
6.  Match data is stored in SQLite, while analytical queries run against
    generated Parquet files through DuckDB.

## System architecture

``` text
┌──────────────────────────┐       /api/*       ┌──────────────────────────┐
│ React 19 + Vite frontend │ ─────────────────> │ FastAPI backend          │
│ frontend/src/            │                    │ backend/app/             │
└──────────────────────────┘                    └────────────┬─────────────┘
                                                             │
                         ┌───────────────────────────────────┼────────────────────┐
                         │                                   │                    │
                  ┌──────▼──────┐                     ┌──────▼──────┐     ┌───────▼──────┐
                  │ SQLite      │                     │ IR indexes  │     │ Parquet lake │
                  │ data/       │                     │ models/ir/  │     │ data/lake/   │
                  │ ballriq.db  │                     │              │     │ DuckDB       │
                  └─────────────┘                     └─────────────┘     └──────────────┘
                  Match and commentary                TF-IDF, BM25,       Analytics and
                  records and audio metadata          semantic, hybrid    stream simulation
```

## Repository structure

``` text
BALLRIQ/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routes and request/response handling
│   │   ├── audio/            # Transcript and audio-related services
│   │   ├── bda/              # DuckDB analytics and stream simulation
│   │   ├── core/             # Configuration and dependencies
│   │   ├── db/               # Database models, access, and seeding
│   │   ├── ir/               # Retrieval methods and evaluation metrics
│   │   ├── nlp/              # Preprocessing, extraction, and classifiers
│   │   └── rag/              # Evidence-first question answering
│   └── tests/                # Backend tests
├── frontend/
│   └── src/
│       ├── components/       # Shared React components
│       └── pages/            # Main application views
├── scripts/                  # Data preparation, indexing, training, and evaluation
├── data/
│   ├── raw/                  # Source CSV and JSONL files
│   ├── interim/              # Cleaned and normalized data
│   ├── processed/            # Prepared datasets and IR documents
│   ├── annotations/          # Event labels
│   └── lake/                 # Generated Parquet tables
├── models/                   # Optional trained models and retrieval indexes
├── reports/                  # Generated data-quality, NLP, and IR reports
├── docs/                     # Architecture, methodology, dataset, and annotation docs
├── requirements.txt          # Python dependencies
└── README.md
```

Some directories or generated assets may not exist until the relevant
preparation scripts have been run.

## Technology stack

-   **Frontend:** React 19, Vite
-   **Backend:** Python, FastAPI
-   **Database:** SQLite with SQLAlchemy and asynchronous database
    access
-   **Information retrieval:** TF-IDF, BM25, semantic retrieval, and
    hybrid retrieval
-   **Analytics:** DuckDB and Parquet
-   **NLP:** Multilingual preprocessing, event classification, entity
    extraction, and rule-based fallback
-   **Question answering:** Retrieval-augmented generation (RAG), with
    optional OpenAI-compatible text generation
-   **Testing:** Pytest and the frontend production build

## Requirements

Before running BALLRIQ, install:

-   Python 3.10 or newer, compatible with the packages in
    `requirements.txt`
-   Node.js and npm compatible with the Vite version in
    `frontend/package.json`
-   The source data required for database seeding and any assets needed
    by the features you want to use

Semantic search, hybrid retrieval, RAG, trained NLP inference, and BDA
analytics may require additional model/index files or generated data.
These may need to be obtained or created separately.

## Run locally

Run the backend commands from the repository root. The frontend runs in
a separate terminal.

### 1. Create a Python environment and install dependencies

**Windows PowerShell**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS/Linux**

``` bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Check that the raw data is present

The database seeder expects these files:

``` text
data/raw/matches/matches.csv
data/raw/matches/players.csv
data/raw/matches/innings.csv
data/raw/matches/batting_stats.csv
data/raw/matches/bowling_stats.csv
data/raw/player_data/player_profiles.csv
data/raw/commentary/commentary.jsonl
data/raw/audio/audio_metadata.jsonl
```

If these files are not present, obtain or prepare the required source
data before running the seeder.

### 3. Seed the local database

From the repository root, run:

``` bash
python -m backend.app.db.seed
```

**Important:** The seeder drops and recreates the local database tables
before loading the data. Back up any local database changes you need
before running it.

The database is created at `data/ballriq.db` by default, subject to your
configuration.

### 4. Start the backend API

From the repository root:

``` bash
python -m uvicorn backend.app.main:app --reload
```

The API should be available at:

-   API root: `http://localhost:8000/`
-   Interactive API documentation: `http://localhost:8000/docs`
-   OpenAPI schema: `http://localhost:8000/openapi.json`

### 5. Install frontend dependencies and start the UI

Open a second terminal:

``` bash
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`. The
frontend's Vite configuration proxies `/api` requests to
`http://127.0.0.1:8000`.

### 6. Build the frontend for production

From the `frontend/` directory:

``` bash
npm run build
npm run preview
```

## Prepare datasets, indexes, and analytics assets

These steps are optional and depend on the features you want to use. Run
the commands from the repository root.

### Build information-retrieval documents and indexes

``` bash
python scripts/build_ir_documents.py
python scripts/build_ir_indices.py
```

TF-IDF and BM25 can work with the prepared document corpus. Semantic
search, hybrid search, method comparison, and RAG require a compatible
semantic index under `models/ir/`. If the required semantic index is
missing or stale, semantic endpoints may return HTTP 503.

### Build the analytics lake

``` bash
python scripts/bda_generate_lake.py
```

BDA endpoints expect Parquet assets under `data/lake/`, including match,
commentary, player, batting, bowling, and ball-event tables.

### Train or evaluate NLP models

Useful scripts include:

``` bash
python scripts/train_nlp_baseline.py
python scripts/train_xlmr.py
python scripts/validate_dataset.py
python scripts/split_dataset.py
python scripts/evaluate_ir.py
python scripts/generate_ground_truth_qrels.py
```

Check each script's source for required input files and supported
options before running it.

The NLP router looks for a compatible XLM-R event-classifier artifact
under `models/nlp/event_classifier_xlmr/`. If it is unavailable, the
router tries the baseline artifact under
`models/nlp/event_classifier_baseline/`. If neither model is usable,
event classification falls back to the preprocessing and rule-based
pipeline.

## Configuration

Application settings are defined in `backend/app/core/config.py` and can
be overridden through a root-level `.env` file.

Common settings include:

``` dotenv
DATABASE_URL=sqlite+aiosqlite:///D:/path/to/data/ballriq.db
MODEL_DIR=./models
DATA_DIR=./data
HOST=0.0.0.0
PORT=8000
```

Use a database path appropriate for your operating system. Do not commit
secrets or local environment files to source control.

### Optional LLM-backed RAG

To enable an OpenAI-compatible generation provider, configure:

``` dotenv
OPENAI_API_KEY=your-key
OPENAI_MODEL=your-model
OPENAI_BASE_URL=https://api.openai.com/v1
```

The provider is used only when both `OPENAI_API_KEY` and `OPENAI_MODEL`
are set. Without them, the application uses deterministic evidence
synthesis. Keep API keys private and never commit them.

## API overview

FastAPI generates the full interactive API reference at
`http://localhost:8000/docs`.

  -----------------------------------------------------------------------
  Route prefix                        Purpose
  ----------------------------------- -----------------------------------
  `/api/matches`                      Match lists and details, innings,
                                      commentary filters, event counts,
                                      statistics, and players

  `/api/nlp`                          Preprocessing, classification,
                                      entity extraction, and pipeline
                                      metadata

  `/api/ir`                           Search, retrieval-method
                                      comparison, evaluation, and
                                      document statistics

  `/api/rag`                          Evidence-grounded answers and
                                      suggested questions

  `/api/bda`                          Parquet analytics, leaderboards,
                                      read-only analytical SQL, and
                                      simulated stream metrics

  `/api/evaluation`                   Dataset, preprocessing, NLP, IR,
                                      and combined evaluation summaries

  `/api/audio`                        Audio metadata, supplied-transcript
                                      analysis, and transcription
                                      capability status
  -----------------------------------------------------------------------

### Example requests

Fetch the matches endpoint:

``` bash
curl http://localhost:8000/api/matches/
```

Preprocess a short multilingual commentary sample:

``` bash
curl -X POST http://localhost:8000/api/nlp/preprocess \
  -H "Content-Type: application/json" \
  -d '{"text":"Kohli ने चौका लगाया"}'
```

Search commentary with BM25:

``` bash
curl -X POST http://localhost:8000/api/ir/search \
  -H "Content-Type: application/json" \
  -d '{"query":"powerplay wicket","method":"bm25","top_k":5}'
```

Ask a question using RAG:

``` bash
curl -X POST http://localhost:8000/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Who was the top scorer?","language":"en"}'
```

## Important behavior and limitations

### Grounded question answering

The `/api/rag/ask` endpoint retrieves commentary through the hybrid
retriever before generating an answer. Responses include fields such as
`answer`, `confidence`, `is_grounded`, `generation`, `citations`,
`sources`, and `retrieved_context_count`.

When the retrieved evidence does not meet the required threshold, the
system is designed to return an insufficient-evidence response rather
than invent an answer. RAG requires the appropriate retrieval assets and
configuration.

### Audio and transcription

The `/api/audio/analyze` endpoint accepts a supplied transcript and runs
the available NLP processing. Acoustic speech-to-text is not installed
by default. The `/api/audio/transcribe` endpoint may return HTTP 503
when no eligible transcription provider or supported transcript sidecar
is available.

### Big Data Analytics

The `/api/bda/query` endpoint is intended for read-only analytical SQL
over the Parquet lake. Use trusted queries during local development. Do
not expose this endpoint publicly without adding authentication and
appropriate query restrictions.

### Demo data and generated assets

Some tests, dashboards, and sample figures depend on generated data,
reports, trained models, indexes, or Parquet outputs. Some displayed
sample figures may be demo values; check the underlying inputs before
presenting them as benchmark results.

## Tests and verification

Run backend tests from the repository root:

``` bash
python -m pytest
```

Build the frontend:

``` bash
cd frontend
npm ci
npm run build
```

For a quick backend smoke check, start the API and run:

``` bash
curl http://localhost:8000/
curl http://localhost:8000/docs
```

If tests or dashboard pages depend on missing generated assets, run the
relevant preparation script first. Where documented, fallback behavior
may be expected when an optional model or index is unavailable.

## Documentation

Project documentation is available in the `docs/` directory:

-   [System architecture](docs/architecture/system_architecture.md)
-   [NLP methodology](docs/nlp/nlp_methodology.md)
-   [Information retrieval methodology](docs/ir/ir_methodology.md)
-   [Dataset documentation](docs/dataset/dataset_documentation.md)
-   [Annotation guidelines](docs/dataset/annotation_guidelines.md)

## Contributing and development notes

When making changes to BALLRIQ:

-   Keep API paths and response formats in sync with the relevant
    routers and schemas.
-   Add or update focused tests when changing backend behavior.
-   Run the backend tests and frontend production build before opening a
    pull request.
-   Prefer regenerating local datasets, indexes, and reports over
    committing machine-specific outputs, unless they are needed for
    reproducibility.
-   Confirm redistribution rights before sharing datasets, model
    checkpoints, indexes, or generated data.
-   Never commit API keys, passwords, or other secrets.

------------------------------------------------------------------------

BALLRIQ is built to make multilingual cricket commentary easier to
explore, search, and analyze---from raw text to evidence-backed answers
and structured match insights.
