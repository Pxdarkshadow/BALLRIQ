"""
IR-specific preprocessing (separate from NLP preprocessing).
"""
import re
from typing import List


def clean_document_text(text: str) -> str:
    """Clean document text for lexical retrieval."""
    # Lowercase
    text = text.lower()
    # Remove excessive punctuation but keep cricket-relevant
    text = re.sub(r'[^\w\s\-\']+', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize_lexical(text: str) -> List[str]:
    """Tokenize for lexical retrieval (TF-IDF, BM25)."""
    return clean_document_text(text).split()


def preprocess_for_semantic(text: str) -> str:
    """Clean but preserve more structure for semantic embeddings."""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text