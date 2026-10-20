# BALLRIQ

BALLRIQ is a multilingual cricket intelligence workbench. It combines match exploration, commentary preprocessing, cricket event and entity extraction, information retrieval, grounded question answering, evaluation reports, and analytical queries in one React + FastAPI application.

The project is designed for English, Hindi, Marathi, and selected code-mixed cricket commentary. It is useful for inspecting the full path from raw commentary to searchable documents, model predictions, evidence-backed answers, and aggregate cricket analytics.

## What the application provides

- **Match Center** — Browse matches, innings, scorecards, players, statistics, commentary, and extracted event counts.
- **Dataset** — Inspect dataset-oriented views and commentary records.
- **Preprocessing** — Run and inspect the multilingual preprocessing pipeline step by step.
- **NLP** — Classify cricket events and extract cricket entities and events.
- **BDA** — Query Parquet-backed lakehouse data with DuckDB, view phase analytics and leaderboards, and inspect simulated streaming metrics.
- **IR** — Search commentary with TF-IDF, BM25, semantic, or hybrid retrieval; compare methods and evaluate results.
- **Evaluation Dashboard** — View dataset, preprocessing, NLP, and IR reports when generated reports are available.
- **Grounded RAG** — Retrieve commentary evidence first, then answer questions from that evidence with citations. An optional OpenAI-compatible provider can generate the answer; otherwise a deterministic evidence synthesis is returned.
- **Audio analysis** — Analyze an explicitly supplied transcript. Acoustic speech-to-text is not installed by default.
<<<<<<< HEAD
=======
BALLRIQ is a developer-oriented demo for exploring multilingual cricket commentary. It combines text preprocessing, event and entity extraction, information retrieval, retrieval-backed question answering, match data, and analytics in one React and FastAPI application. Hindi, Marathi, English, and selected code-mixed commentary are in scope.

## What it does

- **Explore matches:** Browse match, innings, player, scorecard, and commentary data.
- **Process commentary:** Normalize Unicode and text, detect language, normalize cricket terminology and player names, and tokenize text.
- **Analyze language:** Extract cricket events and entities; use an available trained classifier where configured, with a rule-based fallback.
- **Search commentary:** Compare lexical TF-IDF and BM25 retrieval with semantic and hybrid retrieval when their data and index assets are available.
- **Ask questions:** Retrieve relevant commentary and return evidence-linked answers. A deterministic response fallback is used unless an LLM provider is configured.
- **Analyze data:** Query match and ball-event aggregates from Parquet using DuckDB. The streaming analytics endpoint simulates event flow from stored data; it is not a live feed.

## How it works

1. The React/Vite frontend sends requests to the FastAPI backend.
2. The backend routes requests to focused NLP, IR, RAG, match, evaluation, audio, and BDA modules.
3. NLP preprocessing prepares commentary for classification, extraction, and retrieval.
4. IR searches prepared documents using lexical, semantic, or hybrid strategies, depending on available index assets.
5. RAG uses hybrid retrieval and returns source references with its answer; semantic index is required for RAG and method comparison.
6. Match records are stored in SQLite; analytical queries use generated Parquet files through DuckDB.
=======
>>>>>>> a5dfa9f (frontend, readme.md and backend updates)

## Architecture

```text
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> a5dfa9f (frontend, readme.md and backend updates)
┌──────────────────────┐       /api/*        ┌─────────────────────────┐
│ React 19 + Vite UI   │ ──────────────────> │ FastAPI application      │
│ frontend/src/        │                     │ backend/app/             │
└──────────────────────┘                     └───────────┬─────────────┘
                                                         │
                 ┌───────────────────────────────────────┼────────────────────┐
                 │                                       │                    │
           SQLite database                         IR indexes          Parquet lake
           data/ballriq.db                         models/ir/           data/lake/
                 │                                       │                    │
           Match/commentary                      TF-IDF, BM25,       DuckDB OLAP and
           and audio metadata                    semantic, hybrid   stream simulation
```

### Backend modules

- `backend/app/api/` — FastAPI routers and request/response handling.
- `backend/app/db/` — SQLAlchemy models, async database access, and the destructive local seed command.
- `backend/app/nlp/` — preprocessing, language detection, normalization, tokenization, event extraction, entity extraction, and classifiers.
- `backend/app/ir/` — document loading, TF-IDF, BM25, semantic, hybrid retrieval, and retrieval metrics.
- `backend/app/rag/` — evidence-first multilingual question answering.
- `backend/app/bda/` — DuckDB lakehouse analytics and simulated streaming metrics.
- `backend/app/audio/` — metadata and transcript analysis services.
- `backend/app/core/` — environment-backed application settings.

