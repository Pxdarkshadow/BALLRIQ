"""
Semantic retrieval using multilingual embeddings + FAISS.
"""
from pathlib import Path
from typing import List, Dict
import numpy as np


class SemanticRetriever:
    def __init__(self, documents: List[Dict], text_field: str = "content",
                 model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.documents = documents
        self.text_field = text_field
        self.model_name = model_name
        self.embeddings = None
        self.index = None
        self.model = None
        self.doc_ids = [d.get("document_id", str(i)) for i, d in enumerate(documents)]

    def build_index(self):
        from sentence_transformers import SentenceTransformer
        import faiss

        texts = [self._get_text(d) for d in self.documents]
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)

        print(f"Encoding {len(texts)} documents...")
        self.embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)

        # Normalize for cosine similarity
        faiss.normalize_L2(self.embeddings)

        # Build FAISS index
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(self.embeddings.astype(np.float32))

    def _get_text(self, doc: Dict) -> str:
        return doc.get(self.text_field, "")

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        if self.index is None:
            raise RuntimeError("Semantic index is unavailable. Run scripts/build_ir_indices.py to build it.")
        from sentence_transformers import SentenceTransformer
        import faiss

        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
        query_emb = self.model.encode([query])
        faiss.normalize_L2(query_emb)

        scores, indices = self.index.search(query_emb.astype(np.float32), top_k)

        results = []
        for rank, (idx, score) in enumerate(zip(indices[0], scores[0])):
            if idx >= 0 and score > 0:
                doc = self.documents[idx].copy()
                doc["score"] = float(score)
                doc["rank"] = rank + 1
                results.append(doc)
        return results

    def save(self, path: Path):
        import pickle
        path = Path(path)
        if self.index is None:
            raise RuntimeError("Build the semantic index before saving it.")
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "doc_ids": self.doc_ids,
            "model_name": self.model_name,
            "document_count": len(self.documents),
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)
        # Also save FAISS index separately
        import faiss
        faiss.write_index(self.index, str(path.with_suffix(".faiss")))

    @classmethod
    def load(cls, path: Path, documents: List[Dict]):
        import pickle
        path = Path(path)
        faiss_path = path.with_suffix(".faiss")
        if not path.exists() or not faiss_path.exists():
            raise FileNotFoundError(f"Semantic index files not found: {path} and {faiss_path}")
        import faiss
        with open(path, "rb") as f:
            data = pickle.load(f)
        doc_ids = [d.get("document_id", str(i)) for i, d in enumerate(documents)]
        if data.get("doc_ids") != doc_ids:
            raise ValueError("Semantic index does not match the current document corpus. Rebuild it.")
        instance = cls(documents, model_name=data["model_name"])
        instance.doc_ids = data["doc_ids"]
        instance.index = faiss.read_index(str(faiss_path))
        if instance.index.ntotal != len(documents):
            raise ValueError("Semantic index size does not match the current document corpus. Rebuild it.")
        return instance
