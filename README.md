# BALLRIQ

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

## Architecture

```text
backend/app/       FastAPI routes and NLP, IR, RAG, database, BDA modules
backend/tests/     Backend tests
frontend/src/      React/Vite user interface
scripts/           Data preparation, index/model building, evaluation
data/              Raw inputs and generated local data
models/            Optional trained models and retrieval indexes
docs/              Architecture, methodology, and dataset documentation
```

## Prerequisites

- Python with versions supported by dependencies in `requirements.txt`
- Node.js and npm compatible with the Vite version in `frontend/package.json`
- Raw dataset files for database seeding and document/index generation

The repository may not include the data, trained models, semantic indexes, or Parquet outputs required by every feature. Obtain or generate those assets separately. Confirm data and model redistribution rights before sharing them.

## Run locally

Run commands from the repository root unless noted. On Windows PowerShell:

### 1. Install Python dependencies and seed local database

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m backend.app.db.seed
```

> **Warning:** Seeding drops and recreates the local database tables before loading data. Back up any local database contents you need before running it again.

The seeder expects raw files under `data/raw/`, including match CSV files, `commentary/commentary.jsonl`, and `audio/audio_metadata.jsonl`.

### 2. Start the backend

In the same terminal, from repository root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

Backend: `http://localhost:8000`  
Interactive API docs: `http://localhost:8000/docs`

### 3. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open the Vite URL shown in the terminal, usually `http://localhost:5173`.

For macOS/Linux, activate the virtual environment with `source .venv/bin/activate`.

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

```powershell
python -m pytest
```

Build the frontend from `frontend/`:

```powershell
npm ci
npm run build
```

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

## Documentation

- [System architecture](docs/architecture/system_architecture.md)
- [NLP methodology](docs/nlp/nlp_methodology.md)
- [IR methodology](docs/ir/ir_methodology.md)
- [Dataset documentation](docs/dataset/dataset_documentation.md)
- [Annotation guidelines](docs/dataset/annotation_guidelines.md)
