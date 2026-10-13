"""
IR evaluation metrics.
"""
from typing import List, Dict, Set
import json


def precision_at_k(retrieved: List[Dict], relevant: Set[str], k: int) -> float:
    if k == 0:
        return 0.0
    retrieved_k = [r.get("document_id") for r in retrieved[:k]]
    hits = sum(1 for doc_id in retrieved_k if doc_id in relevant)
    return hits / k


def recall_at_k(retrieved: List[Dict], relevant: Set[str], k: int) -> float:
    if not relevant:
        return 0.0
    retrieved_k = [r.get("document_id") for r in retrieved[:k]]
    hits = sum(1 for doc_id in retrieved_k if doc_id in relevant)
    return hits / len(relevant)


def mrr(retrieved: List[Dict], relevant: Set[str]) -> float:
    for rank, doc in enumerate(retrieved, 1):
        if doc.get("document_id") in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved: List[Dict], relevant: Set[str], k: int) -> float:
    """Normalized Discounted Cumulative Gain."""
    import math
    retrieved_k = retrieved[:k]
    # DCG
    dcg = 0.0
    for i, doc in enumerate(retrieved_k):
        rel = 1.0 if doc.get("document_id") in relevant else 0.0
        if i == 0:
            dcg += rel
        else:
            dcg += rel / math.log2(i + 1)
    # IDCG (ideal)
    ideal_rels = [1.0] * min(len(relevant), k)
    idcg = 0.0
    for i, rel in enumerate(ideal_rels):
        if i == 0:
            idcg += rel
        else:
            idcg += rel / math.log2(i + 1)
    return dcg / idcg if idcg > 0 else 0.0


def evaluate_retriever(retriever, queries: List[Dict], qrels: Dict[str, List[str]],
                       top_k: int = 5) -> Dict:
    """Evaluate a retriever on query set."""
    metrics = {
        "precision@1": 0.0, "precision@3": 0.0, "precision@5": 0.0,
        "recall@1": 0.0, "recall@3": 0.0, "recall@5": 0.0,
        "mrr": 0.0, "ndcg@5": 0.0
    }
    valid_queries = 0

    for q in queries:
        query_id = q.get("query_id")
        query_text = q.get("query")
        if not query_id or not query_text:
            continue
        relevant = set(qrels.get(query_id, []))
        if not relevant:
            continue

        results = retriever.search(query_text, top_k=top_k)

        metrics["precision@1"] += precision_at_k(results, relevant, 1)
        metrics["precision@3"] += precision_at_k(results, relevant, 3)
        metrics["precision@5"] += precision_at_k(results, relevant, 5)
        metrics["recall@1"] += recall_at_k(results, relevant, 1)
        metrics["recall@3"] += recall_at_k(results, relevant, 3)
        metrics["recall@5"] += recall_at_k(results, relevant, 5)
        metrics["mrr"] += mrr(results, relevant)
        metrics["ndcg@5"] += ndcg_at_k(results, relevant, 5)
        valid_queries += 1

    if valid_queries > 0:
        for k in metrics:
            metrics[k] /= valid_queries

    metrics["num_queries"] = valid_queries
    return metrics


def compare_retrievers(retrievers: Dict[str, object], queries: List[Dict],
                       qrels: Dict[str, List[str]], top_k: int = 5) -> Dict:
    """Compare multiple retrievers."""
    results = {}
    for name, retriever in retrievers.items():
        print(f"Evaluating {name}...")
        results[name] = evaluate_retriever(retriever, queries, qrels, top_k)
    return results


def load_qrels(path) -> Dict[str, List[str]]:
    """Load relevance judgments from JSON."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Convert to {query_id: [doc_ids]}
    qrels = {}
    for item in data:
        qrels[item["query_id"]] = item.get("relevant_documents", [])
    return qrels