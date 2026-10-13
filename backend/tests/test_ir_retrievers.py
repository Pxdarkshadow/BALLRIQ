from backend.app.ir.tfidf_search import TFIDFRetriever
from backend.app.ir.bm25_search import BM25Retriever
from backend.app.ir.hybrid_search import HybridRetriever


def test_tfidf_builds_index():
    docs = [{"document_id": "d1", "content": "Kohli scored four runs"}]
    retriever = TFIDFRetriever(docs)
    retriever.build_index()
    assert retriever.tfidf_matrix is not None


def test_tfidf_searches_empty_corpus():
    retriever = TFIDFRetriever([])
    retriever.build_index()
    results = retriever.search("Kohli", top_k=5)
    assert results == []


def test_tfidf_returns_scored_documents():
    docs = [
        {"document_id": "d1", "content": "Kohli hit a boundary"},
        {"document_id": "d2", "content": "Rohit played defense"}
    ]
    retriever = TFIDFRetriever(docs)
    retriever.build_index()
    results = retriever.search("Kohli", top_k=1)
    assert len(results) <= 1
    if results:
        assert "score" in results[0]


def test_bm25_builds_index():
    docs = [{"document_id": "d1", "content": "Kohli scored runs"}]
    retriever = BM25Retriever(docs)
    retriever.build_index()
    assert retriever.bm25 is not None


def test_bm25_searches_with_scoring():
    docs = [{"document_id": "d1", "content": "Kohli boundary"}, {"document_id": "d2", "content": "Rohit six"}]
    retriever = BM25Retriever(docs)
    retriever.build_index()
    results = retriever.search("Kohli", top_k=2)
    assert len(results) <= 2


def test_bm25_handles_empty_query():
    docs = [{"document_id": "d1", "content": "test"}]
    retriever = BM25Retriever(docs)
    retriever.build_index()
    results = retriever.search("", top_k=5)
    assert isinstance(results, list)


def test_hybrid_combines_retrievers():
    docs = [{"document_id": "d1", "content": "Kohli four"}]
    hybrid = HybridRetriever(docs, alpha=0.5)
    hybrid.bm25_retriever = BM25Retriever(docs)
    hybrid.bm25_retriever.build_index()
    results = hybrid.search("Kohli", top_k=5)
    assert isinstance(results, list)


def test_hybrid_respects_top_k():
    docs = [{"document_id": f"d{i}", "content": f"doc {i}"} for i in range(10)]
    hybrid = HybridRetriever(docs, alpha=0.5)
    hybrid.bm25_retriever = BM25Retriever(docs)
    hybrid.bm25_retriever.build_index()
    results = hybrid.search("doc", top_k=3)
    assert len(results) <= 3
