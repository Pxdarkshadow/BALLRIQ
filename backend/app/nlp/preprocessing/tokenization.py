"""
Tokenization for Cricket Commentary

Supports:
- Hindi/Marathi: indic-nlp library (with fallback to simple whitespace)
- English: NLTK word_tokenize (with fallback to simple whitespace)
- Code-mixed: Language-aware tokenization
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass


# Try to import optional dependencies
try:
    from indicnlp.tokenize import indic_tokenize
    INDIC_NLP_AVAILABLE = True
except ImportError:
    INDIC_NLP_AVAILABLE = False

try:
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


@dataclass
class TokenizationResult:
    original_text: str
    tokens: List[str]
    language: str
    token_count: int
    method_used: str


def simple_tokenize(text: str) -> List[str]:
    """
    Simple whitespace + punctuation tokenizer as fallback.
    Works for all languages.
    """
    if not text:
        return []

    # Split on whitespace and punctuation, keep punctuation as separate tokens
    # This regex splits on whitespace but keeps punctuation attached or separate
    tokens = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
    return [t for t in tokens if t.strip()]


def indic_tokenize_text(text: str, language: str = 'hi') -> List[str]:
    """
    Tokenize Hindi/Marathi text using indic-nlp.
    language: 'hi' for Hindi, 'mr' for Marathi
    """
    if not INDIC_NLP_AVAILABLE:
        return simple_tokenize(text)

    try:
        # indic-nlp expects language code
        lang_code = 'hi' if language == 'hi' else 'mr'
        tokens = indic_tokenize.trivial_tokenize(text, lang=lang_code)
        return tokens
    except Exception:
        return simple_tokenize(text)


def english_tokenize(text: str) -> List[str]:
    """Tokenize English text using NLTK."""
    if not NLTK_AVAILABLE:
        return simple_tokenize(text)

    try:
        return word_tokenize(text)
    except Exception:
        return simple_tokenize(text)


def code_mixed_tokenize(text: str, primary_lang: str) -> List[str]:
    """
    Tokenize code-mixed text.
    Strategy: Split by script changes, tokenize each segment with appropriate tokenizer.
    """
    # Simple approach: use indic tokenizer for Devanagari segments, NLTK for Latin
    # For now, fall back to simple tokenization
    return simple_tokenize(text)


def detect_primary_script(text: str) -> str:
    """Detect primary script of text: 'devanagari', 'latin', or 'mixed'."""
    devanagari_count = len(re.findall(r'[ऀ-ॿ]', text))
    latin_count = len(re.findall(r'[a-zA-Z]', text))
    total = devanagari_count + latin_count

    if total == 0:
        return 'unknown'

    if devanagari_count / total > 0.6:
        return 'devanagari'
    elif latin_count / total > 0.6:
        return 'latin'
    else:
        return 'mixed'


def tokenize(text: str, language: str = 'auto') -> TokenizationResult:
    """
    Main tokenization function.
    language: 'hi', 'mr', 'en', 'hi_en', 'mr_en', or 'auto'
    """
    if not text:
        return TokenizationResult(
            original_text=text,
            tokens=[],
            language=language,
            token_count=0,
            method_used='empty'
        )

    original = text
    detected_lang = language

    # Auto-detect language if needed
    if language == 'auto':
        script = detect_primary_script(text)
        if script == 'devanagari':
            # Could be hi or mr - default to hi
            detected_lang = 'hi'
        elif script == 'latin':
            detected_lang = 'en'
        else:
            detected_lang = 'hi_en'  # Mixed

    # Tokenize based on language
    if detected_lang == 'hi':
        tokens = indic_tokenize_text(text, 'hi')
        method = 'indic_nlp' if INDIC_NLP_AVAILABLE else 'simple_fallback'
    elif detected_lang == 'mr':
        tokens = indic_tokenize_text(text, 'mr')
        method = 'indic_nlp' if INDIC_NLP_AVAILABLE else 'simple_fallback'
    elif detected_lang == 'en':
        tokens = english_tokenize(text)
        method = 'nltk' if NLTK_AVAILABLE else 'simple_fallback'
    elif detected_lang in ('hi_en', 'mr_en'):
        tokens = code_mixed_tokenize(text, detected_lang.split('_')[0])
        method = 'code_mixed_simple'
    else:
        tokens = simple_tokenize(text)
        method = 'simple'

    return TokenizationResult(
        original_text=original,
        tokens=tokens,
        language=detected_lang,
        token_count=len(tokens),
        method_used=method
    )


def tokenize_with_pos(text: str, language: str = 'auto') -> List[Tuple[str, str]]:
    """
    Tokenize with POS tags (if available).
    Returns list of (token, pos_tag) tuples.
    """
    result = tokenize(text, language)
    tokens = result.tokens

    # Simple POS tagging fallback
    if NLTK_AVAILABLE and result.language == 'en':
        try:
            from nltk import pos_tag
            return pos_tag(tokens)
        except Exception:
            pass

    # Fallback: basic heuristic POS
    pos_tags = []
    for token in tokens:
        if re.match(r'^\d+$', token):
            pos = 'NUM'
        elif re.match(r'^[A-Z][a-z]+$', token):
            pos = 'PROPN'
        elif token in '.,!?;:':
            pos = 'PUNCT'
        elif token.lower() in {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}:
            pos = 'ADP'
        elif token.lower() in {'is', 'was', 'were', 'are', 'am', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'did', 'does'}:
            pos = 'AUX'
        else:
            pos = 'X'
        pos_tags.append((token, pos))

    return pos_tags


if __name__ == "__main__":
    print(f"indic-nlp available: {INDIC_NLP_AVAILABLE}")
    print(f"NLTK available: {NLTK_AVAILABLE}")
    print()

    test_cases = [
        ("कोहली ने शानदार कवर ड्राइव खेला", "hi"),
        ("कोहलीने अप्रतिम कव्हर ड्राइव्ह मारला", "mr"),
        ("Kohli played a brilliant cover drive", "en"),
        ("Virat ne शानदार four मारा", "hi_en"),
        ("कोहलीने amazing six मारला", "mr_en"),
        ("बुमराह ने यॉर्कर डाली", "hi"),
    ]

    for text, lang in test_cases:
        result = tokenize(text, lang)
        print(f"Input ({lang}): {text}")
        print(f"Tokens: {result.tokens}")
        print(f"Count: {result.token_count}, Method: {result.method_used}")
        print()

    # Test with POS
    print("POS Tagging:")
    pos_result = tokenize_with_pos("Kohli scored four runs", "en")
    print(pos_result)