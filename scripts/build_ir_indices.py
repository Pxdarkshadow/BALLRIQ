#!/usr/bin/env python3
"""
Build and save all IR indices.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from backend.app.ir.tfidf_search import TFIDFRetriever, load_ir_documents
from backend.app.ir.bm25_search import BM25Retriever
from backend.app.ir.semantic_search import SemanticRetriever

def main():
    data_dir = PROJECT_ROOT / "data" / "processed" / "ir"
    model_dir = PROJECT_ROOT / "models" / "ir"
    model_dir.mkdir(parents=True, exist_ok=True)

    print("Loading documents...")
    documents = load_ir_documents(data_dir / "documents.jsonl")
    print(f"Loaded {len(documents)} documents")

    # TF-IDF
    print("\n=== Building TF-IDF index ===")
    tfidf = TFIDFRetriever(documents)
    tfidf.build_index()
    tfidf.save(model_dir / "tfidf_index.pkl")
    print("TF-IDF saved")

    # BM25
    print("\n=== Building BM25 index ===")
    bm25 = BM25Retriever(documents)
    bm25.build_index()
    bm25.save(model_dir / "bm25_index.pkl")
    print("BM25 saved")

    # Semantic
    print("\n=== Building Semantic index ===")
    semantic = SemanticRetriever(documents)
    semantic.build_index()
    semantic.save(model_dir / "semantic_index.pkl")
    print("Semantic saved")

    print("\n=== All indices built and saved ===")

if __name__ == "__main__":
    main()
