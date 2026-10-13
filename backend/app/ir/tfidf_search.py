"""
TF-IDF baseline retrieval.
"""
import json
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFRetriever:
    def __init__(self, documents: List[Dict], text_field: str = "content"):
        self.documents = documents
        self.text_field = text_field
        self.vectorizer = None
        self.doc_vectors = None
        self.doc_ids = [d.get("document_id", str(i)) for i, d in enumerate(documents)]

    def build_index(self):
        texts = [self._get_text(d) for d in self.documents]
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True
        )
        self.doc_vectors = self.vectorizer.fit_transform(texts)

    def _get_text(self, doc: Dict) -> str:
        return doc.get(self.text_field, "")

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        if self.vectorizer is None:
            self.build_index()
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.doc_vectors).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                doc = self.documents[idx].copy()
                doc["score"] = float(similarities[idx])
                doc["rank"] = len(results) + 1
                results.append(doc)
        return results

    def save(self, path: Path):
        import pickle
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({
                "vectorizer": self.vectorizer,
                "doc_vectors": self.doc_vectors,
                "doc_ids": self.doc_ids
            }, f)

    @classmethod
    def load(cls, path: Path, documents: List[Dict]):
        import pickle
        with open(path, "rb") as f:
            data = pickle.load(f)
        instance = cls(documents)
        instance.vectorizer = data["vectorizer"]
        instance.doc_vectors = data["doc_vectors"]
        instance.doc_ids = data["doc_ids"]
        return instance


def load_ir_documents(path: Path) -> List[Dict]:
    """Load documents from JSONL."""
    documents = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            documents.append(json.loads(line.strip()))
    return documents