### Frontend modules

`frontend/src/App.jsx` maps the navigation tabs to these pages:

| Tab | Component | Main purpose |
| --- | --- | --- |
| Matches | `MatchCenter.jsx` | Match and commentary exploration |
| News | `DatasetExplorer.jsx` | Dataset inspection |
| Teams | `PreprocessingExplorer.jsx` | Preprocessing pipeline |
| Players | `NLPExplorer.jsx` | NLP classification and extraction |
| Leagues | `BDAExplorer.jsx` | Lakehouse and aggregate analytics |
| Stats | `IRExplorer.jsx` | Search and retrieval evaluation |
| More | `EvaluationDashboard.jsx` | Evaluation summaries |

The tab labels are product-oriented and do not exactly match the internal page filenames.

## Repository layout

```text
backend/
  app/
    api/                  FastAPI routers
    audio/                Transcript/audio services
    bda/                  DuckDB analytics and stream simulation
    core/                 Settings and dependencies
    db/                   Database models, access, and seeding
    ir/                   Retrieval implementations and metrics
    nlp/                  NLP pipeline, extraction, and models
    rag/                  Grounded question-answering engine
  tests/                  Pytest tests
frontend/
  src/
    components/           Shared React components
    pages/                Product views
scripts/                  Dataset, preprocessing, index, training, and evaluation jobs
data/
  raw/                    Source CSV and JSONL files
  interim/                Cleaned, normalized, and language-labelled data
  processed/              Train/validation/test data and IR documents
  annotations/            Event labels
  lake/                   Generated Parquet tables
models/                   Optional trained NLP models and IR indexes
reports/                  Generated data-quality, NLP, and IR reports
docs/                     Architecture, methodology, dataset, and annotation docs
requirements.txt          Python dependencies
frontend/package.json     JavaScript dependencies and Vite commands
<<<<<<< HEAD
=======
backend/app/       FastAPI routes and NLP, IR, RAG, database, BDA modules
backend/tests/     Backend tests
frontend/src/      React/Vite user interface
scripts/           Data preparation, index/model building, evaluation
data/              Raw inputs and generated local data
models/            Optional trained models and retrieval indexes
docs/              Architecture, methodology, and dataset documentation
>>>>>>> ef74100db53296feb09a213ac4fcb0a2d664dcbc
=======
>>>>>>> a5dfa9f (frontend, readme.md and backend updates)
```

## Prerequisites

- Python 3.10+ with a virtual environment.
- Node.js and npm compatible with the Vite version in `frontend/package.json`.
- Source data under `data/raw/` if rebuilding the database or generated assets.
- Optional: model and index artifacts for semantic search and trained NLP inference.

Large datasets, model checkpoints, indexes, and generated lake files may be absent in a fresh clone or may be managed separately. Confirm redistribution rights before publishing or sharing them.

## Run locally

Run commands from the repository root.

### 1. Install backend dependencies

PowerShell:
<<<<<<< HEAD
=======
- Python with versions supported by dependencies in `requirements.txt`
- Node.js and npm compatible with the Vite version in `frontend/package.json`
- Raw dataset files for database seeding and document/index generation

The repository may not include the data, trained models, semantic indexes, or Parquet outputs required by every feature. Obtain or generate those assets separately. Confirm data and model redistribution rights before sharing them.

## Run locally

Run commands from the repository root unless noted. On Windows PowerShell:

### 1. Install Python dependencies and seed local database
=======
>>>>>>> a5dfa9f (frontend, readme.md and backend updates)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Prepare the local database

```bash
python -m backend.app.db.seed
```

The seeder reads:

- `data/raw/matches/matches.csv`
- `data/raw/matches/players.csv`
- `data/raw/matches/innings.csv`
- `data/raw/matches/batting_stats.csv`
- `data/raw/matches/bowling_stats.csv`
- `data/raw/player_data/player_profiles.csv`
- `data/raw/commentary/commentary.jsonl`
- `data/raw/audio/audio_metadata.jsonl`

It recreates tables in `data/ballriq.db` before loading data. Back up any local database changes before running it again.

### 3. Start the API

```bash
python -m uvicorn backend.app.main:app --reload
```

- API root: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### 4. Start the frontend

In a second terminal:
=======
> **Warning:** Seeding drops and recreates the local database tables before loading data. Back up any local database contents you need before running it again.

The seeder expects raw files under `data/raw/`, including match CSV files, `commentary/commentary.jsonl`, and `audio/audio_metadata.jsonl`.

### 2. Start the backend

In the same terminal, from repository root:

<<<<<<< HEAD
```powershell
python -m uvicorn backend.app.main:app --reload
```

