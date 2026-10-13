# BALLRIQ

Multilingual cricket-commentary NLP and search demo for Hindi, Marathi, English, and code-mixed text.

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer
- Git

## Run locally

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m backend.app.db.seed
python -m uvicorn backend.app.main:app --reload
```

In a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. API docs: `http://localhost:8000/docs`.

For macOS/Linux, activate the virtual environment with `source .venv/bin/activate`.

## Tests and build

From repository root:

```powershell
python -m pytest
```

Frontend production build:

```powershell
cd frontend
npm ci
npm run build
```

## Project layout

```text
backend/app/       FastAPI API, NLP, IR, RAG, database, BDA
backend/tests/     Backend tests
frontend/src/      React/Vite interface
scripts/           Data processing, model/index building, evaluation
 data/             Raw inputs and generated local outputs
models/            Generated model and retrieval artifacts
 docs/             Architecture, NLP, IR, dataset documentation
 tests/            Additional tests
```

Generated outputs are not required in Git by default. The database seeder expects source files under `data/raw/`. Confirm you have permitted source data before sharing or distributing it. IR indexes can be rebuilt with `python scripts/build_ir_indices.py` after preparing `data/processed/ir/documents.jsonl` using the project's data pipeline.

## Configuration

Backend defaults are defined in `backend/app/core/config.py`. Optional `.env` values include `DATABASE_URL`, `MODEL_DIR`, `DATA_DIR`, `LLM_API_KEY`, `LLM_BASE_URL`, `HOST`, and `PORT`. Keep real credentials in local `.env`; never commit it. The default database is `data/ballriq.db`.

## Current limitations

- Audio transcription is not integrated; `/api/audio/transcribe` returns HTTP 503 unless an eligible transcript sidecar is provided.
- Large datasets, generated Parquet files, trained weights, and IR indexes are excluded from Git; some NLP/IR features may require generating or separately obtaining those assets.

## Documentation

- [System architecture](docs/architecture/system_architecture.md)
- [NLP methodology](docs/nlp/nlp_methodology.md)
- [IR methodology](docs/ir/ir_methodology.md)
- [Dataset documentation](docs/dataset/dataset_documentation.md)
- [Annotation guidelines](docs/dataset/annotation_guidelines.md)

## GitHub checklist

Commit maintained source, tests, documentation, scripts, dependency manifests, and lockfiles. Review raw datasets and annotations individually for size, privacy, provenance, and redistribution rights before adding them.

Do not commit `node_modules`, build output, Python caches/virtual environments, `.env` credentials, local databases, logs, generated intermediate/processed/lake data, or generated model/index binaries unless deliberately approved and needed. Use Git LFS or external hosting for assets too large for normal Git, after confirming rights to distribute them.
