"""
Hybrid retrieval combining lexical (BM25) and semantic scores.
"""
from typing import List, Dict
from backend.app.ir.bm25_search import BM25Retriever
from backend.app.ir.semantic_search import SemanticRetriever


class HybridRetriever:
    def __init__(self, documents: List[Dict], alpha: float = 0.5,
                 text_field: str = "content"):
        self.documents = documents
        self.alpha = alpha  # weight for BM25, (1-alpha) for semantic
        self.bm25_retriever = BM25Retriever(documents, text_field)
        self.semantic_retriever = SemanticRetriever(documents, text_field)

    def build_indices(self):
        print("Building BM25 index...")
        self.bm25_retriever.build_index()
        print("Building semantic index...")
        self.semantic_retriever.build_index()

    def _normalize_scores(self, results: List[Dict]) -> Dict[str, float]:
        """Min-max normalize scores to 0-1 range."""
        if not results:
            return {}
        scores = [r["score"] for r in results]
        min_s, max_s = min(scores), max(scores)
        if max_s == min_s:
            return {r["document_id"]: 1.0 for r in results}
        return {r["document_id"]: (r["score"] - min_s) / (max_s - min_s) for r in results}

    def search(self, query: str, top_k: int = 10, alpha: float = None) -> List[Dict]:
        if alpha is None:
            alpha = self.alpha

        # Get more results from each for better fusion
        bm25_results = self.bm25_retriever.search(query, top_k * 2)
        semantic_results = self.semantic_retriever.search(query, top_k * 2)

        # Normalize scores
        bm25_norm = self._normalize_scores(bm25_results)
        semantic_norm = self._normalize_scores(semantic_results)

        # Combine scores
        all_doc_ids = set(bm25_norm.keys()) | set(semantic_norm.keys())
        combined = []
        for doc_id in all_doc_ids:
            bm25_score = bm25_norm.get(doc_id, 0.0)
            sem_score = semantic_norm.get(doc_id, 0.0)
            hybrid_score = alpha * bm25_score + (1 - alpha) * sem_score

            # Find the document
            doc = next((d for d in self.documents if d.get("document_id") == doc_id), None)
            if doc:
                combined.append({
                    **doc,
                    "score": hybrid_score,
                    "bm25_score": bm25_score,
                    "semantic_score": sem_score
                })

        # Sort and rank
        combined.sort(key=lambda x: x["score"], reverse=True)
        for i, r in enumerate(combined[:top_k]):
            r["rank"] = i + 1
        return combined[:top_k]