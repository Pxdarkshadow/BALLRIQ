# System Architecture

## Frontend
A React React (Vite) application comprising the following primary flows: Match Center, Dataset exploration, Preprocessing views, NLP model, IR interactions, Evaluation metrics, and big-data/lakehouse analysis (BDA).

## Backend
A FastAPI service consisting of 7 distinct routers housed in `backend/app/api/`. 
Data persists to a SQLite database (`backend/app/db/models.py`).

### Data Flow
- **Raw Data** (`data/raw/`): Unedited source commentary strings.
- **Interim Data** (`data/interim/`): Cleaned, normalized, and tokenized (with language-detection labels appended).
- **Processed Data** (`data/processed/`): Fully contextualized dataset items, generated train/val/test splits, and structured IR documents.

### RAG System
The grounding system (`backend/app/rag/engine.py`) retrieves context from the **hybrid IR search constraint**. The retrieved context limits the generator. If the evidence lacks confidence (hybrid search yields < 0.05 relevance) or no documents match, the engine falls back deterministically to indicate insufficient evidence, actively refusing to hallucinate ungrounded answers.

### Audio System
The `/api/audio/analyze` endpoint expects explicit pre-transcribed strings (i.e. `TranscriptRequest(transcript="string")`), routing NLP processing. The capability `/api/audio/transcribe` explicitly defaults to returning `HTTP 503 Service Unavailable`, as no acoustic model integration is physically installed by default.