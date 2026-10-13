"""
Main IR pipeline orchestrator.
"""
from pathlib import Path
from typing import List, Dict
from backend.app.ir.tfidf_search import TFIDFRetriever, load_ir_documents
from backend.app.ir.bm25_search import BM25Retriever
from backend.app.ir.semantic_search import SemanticRetriever
from backend.app.ir.hybrid_search import HybridRetriever


class IRPipeline:
    def __init__(self, documents_path: Path, alpha: float = 0.5):
        self.documents_path = documents_path
        self.alpha = alpha
        self.documents = None
        self.tfidf = None
        self.bm25 = None
        self.semantic = None
        self.hybrid = None

    def load_documents(self):
        self.documents = load_ir_documents(self.documents_path)
        print(f"Loaded {len(self.documents)} documents")

    def build_all_indices(self):
        if self.documents is None:
            self.load_documents()
        print("Building TF-IDF index...")
        self.tfidf = TFIDFRetriever(self.documents)
        self.tfidf.build_index()

        print("Building BM25 index...")
        self.bm25 = BM25Retriever(self.documents)
        self.bm25.build_index()

        print("Building Semantic index...")
        self.semantic = SemanticRetriever(self.documents)
        self.semantic.build_index()

        print("Building Hybrid retriever...")
        self.hybrid = HybridRetriever(self.documents, alpha=self.alpha)
        self.hybrid.build_indices()

    def search(self, query: str, method: str = "hybrid", top_k: int = 10) -> List[Dict]:
        retriever_map = {
            "tfidf": self.tfidf,
            "bm25": self.bm25,
            "semantic": self.semantic,
            "hybrid": self.hybrid
        }
        retriever = retriever_map.get(method, self.hybrid)
        if retriever is None:
            raise ValueError(f"Method {method} not available")
        return retriever.search(query, top_k)