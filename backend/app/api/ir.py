"""
IR FastAPI Router: Live Lexical, Semantic, and Hybrid Information Retrieval Endpoints.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import json

from backend.app.ir.tfidf_search import TFIDFRetriever, load_ir_documents
from backend.app.ir.bm25_search import BM25Retriever
from backend.app.ir.hybrid_search import HybridRetriever
from backend.app.ir.semantic_search import SemanticRetriever
from backend.app.ir.evaluation import precision_at_k, recall_at_k, mrr, ndcg_at_k

router = APIRouter(prefix="/api/ir", tags=["ir"])

BASE_DIR = Path(__file__).resolve().parents[3]
DOCS_PATH = BASE_DIR / "data" / "processed" / "ir" / "documents.jsonl"
REPORTS_PATH = BASE_DIR / "reports" / "ir" / "ir_evaluation_report.json"
SEMANTIC_INDEX_PATH = BASE_DIR / "models" / "ir" / "semantic_index.pkl"

# Lazy-loaded singleton retrievers
_documents: Optional[List[Dict]] = None
_tfidf: Optional[TFIDFRetriever] = None
_bm25: Optional[BM25Retriever] = None
_hybrid: Optional[HybridRetriever] = None
_semantic: Optional[SemanticRetriever] = None


def get_ir_components():
    global _documents, _tfidf, _bm25, _hybrid, _semantic
    if _documents is None:
        if DOCS_PATH.exists():
            _documents = load_ir_documents(DOCS_PATH)
        else:
            _documents = []
        _tfidf = TFIDFRetriever(_documents)
        _tfidf.build_index()
        _bm25 = BM25Retriever(_documents)
        _bm25.build_index()
        _hybrid = HybridRetriever(_documents, alpha=0.5)
        _hybrid.bm25_retriever = _bm25
        try:
            _semantic = SemanticRetriever.load(SEMANTIC_INDEX_PATH, _documents)
            _hybrid.semantic_retriever = _semantic
        except (FileNotFoundError, ValueError, OSError, ImportError):
            _semantic = None
    return _documents, _tfidf, _bm25, _hybrid


def get_semantic_retriever() -> SemanticRetriever:
    get_ir_components()
    if _semantic is None:
        raise HTTPException(
            status_code=503,
            detail="Semantic index is unavailable or stale. Run scripts/build_ir_indices.py to build it.",
        )
    return _semantic


class SearchRequest(BaseModel):
    query: str
    method: str = "hybrid"  # "tfidf", "bm25", "semantic", "hybrid"
    top_k: int = 10
    match_id: Optional[str] = None
    alpha: Optional[float] = 0.5


class EvaluateRequest(BaseModel):
    query: str
    relevant_doc_ids: List[str]
    method: str = "hybrid"
    top_k: int = 5


@router.post("/search")
async def search(req: SearchRequest):
    docs, tfidf, bm25, hybrid = get_ir_components()
    if not docs:
        return {"status": "error", "message": "IR documents corpus not found.", "results": []}

    method = req.method.lower()
    if method == "tfidf":
        raw_results = tfidf.search(req.query, top_k=req.top_k * 2)
    elif method == "bm25":
        raw_results = bm25.search(req.query, top_k=req.top_k * 2)
    elif method == "semantic":
        raw_results = get_semantic_retriever().search(req.query, top_k=req.top_k * 2)
    elif method == "hybrid":
        get_semantic_retriever()
        raw_results = hybrid.search(req.query, top_k=req.top_k * 2, alpha=0.5 if req.alpha is None else req.alpha)
    else:
        raw_results = bm25.search(req.query, top_k=req.top_k * 2)

    # Filter by match_id if provided
    if req.match_id:
        filtered = [r for r in raw_results if r.get("match_id") == req.match_id]
    else:
        filtered = raw_results

    results = filtered[:req.top_k]
    for idx, r in enumerate(results, 1):
        r["rank"] = idx

    return {
        "query": req.query,
        "method": req.method,
        "top_k": req.top_k,
        "match_id": req.match_id,
        "total_matches": len(results),
        "results": results
    }


@router.get("/compare")
async def compare_methods(query: str = Query(..., min_length=1), top_k: int = Query(5, ge=1, le=20)):
    """Side-by-side execution of all 4 retrieval methods for the IR Explorer."""
    docs, tfidf, bm25, hybrid = get_ir_components()

    res_tfidf = tfidf.search(query, top_k=top_k)
    res_bm25 = bm25.search(query, top_k=top_k)
    semantic = get_semantic_retriever()
    res_semantic = semantic.search(query, top_k=top_k)
    res_hybrid = hybrid.search(query, top_k=top_k, alpha=0.5)

    return {
        "query": query,
        "top_k": top_k,
        "methods": {
            "tfidf": {"title": "TF-IDF Baseline", "results": res_tfidf},
            "bm25": {"title": "BM25 Okapi", "results": res_bm25},
            "semantic": {"title": "Semantic Vector Search", "results": res_semantic},
            "hybrid": {"title": "Hybrid Search (BM25 + Semantic α=0.5)", "results": res_hybrid}
        }
    }


@router.get("/methods")
async def list_methods():
    return {
        "methods": [
            {"id": "tfidf", "name": "TF-IDF Vector Space", "type": "Lexical Baseline", "description": "Term frequency-inverse document frequency cosine ranking"},
            {"id": "bm25", "name": "BM25 Okapi", "type": "Probabilistic Relevance", "description": "State-of-the-art lexical ranking with document length normalization"},
            {"id": "semantic", "name": "Semantic Vector Search", "type": "Dense Embedding", "description": "Multilingual sentence embeddings for cross-lingual intent matching"},
            {"id": "hybrid", "name": "Hybrid Fusion", "type": "Ensemble", "description": "Convex combination of BM25 lexical score and Semantic embedding similarity"}
        ]
    }


@router.post("/evaluate")
async def evaluate_query(req: EvaluateRequest):
    docs, tfidf, bm25, hybrid = get_ir_components()
    method = req.method.lower()
    if method == "tfidf":
        retrieved = tfidf.search(req.query, top_k=req.top_k)
    elif method == "bm25":
        retrieved = bm25.search(req.query, top_k=req.top_k)
    elif method == "semantic":
        retrieved = get_semantic_retriever().search(req.query, top_k=req.top_k)
    else:
        get_semantic_retriever()
        retrieved = hybrid.search(req.query, top_k=req.top_k)

    relevant_set = set(req.relevant_doc_ids)
    p_k = precision_at_k(retrieved, relevant_set, req.top_k)
    r_k = recall_at_k(retrieved, relevant_set, req.top_k)
    mrr_score = mrr(retrieved, relevant_set)
    ndcg_score = ndcg_at_k(retrieved, relevant_set, req.top_k)

    return {
        "query": req.query,
        "method": req.method,
        "top_k": req.top_k,
        "metrics": {
            f"precision@{req.top_k}": round(p_k, 4),
            f"recall@{req.top_k}": round(r_k, 4),
            "mrr": round(mrr_score, 4),
            f"ndcg@{req.top_k}": round(ndcg_score, 4)
        },
        "retrieved_documents": retrieved
    }


@router.get("/documents/stats")
async def document_stats():
    docs, _, _, _ = get_ir_components()
    lang_dist = {}
    sources = {}
    event_dist = {}

    for d in docs:
        lang = d.get("language", "unknown")
        lang_dist[lang] = lang_dist.get(lang, 0) + 1
        src = d.get("source", "commentary")
        sources[src] = sources.get(src, 0) + 1
        ev = d.get("event_type", "OTHER")
        event_dist[ev] = event_dist.get(ev, 0) + 1

    return {
        "total_documents": len(docs),
        "language_distribution": lang_dist,
        "sources_distribution": sources,
        "events_distribution": event_dist,
        "index_status": "loaded",
        "supported_languages": ["Hindi (hi)", "Marathi (mr)", "English (en)"]
    }
