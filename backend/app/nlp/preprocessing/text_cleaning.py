"""
Text Cleaning for Cricket Commentary

Removes:
- Unnecessary symbols
- URLs
- HTML artifacts
- Broken encoding
- Excessive punctuation (but preserves meaningful cricket symbols)
"""

import re
from typing import Tuple, List


# Patterns for cleaning
URL_PATTERN = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)
HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
HTML_ENTITY_PATTERN = re.compile(r'&[a-zA-Z0-9#]+;')
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# Cricket symbols to PRESERVE (don't clean these)
CRICKET_SYMBOLS = {
    '4', '6', 'W', 'w', 'WD', 'wd', 'NB', 'nb',
    'FOUR', 'SIX', 'WICKET', 'OUT', 'DOT',
    'चौका', 'छक्का', 'विकेट', 'आउट', 'डॉट',
    'चार', 'छह', 'बाद',
}

# Symbols that are safe to remove
REMOVABLE_SYMBOLS_PATTERN = re.compile(
    r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]\{\}\'\"/\@\#\$\%\^\&\*\+\=\<\>\|\\'
    r'उऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहािीुूृॄॅॆेैॉॊोौ्'
    r'अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह'
    r'ँंःअआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह]+'
)


def remove_urls(text: str) -> Tuple[str, int]:
    """Remove URLs from text. Returns cleaned text and count of URLs removed."""
    if not text:
        return "", 0
    urls_found = URL_PATTERN.findall(text)
    cleaned = URL_PATTERN.sub(' ', text)
    return cleaned, len(urls_found)


def remove_html_artifacts(text: str) -> Tuple[str, int]:
    """Remove HTML tags and entities. Returns cleaned text and count removed."""
    if not text:
        return "", 0

    tags = HTML_TAG_PATTERN.findall(text)
    entities = HTML_ENTITY_PATTERN.findall(text)

    cleaned = HTML_TAG_PATTERN.sub(' ', text)
    cleaned = HTML_ENTITY_PATTERN.sub(' ', cleaned)

    return cleaned, len(tags) + len(entities)


def remove_emails(text: str) -> Tuple[str, int]:
    """Remove email addresses."""
    if not text:
        return "", 0
    emails = EMAIL_PATTERN.findall(text)
    cleaned = EMAIL_PATTERN.sub(' ', text)
    return cleaned, len(emails)


def clean_excessive_punctuation(text: str, preserve_cricket: bool = True) -> Tuple[str, int]:
    """
    Remove excessive punctuation while optionally preserving cricket-relevant symbols.
    """
    if not text:
        return "", 0

    original = text
    count = 0

    if preserve_cricket:
        # Only reduce non-cricket punctuation runs
        # Replace 3+ same punctuation with 2, but skip cricket symbols
        def replace_excessive(match):
            nonlocal count
            char = match.group(1)
            if char in '46Ww':
                return match.group(0)  # Preserve cricket symbols
            count += 1
            return char * 2

        # Pattern: 3+ same punctuation character
        pattern = re.compile(r'([!?।\.]{3,})')
        text = pattern.sub(replace_excessive, text)
    else:
        # Aggressive: reduce all 3+ punctuation runs
        pattern = re.compile(r'([^\w\s])\1{2,}')
        text = pattern.sub(lambda m: m.group(1) * 2, text)
        count = len(pattern.findall(original))

    return text, count


def remove_control_chars(text: str) -> Tuple[str, int]:
    """Remove invisible control characters."""
    if not text:
        return "", 0

    control_chars = [
        '​',  # Zero width space
        '‌',  # Zero width non-joiner
        '‍',  # Zero width joiner
        '⁠',  # Word joiner
        '﻿',  # BOM
        '\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07',
        '\x08', '\x0b', '\x0c', '\x0e', '\x0f',
        '\x10', '\x11', '\x12', '\x13', '\x14', '\x15', '\x16', '\x17',
        '\x18', '\x19', '\x1a', '\x1b', '\x1c', '\x1d', '\x1e', '\x1f',
        '\x7f',
    ]

    count = 0
    for ch in control_chars:
        c = text.count(ch)
        if c > 0:
            count += c
            text = text.replace(ch, '')

    return text, count


def normalize_quotes(text: str) -> str:
    """Normalize various quote styles to standard ASCII."""
    replacements = {
        '‘': "'",  # Left single quote
        '’': "'",  # Right single quote
        '“': '"',  # Left double quote
        '”': '"',  # Right double quote
        '‚': "'",  # Single low-9 quote
        '‛': "'",  # Single high-reversed-9 quote
        '„': '"',  # Double low-9 quote
        '‟': '"',  # Double high-reversed-9 quote
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def normalize_dashes(text: str) -> str:
    """Normalize various dash styles."""
    replacements = {
        '–': '-',  # En dash
        '—': '-',  # Em dash
        '―': '-',  # Horizontal bar
        '−': '-',  # Minus sign
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def clean_text(text: str, preserve_cricket_symbols: bool = True) -> Tuple[str, dict]:
    """
    Full text cleaning pipeline.
    Returns cleaned text and metadata about transformations.
    """
    if not text:
        return "", {"steps_applied": [], "counts": {}}

    original = text
    counts = {}
    steps = []

    # Step 1: Remove control characters
    text, cnt = remove_control_chars(text)
    counts['control_chars_removed'] = cnt
    steps.append('remove_control_chars')

    # Step 2: Remove URLs
    text, cnt = remove_urls(text)
    counts['urls_removed'] = cnt
    steps.append('remove_urls')

    # Step 3: Remove HTML artifacts
    text, cnt = remove_html_artifacts(text)
    counts['html_artifacts_removed'] = cnt
    steps.append('remove_html_artifacts')

    # Step 4: Remove emails
    text, cnt = remove_emails(text)
    counts['emails_removed'] = cnt
    steps.append('remove_emails')

    # Step 5: Normalize quotes
    text = normalize_quotes(text)
    steps.append('normalize_quotes')

    # Step 6: Normalize dashes
    text = normalize_dashes(text)
    steps.append('normalize_dashes')

    # Step 7: Clean excessive punctuation
    text, cnt = clean_excessive_punctuation(text, preserve_cricket_symbols)
    counts['excessive_punctuation_cleaned'] = cnt
    steps.append('clean_excessive_punctuation')

    # Step 8: Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    steps.append('normalize_whitespace')

    metadata = {
        "original_length": len(original),
        "cleaned_length": len(text),
        "steps_applied": steps,
        "counts": counts,
        "changed": original != text
    }

    return text, metadata


if __name__ == "__main__":
    test_cases = [
        "Check out http://example.com for more info!",
        "Hello <b>world</b> & welcome!",
        "Email me at test@example.com please.",
        "विराट ने शानदार चौका मारा!!! क्या बात है!!!",
        "Normal text with \"smart quotes\" and – dashes.",
        "Text with​invisible‌chars.",
        "FOUR!!! SIX!!! WICKET!!!",
    ]

    for test in test_cases:
        cleaned, meta = clean_text(test)
        print(f"Input:  {repr(test)}")
        print(f"Output: {repr(cleaned)}")
        print(f"Meta:   {meta}")
        print("-" * 60)