Backend: `http://localhost:8000`  
Interactive API docs: `http://localhost:8000/docs`

### 3. Start the frontend

Open a second terminal:

=======
>>>>>>> a5dfa9f (frontend, readme.md and backend updates)
```bash
cd frontend
npm ci
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`. Vite proxies `/api` requests to `http://127.0.0.1:8000` as configured in `frontend/vite.config.js`.
<<<<<<< HEAD
=======
Open the Vite URL shown in the terminal, usually `http://localhost:5173`.
>>>>>>> ef74100db53296feb09a213ac4fcb0a2d664dcbc
=======
>>>>>>> a5dfa9f (frontend, readme.md and backend updates)

Production frontend build:

```bash
cd frontend
npm run build
npm run preview
```

## Data and model pipeline
<<<<<<< HEAD
=======
## Data and model preparation

The database seeder loads match, player, innings, statistics, commentary, and audio metadata from `data/raw/` into `data/ballriq.db`.

To prepare IR data and indexes when raw source data is available, run from the repository root:

```powershell
python scripts/build_ir_documents.py
python scripts/build_ir_indices.py
```

TF-IDF and BM25 search can run without a semantic index. Semantic search, hybrid search, the method-comparison endpoint, and RAG require a compatible semantic index. BDA endpoints require Parquet assets under `data/lake/`; `scripts/bda_generate_lake.py` builds the local lake from prepared data. Learned NLP classification requires compatible model artifacts; otherwise, a fallback is used.

## Configuration

Application settings are defined in `backend/app/core/config.py` and may be overridden through a local `.env` file. Main settings include `DATABASE_URL`, `MODEL_DIR`, `DATA_DIR`, `HOST`, and `PORT`. Do not commit secrets.

For LLM-backed RAG, the engine reads `OPENAI_API_KEY`, `OPENAI_MODEL`, and optionally `OPENAI_BASE_URL`. Without a configured provider, the application uses its deterministic answer fallback.

## Tests and frontend build

From the repository root:

=======

>>>>>>> a5dfa9f (frontend, readme.md and backend updates)
The intended data flow is:

```text
raw CSV/JSONL
    │
    ├─ python -m backend.app.db.seed ──> SQLite match database
    │
    ├─ preprocessing scripts ──────────> data/interim/
    │
    ├─ scripts/build_ir_documents.py ──> data/processed/ir/documents.jsonl
    │
    ├─ scripts/build_ir_indices.py ────> models/ir/
    │
    ├─ scripts/bda_generate_lake.py ───> data/lake/*.parquet
    │
    └─ training/evaluation scripts ────> models/ and reports/
```

### Build IR documents and indexes

```bash
python scripts/build_ir_documents.py
python scripts/build_ir_indices.py
```

TF-IDF and BM25 use the document corpus. Semantic and hybrid search require a compatible semantic index under `models/ir/`. The IR router loads retrievers lazily on first request and returns HTTP 503 for semantic methods when the semantic index is unavailable or stale.

### Build the analytics lake

```bash
python scripts/bda_generate_lake.py
```

BDA endpoints expect Parquet assets under `data/lake/`, including match, commentary, player, batting, bowling, and ball-event tables.

### NLP model behavior

The NLP router prefers a compatible XLM-R artifact under `models/nlp/event_classifier_xlmr/`. If unavailable, it tries the baseline artifact under `models/nlp/event_classifier_baseline/`. If no usable classifier is available, event classification falls back to the preprocessing and rule-based pipeline.

Useful scripts include:

```bash
python scripts/train_nlp_baseline.py
python scripts/train_xlmr.py
python scripts/validate_dataset.py
python scripts/split_dataset.py
python scripts/evaluate_ir.py
python scripts/generate_ground_truth_qrels.py
```

Check each script's source for required input files and options before running it.

## Configuration

Settings live in `backend/app/core/config.py` and can be overridden through a root `.env` file. Important settings:

```dotenv
DATABASE_URL=sqlite+aiosqlite:///D:/path/to/data/ballriq.db
MODEL_DIR=./models
DATA_DIR=./data
HOST=0.0.0.0
PORT=8000
```

For optional OpenAI-compatible RAG generation:

```dotenv
OPENAI_API_KEY=your-key
OPENAI_MODEL=your-model
OPENAI_BASE_URL=https://api.openai.com/v1
```

The provider is used only when both `OPENAI_API_KEY` and `OPENAI_MODEL` are set. Without them, RAG uses deterministic evidence synthesis. Never commit `.env` files or API keys.

## API reference

FastAPI generates the complete interactive reference at `/docs`. Main route groups:

