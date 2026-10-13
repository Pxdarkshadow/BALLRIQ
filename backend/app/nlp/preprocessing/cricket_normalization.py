"""
Cricket Vocabulary Normalization

Maps cricket terminology variants to canonical forms using cricket_vocabulary.json.
Handles Hindi, Marathi, English, and code-mixed variants.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CricketNormalizationResult:
    original_text: str
    normalized_text: str
    terms_mapped: List[Dict]


class CricketVocabularyNormalizer:
    """Normalizes cricket terminology to canonical forms."""

    def __init__(self, vocab_path: Optional[str] = None):
        if vocab_path is None:
            vocab_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "cricket_vocabulary.json"

        with open(vocab_path, 'r', encoding='utf-8') as f:
            self.vocab = json.load(f)

        # Build reverse mapping: variant -> canonical
        self.variant_to_canonical = {}
        self.canonical_terms = set(self.vocab.keys())

        for canonical, variants in self.vocab.items():
            for variant in variants:
                self.variant_to_canonical[variant.lower()] = canonical

        # Build regex pattern for matching (longest first)
        all_variants = sorted(self.variant_to_canonical.keys(), key=len, reverse=True)
        escaped_variants = [re.escape(v) for v in all_variants]
        # Word boundary pattern that works with Devanagari
        self.pattern = re.compile(r'(?<!\w)(' + '|'.join(escaped_variants) + r')(?!\w)', re.IGNORECASE)

    def normalize(self, text: str) -> CricketNormalizationResult:
        """Normalize cricket terms in text."""
        original = text
        terms_mapped = []

        def replace(match):
            variant = match.group(0).lower()
            canonical = self.variant_to_canonical.get(variant, variant.upper())
            terms_mapped.append({
                'original': match.group(0),
                'canonical': canonical,
                'position': match.start(),
                'variant_lower': variant
            })
            return canonical

        normalized = self.pattern.sub(replace, text)

        return CricketNormalizationResult(
            original_text=original,
            normalized_text=normalized,
            terms_mapped=terms_mapped
        )

    def get_canonical(self, term: str) -> str:
        """Get canonical form for a single term."""
        return self.variant_to_canonical.get(term.lower(), term.upper())

    def is_cricket_term(self, term: str) -> bool:
        """Check if term is in cricket vocabulary."""
        return term.lower() in self.variant_to_canonical

    def get_all_variants(self, canonical: str) -> List[str]:
        """Get all variants for a canonical term."""
        return self.vocab.get(canonical, [])


def normalize_cricket_terms(text: str, vocab_path: Optional[str] = None) -> CricketNormalizationResult:
    """Convenience function for cricket term normalization."""
    normalizer = CricketVocabularyNormalizer(vocab_path)
    return normalizer.normalize(text)


# Additional cricket-specific normalization rules
CRICKET_CONTEXT_PATTERNS = [
    # Score patterns
    (re.compile(r'(\d+)\s*/\s*(\d+)'), lambda m: f"{m.group(1)}/{m.group(2)}"),
    (re.compile(r'(\d+)\s*(?:runs?|रन|धाव)\s*(?:for|के)\s*(\d+)\s*(?:wickets?|विकेट|बाद)'),
     lambda m: f"{m.group(1)}/{m.group(2)}"),
    # Over patterns
    (re.compile(r'(\d+)\.(\d)\s*(?:over|ओवर|ओव्हर)'), lambda m: f"{m.group(1)}.{m.group(2)} ov"),
    (re.compile(r'over\s+(\d+)\.(\d)'), lambda m: f"over {m.group(1)}.{m.group(2)}"),
    # Run rate
    (re.compile(r'(?:run.rate|रन.रेट|स्ट्राइक.रेट)\s*[:=]\s*(\d+\.?\d*)'), lambda m: f"RR: {m.group(1)}"),
]


def apply_cricket_context_normalization(text: str) -> Tuple[str, List[Dict]]:
    """Apply cricket-specific context normalization patterns."""
    original = text
    mappings = []

    for pattern, replacer in CRICKET_CONTEXT_PATTERNS:
        matches = list(pattern.finditer(text))
        for match in matches:
            mappings.append({
                'pattern': pattern.pattern,
                'original': match.group(0),
                'position': match.start()
            })
        text = pattern.sub(replacer, text)

    return text, mappings


if __name__ == "__main__":
    normalizer = CricketVocabularyNormalizer()

    test_cases = [
        "कोहली ने शानदार चौका मारा",
        "वॉर्नर ने चार रन के लिए कवर ड्राइव खेला",
        "बुमराह ने छक्का लगाया",
        "Kohli hit a four through cover",
        "Warner scored 4 runs with a cover drive",
        "Bumrah bowled a yorker for a wicket",
        "पांड्या ने मिडविकेट के ऊपर से छक्का मारा",
        "पंड्याने मिडविकेटवरून षटकार मारला",
        "Virat ne शानदार four मारा",
        "कोहलीने amazing six मारला",
        "He scored a century in the match",
        "कोहली का शतक पूरा हुआ",
    ]

    for test in test_cases:
        result = normalizer.normalize(test)
        text_after_context, context_maps = apply_cricket_context_normalization(result.normalized_text)
        print(f"Input:    {test}")
        print(f"Terms:    {result.terms_mapped}")
        print(f"Normalized: {text_after_context}")
        print("-" * 60)