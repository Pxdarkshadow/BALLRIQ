from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


def test_ir_methods_endpoint_returns_list():
    response = client.get("/api/ir/methods")
    assert response.status_code == 200
    body = response.json()
    assert "methods" in body
    assert len(body["methods"]) > 0


def test_ir_search_requires_query():
    response = client.post("/api/ir/search", json={"method": "bm25", "top_k": 5})
    assert response.status_code == 422


def test_ir_search_accepts_valid_request():
    response = client.post("/api/ir/search", json={"query": "Kohli", "method": "bm25", "top_k": 5})
    assert response.status_code == 200
    body = response.json()
    assert "results" in body


def test_ir_document_stats_responds():
    response = client.get("/api/ir/documents/stats")
    assert response.status_code == 200
    body = response.json()
    assert "total_documents" in body


def test_rag_answer_requires_question():
    response = client.post("/api/rag/answer", json={"language": "en"})
    assert response.status_code == 422


def test_rag_answer_accepts_valid_question():
    response = client.post("/api/rag/answer", json={"question": "Who scored?", "language": "en"})
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body


def test_evaluate_endpoint_validates_input():
    response = client.post("/api/ir/evaluate", json={"query": "test", "relevant_doc_ids": [], "top_k": 5})
    assert response.status_code == 200
    body = response.json()
    assert "metrics" in body