| Prefix | Endpoints provide |
| --- | --- |
| `/api/matches` | Match list/detail, innings, commentary filters, event counts, statistics, players |
| `/api/nlp` | `/preprocess`, `/classify`, `/entities`, pipeline metadata |
| `/api/ir` | Search, method comparison, method list, evaluation, document statistics |
| `/api/rag` | `/ask` grounded answers and suggested questions |
| `/api/bda` | Lake summary, phase analytics, multilingual metrics, top batters/bowlers, read-only SQL, simulated stream metrics |
| `/api/evaluation` | Dataset, preprocessing, NLP, IR, and combined evaluation summaries |
| `/api/audio` | Metadata, supplied-transcript analysis, transcription capability status |

Example requests:

```bash
curl http://localhost:8000/api/matches/

curl -X POST http://localhost:8000/api/nlp/preprocess \
  -H "Content-Type: application/json" \
  -d '{"text":"Kohli ने चौका लगाया"}'

curl -X POST http://localhost:8000/api/ir/search \
  -H "Content-Type: application/json" \
  -d '{"query":"powerplay wicket","method":"bm25","top_k":5}'

curl -X POST http://localhost:8000/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Who was the top scorer?","language":"en"}'
```

### RAG grounding contract

`/api/rag/ask` retrieves commentary through the hybrid retriever before generation. Responses include `answer`, `confidence`, `is_grounded`, `generation`, `citations`, `sources`, and `retrieved_context_count`. If no result meets the evidence threshold, the engine returns an insufficient-evidence response instead of inventing an answer.

### Audio limitation

`/api/audio/analyze` accepts a transcript and runs existing NLP processing. `/api/audio/transcribe` reports HTTP 503 unless a transcription provider is configured; the repository does not ship an acoustic speech-to-text model by default.

### BDA SQL limitation

`/api/bda/query` is intended for read-only analytical SQL over the Parquet lake. Only send trusted queries when developing locally, and do not expose this endpoint publicly without adding authentication and query restrictions.

## Tests and verification

Run backend tests from the repository root:

```bash
python -m pytest
```

<<<<<<< HEAD
<<<<<<< HEAD
Build the frontend:

```bash
cd frontend
=======
Build the frontend from `frontend/`:

```powershell
>>>>>>> ef74100db53296feb09a213ac4fcb0a2d664dcbc
=======
Build the frontend:

```bash
cd frontend
>>>>>>> a5dfa9f (frontend, readme.md and backend updates)
npm ci
npm run build
```

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> a5dfa9f (frontend, readme.md and backend updates)
For a focused API smoke check after starting the backend:

```bash
curl http://localhost:8000/
curl http://localhost:8000/docs
```

Some tests and dashboards depend on generated data, reports, model files, or indexes. If those assets are missing, run the relevant preparation script first and treat fallback responses as expected behavior where documented above.
<<<<<<< HEAD
=======
## API areas

| Prefix | Purpose |
| --- | --- |
| `/api/matches` | Match, innings, commentary, player, and statistics endpoints |
| `/api/nlp` | Preprocessing, classification, entity extraction, pipeline steps |
| `/api/ir` | Search, method comparison, evaluation, document statistics |
| `/api/rag` | Evidence-backed question answering and suggested questions |
| `/api/bda` | Parquet analytics, leaderboards, and SQL exploration |
| `/api/evaluation` | Dataset and NLP/IR evaluation summaries |
| `/api/audio` | Audio metadata and transcript analysis endpoints |

## Limitations

- Acoustic speech-to-text is not integrated. `/api/audio/transcribe` can use an eligible `.txt` transcript sidecar under the data directory; without one it returns HTTP 503.
- Semantic search and BDA require generated or separately obtained index and Parquet assets.
- Evaluation displays and sample dataset figures may include demo values; verify underlying inputs before treating them as benchmark results.
=======
>>>>>>> a5dfa9f (frontend, readme.md and backend updates)

## Documentation

- [System architecture](docs/architecture/system_architecture.md)
- [NLP methodology](docs/nlp/nlp_methodology.md)
- [IR methodology](docs/ir/ir_methodology.md)
- [Dataset documentation](docs/dataset/dataset_documentation.md)
- [Annotation guidelines](docs/dataset/annotation_guidelines.md)

## Development notes

- Keep API paths and response shapes documented in the router and schemas when changing them.
- Prefer generated assets over committing machine-specific outputs unless the project explicitly needs them for reproducibility.
- Keep secrets out of source control.
- Add or update a focused test when changing backend behavior.
- Validate both `python -m pytest` and `npm run build` before opening a pull request.
<<<<<<< HEAD
=======
=======
>>>>>>> a5dfa9f (frontend, readme.md and backend updates)
