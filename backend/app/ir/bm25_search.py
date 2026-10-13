"""
BM25 retrieval using rank_bm25.
"""
import json
from pathlib import Path
from typing import List, Dict
from rank_bm25 import BM25Okapi


class BM25Retriever:
    def __init__(self, documents: List[Dict], text_field: str = "content"):
        self.documents = documents
        self.text_field = text_field
        self.bm25 = None
        self.doc_ids = [d.get("document_id", str(i)) for i, d in enumerate(documents)]

    def build_index(self):
        from backend.app.ir.preprocessing import tokenize_lexical
        tokenized_corpus = [tokenize_lexical(self._get_text(d)) for d in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def _get_text(self, doc: Dict) -> str:
        return doc.get(self.text_field, "")

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        if self.bm25 is None:
            self.build_index()
        from backend.app.ir.preprocessing import tokenize_lexical
        tokenized_query = tokenize_lexical(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                doc = self.documents[idx].copy()
                doc["score"] = float(scores[idx])
                doc["rank"] = len(results) + 1
                results.append(doc)
        return results

    def save(self, path: Path):
        import pickle
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"bm25": self.bm25, "doc_ids": self.doc_ids}, f)

    @classmethod
    def load(cls, path: Path, documents: List[Dict]):
        import pickle
        with open(path, "rb") as f:
            data = pickle.load(f)
        instance = cls(documents)
        instance.bm25 = data["bm25"]
        instance.doc_ids = data["doc_ids"]
        return instance