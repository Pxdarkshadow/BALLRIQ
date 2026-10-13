"""
Unicode Normalization for Hindi/Marathi Text

Handles:
- NFC normalization for Devanagari scripts
- Extra whitespace removal
- Repeated punctuation reduction
- Invalid encoding character removal
"""

import re
import unicodedata
from typing import Tuple


def normalize_unicode(text: str) -> str:
    """
    Apply Unicode NFC normalization to text.
    Critical for Hindi/Marathi where combining characters can create visually identical but different codepoints.
    """
    if not text:
        return ""
    return unicodedata.normalize('NFC', text)


def remove_extra_whitespace(text: str) -> str:
    """Normalize whitespace: collapse multiple spaces, tabs, newlines to single space."""
    if not text:
        return ""
    # Replace any whitespace sequence with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def reduce_repeated_punctuation(text: str, max_repeats: int = 2) -> str:
    """
    Reduce repeated punctuation (!!! -> !!, ??? -> ??, .... -> ..)
    Preserves up to max_repeats for emphasis.
    """
    if not text:
        return ""
    # Pattern for repeated punctuation
    pattern = re.compile(r'([!?।।\.])\1{%d,}' % max_repeats)
    return pattern.sub(lambda m: m.group(1) * max_repeats, text)


def remove_invalid_chars(text: str) -> str:
    """Remove control characters and other invalid Unicode."""
    if not text:
        return ""
    # Remove control characters except newline/tab
    # Keep: printable chars, whitespace, Devanagari, Latin, common punctuation
    cleaned = []
    for char in text:
        cat = unicodedata.category(char)
        # Keep printable characters and whitespace
        if cat.startswith('C') and char not in '\n\t\r ':
            continue
        cleaned.append(char)
    return ''.join(cleaned)


def normalize_devanagari_digits(text: str) -> str:
    """Convert Devanagari digits (०-९) to ASCII digits (0-9)."""
    devanagari_digits = '०१२३४५६७८९'
    ascii_digits = '0123456789'
    trans_table = str.maketrans(devanagari_digits, ascii_digits)
    return text.translate(trans_table)


def normalize_devanagari_punctuation(text: str) -> str:
    """Normalize Devanagari punctuation to standard forms."""
    replacements = {
        '।': '.',      # Devanagari danda -> period
        '॥': '.',      # Double danda -> period
        '‘': "'",      # Left single quote
        '’': "'",      # Right single quote
        '“': '"',      # Left double quote
        '”': '"',      # Right double quote
        '–': '-',      # En dash
        '—': '-',      # Em dash
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def unicode_normalization_pipeline(text: str) -> Tuple[str, dict]:
    """
    Full Unicode normalization pipeline.
    Returns normalized text and metadata about transformations applied.
    """
    if not text:
        return "", {"steps_applied": []}

    original = text
    steps = []

    # Step 1: Unicode NFC normalization
    text = normalize_unicode(text)
    steps.append("unicode_nfc")

    # Step 2: Normalize Devanagari digits
    text = normalize_devanagari_digits(text)
    steps.append("devanagari_digits")

    # Step 3: Normalize Devanagari punctuation
    text = normalize_devanagari_punctuation(text)
    steps.append("devanagari_punctuation")

    # Step 4: Remove invalid characters
    text = remove_invalid_chars(text)
    steps.append("remove_invalid_chars")

    # Step 5: Reduce repeated punctuation
    text = reduce_repeated_punctuation(text)
    steps.append("reduce_repeated_punctuation")

    # Step 6: Normalize whitespace
    text = remove_extra_whitespace(text)
    steps.append("normalize_whitespace")

    metadata = {
        "original_length": len(original),
        "normalized_length": len(text),
        "steps_applied": steps,
        "changed": original != text
    }

    return text, metadata


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "कोहली   ने  शानदार!!!  चौका मारा",
        "विराट्वार्त  कोहली",  # With combining chars
        "रन ०१२३४५६७८९",  # Devanagari digits
        "शानदार।।। क्या बात है!!!",  # Repeated punctuation
        "Hello​World",  # Zero-width space
        "Normal text without issues.",
    ]

    for test in test_cases:
        normalized, meta = unicode_normalization_pipeline(test)
        print(f"Input:    {repr(test)}")
        print(f"Output:   {repr(normalized)}")
        print(f"Meta:     {meta}")
        print("-" * 60)