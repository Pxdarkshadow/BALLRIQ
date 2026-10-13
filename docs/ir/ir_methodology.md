# Information Retrieval Methodology

The IR system maps natural language search queries across multiple languages back to the relevant commentary events. Indices exist at `models/ir/`.

## Document Processing
Documents are prepared and indexed using `scripts/build_ir_documents.py`. The text features are transformed through `backend/app/ir/preprocessing.py` to prepare semantic and lexical vectors.

## Retrieval Systems
Three independent retrievers power BALLRIQ's IR logic, exposed via `/api/ir/search`:
1. **TF-IDF Search**: Built and saved as `tfidf_index.pkl`.
2. **BM25 Search**: Built and saved as `bm25_index.pkl`. Provides stronger lexical scoring for keyword density on cricket queries.
3. **Semantic Search** (`backend/app/ir/semantic_search.py`): Maps deep contextual embeddings. Implemented using the multilingual model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` and an optimized FAISS store (`semantic_index.faiss`).

### Hybrid Search
In `backend/app/ir/hybrid_search.py`, a min-max normalized combination of BM25 and Semantic Search yields the hybrid search results. An adjustable weight term (`alpha = 0.5`) governs the distribution between BM25 (`alpha`) and Semantic Search (`1-alpha`).

## Cross-lingual Capability
The hybrid approach allows searches in English, Hindi, and Marathi (`data/evaluation/ir_queries.json`).

## Evaluation
The evaluation engine (`backend/app/ir/evaluation.py`) grades standard metrics (Precision@K, Recall@K, MRR, nDCG@K) using ground truth relevance sets (`data/evaluation/qrels.json`). 

Results in `reports/ir/ir_evaluation_report.json` document Hybrid retrieval demonstrating greater recall (0.0347 R@5) and nDCG (0.151 nDCG@5) scores than lexical baselines. Hybrid approach maintains precision when answering cross-lingual Hindi and Marathi search queries.