"""
Number Normalization for Cricket Commentary

Converts:
- Hindi number words to digits (चार -> 4, छह -> 6)
- Marathi number words to digits (चार -> 4, सहा -> 6)
- English number words to digits (four -> 4, six -> 6)
- Cricket meaning: 4 -> FOUR, 6 -> SIX
"""

import re
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass


# Hindi number words
HINDI_NUMBERS = {
    'शून्य': 0, 'जीरो': 0,
    'एक': 1, '१': 1,
    'दो': 2, '२': 2,
    'तीन': 3, '३': 3,
    'चार': 4, '४': 4,
    'पांच': 5, 'पाँच': 5, '५': 5,
    'छह': 6, 'छः': 6, '६': 6,
    'सात': 7, '७': 7,
    'आठ': 8, '८': 8,
    'नौ': 9, '९': 9,
    'दस': 10, '१०': 10,
    'ग्यारह': 11, '११': 11,
    'बारह': 12, '१२': 12,
    'तेरह': 13, '१३': 13,
    'चौदह': 14, '१४': 14,
    'पंद्रह': 15, '१५': 15,
    'सोलह': 16, '१६': 16,
    'सत्रह': 17, '१७': 17,
    'अठारह': 18, '१८': 18,
    'उन्नीस': 19, '१९': 19,
    'बीस': 20, '२०': 20,
}

# Marathi number words
MARATHI_NUMBERS = {
    'शून्य': 0, 'जीरो': 0,
    'एक': 1, '१': 1,
    'दोन': 2, '२': 2,
    'तीन': 3, '३': 3,
    'चार': 4, '४': 4,
    'पाच': 5, '५': 5,
    'सहा': 6, '६': 6,
    'सात': 7, '७': 7,
    'आठ': 8, '८': 8,
    'नऊ': 9, '९': 9,
    'दहा': 10, '१०': 10,
    'अकरा': 11, '११': 11,
    'बारा': 12, '१२': 12,
    'तेरा': 13, '१३': 13,
    'चौदा': 14, '१४': 14,
    'पंधरा': 15, '१५': 15,
    'सोळा': 16, '१६': 16,
    'सतरा': 17, '१७': 17,
    'अठरा': 18, '१८': 18,
    'एकोणीस': 19, '१९': 19,
    'वीस': 20, '२०': 20,
}

# English number words
ENGLISH_NUMBERS = {
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
}

# Cricket-specific: digit -> event mapping
CRICKET_DIGIT_EVENTS = {
    4: 'FOUR',
    6: 'SIX',
}

# Compound number patterns (e.g., "twenty one", "इक्कीस")
HINDI_COMPOUNDS = {
    'इक्कीस': 21, 'बाईस': 22, 'तेईस': 23, 'चौबीस': 24, 'पच्चीस': 25,
    'छब्बीस': 26, 'सत्ताईस': 27, 'अट्ठाईस': 28, 'उनतीस': 29, 'तीस': 30,
    'इकतीस': 31, 'बत्तीस': 32, 'तैंतीस': 33, 'चौंतीस': 34, 'पैंतीस': 35,
    'छत्तीस': 36, 'सैंतीस': 37, 'अड़तीस': 38, 'उनतालीस': 39, 'चालीस': 40,
    'इकतालीस': 41, 'बयालीस': 42, 'तैंतालीस': 43, 'चवालीस': 44, 'पैंतालीस': 45,
    'छियालीस': 46, 'सैंतालीस': 47, 'अड़तालीस': 48, 'उनचास': 49, 'पचास': 50,
}

MARATHI_COMPOUNDS = {
    'एक्कीस': 21, 'बाईस': 22, 'तेव्हा': 23, 'चोवीस': 24, 'पंचवीस': 25,
    'सहावीस': 26, 'सत्तावीस': 27, 'अठ्ठावीस': 28, 'एकोणतीस': 29, 'तीस': 30,
    'एकतीस': 31, 'बत्तीस': 32, 'तेहेतीस': 33, 'चौतीस': 34, 'पस्तीस': 35,
    'छत्तीस': 36, 'सदतीस': 37, 'अडतीस': 38, 'एकोणचाळीस': 39, 'चाळीस': 40,
    'एक्केचाळीस': 41, 'बेचाळीस': 42, 'त्रेचाळीस': 43, 'चव्वेचाळीस': 44, 'पंचेचाळीस': 45,
    'सहेचाळीस': 46, 'सत्तेचाळीस': 47, 'अठ्ठेचाळीस': 48, 'एकोणपन्नास': 49, 'पन्नास': 50,
}

ENGLISH_COMPOUNDS = {
    'twenty one': 21, 'twenty two': 22, 'twenty three': 23, 'twenty four': 24, 'twenty five': 25,
    'twenty six': 26, 'twenty seven': 27, 'twenty eight': 28, 'twenty nine': 29, 'thirty': 30,
    'thirty one': 31, 'thirty two': 32, 'thirty three': 33, 'thirty four': 34, 'thirty five': 35,
    'thirty six': 36, 'thirty seven': 37, 'thirty eight': 38, 'thirty nine': 39, 'forty': 40,
    'forty one': 41, 'forty two': 42, 'forty three': 43, 'forty four': 44, 'forty five': 45,
    'forty six': 46, 'forty seven': 47, 'forty eight': 48, 'forty nine': 49, 'fifty': 50,
}

# Ordinal patterns
HINDI_ORDINALS = {
    'पहला': 1, 'दूसरा': 2, 'तीसरा': 3, 'चौथा': 4, 'पांचवा': 5, 'पाँचवा': 5,
    'छठा': 6, 'सातवाँ': 7, 'आठवाँ': 8, 'नौवाँ': 9, 'दसवाँ': 10,
}

MARATHI_ORDINALS = {
    'पहिला': 1, 'दुसरा': 2, 'तिसरा': 3, 'चौथा': 4, 'पाचवा': 5,
    'सहावा': 6, 'सातवा': 7, 'आठवा': 8, 'नववा': 9, 'दहावा': 10,
}

ENGLISH_ORDINALS = {
    'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
    'sixth': 6, 'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10,
}


@dataclass
class NumberNormalizationResult:
    original_text: str
    normalized_text: str
    numbers_found: List[Dict]
    cricket_events: List[Dict]


def build_number_pattern(numbers_dict: Dict[str, int]) -> re.Pattern:
    """Build regex pattern for number words, sorted by length (longest first)."""
    sorted_words = sorted(numbers_dict.keys(), key=len, reverse=True)
    escaped = [re.escape(w) for w in sorted_words]
    return re.compile(r'\b(' + '|'.join(escaped) + r')\b', re.IGNORECASE)


HINDI_NUMBER_PATTERN = build_number_pattern({**HINDI_NUMBERS, **HINDI_COMPOUNDS, **HINDI_ORDINALS})
MARATHI_NUMBER_PATTERN = build_number_pattern({**MARATHI_NUMBERS, **MARATHI_COMPOUNDS, **MARATHI_ORDINALS})
ENGLISH_NUMBER_PATTERN = build_number_pattern({**ENGLISH_NUMBERS, **ENGLISH_COMPOUNDS, **ENGLISH_ORDINALS})

# Devanagari digit pattern
DEVANAGARI_DIGIT_PATTERN = re.compile(r'[०-९]+')
ASCII_DIGIT_PATTERN = re.compile(r'\b\d+\b')


def normalize_hindi_numbers(text: str) -> Tuple[str, List[Dict]]:
    """Replace Hindi number words with digits."""
    numbers_found = []

    def replace(match):
        word = match.group(0)
        # Check compounds first
        for dict_name, num_dict in [('compound', HINDI_COMPOUNDS), ('ordinal', HINDI_ORDINALS), ('basic', HINDI_NUMBERS)]:
            if word in num_dict:
                value = num_dict[word]
                numbers_found.append({
                    'original': word,
                    'normalized': str(value),
                    'type': dict_name,
                    'language': 'hi',
                    'position': match.start()
                })
                return str(value)
        return word

    normalized = HINDI_NUMBER_PATTERN.sub(replace, text)
    return normalized, numbers_found


def normalize_marathi_numbers(text: str) -> Tuple[str, List[Dict]]:
    """Replace Marathi number words with digits."""
    numbers_found = []

    def replace(match):
        word = match.group(0)
        for dict_name, num_dict in [('compound', MARATHI_COMPOUNDS), ('ordinal', MARATHI_ORDINALS), ('basic', MARATHI_NUMBERS)]:
            if word in num_dict:
                value = num_dict[word]
                numbers_found.append({
                    'original': word,
                    'normalized': str(value),
                    'type': dict_name,
                    'language': 'mr',
                    'position': match.start()
                })
                return str(value)
        return word

    normalized = MARATHI_NUMBER_PATTERN.sub(replace, text)
    return normalized, numbers_found


def normalize_english_numbers(text: str) -> Tuple[str, List[Dict]]:
    """Replace English number words with digits."""
    numbers_found = []

    def replace(match):
        word = match.group(0).lower()
        for dict_name, num_dict in [('compound', ENGLISH_COMPOUNDS), ('ordinal', ENGLISH_ORDINALS), ('basic', ENGLISH_NUMBERS)]:
            if word in num_dict:
                value = num_dict[word]
                numbers_found.append({
                    'original': word,
                    'normalized': str(value),
                    'type': dict_name,
                    'language': 'en',
                    'position': match.start()
                })
                return str(value)
        return word

    normalized = ENGLISH_NUMBER_PATTERN.sub(replace, text)
    return normalized, numbers_found


def normalize_devanagari_digits(text: str) -> Tuple[str, List[Dict]]:
    """Convert Devanagari digits (०-९) to ASCII."""
    numbers_found = []

    def replace(match):
        dev_digits = match.group(0)
        ascii_digits = ''.join(str('०१२३४५६७८९'.index(d)) for d in dev_digits)
        numbers_found.append({
            'original': dev_digits,
            'normalized': ascii_digits,
            'type': 'devanagari_digit',
            'language': 'hi/mr',
            'position': match.start()
        })
        return ascii_digits

    normalized = DEVANAGARI_DIGIT_PATTERN.sub(replace, text)
    return normalized, numbers_found


def detect_cricket_events_from_numbers(text: str) -> List[Dict]:
    """
    Detect cricket events from normalized numbers.
    e.g., "4 runs" -> FOUR event, "6" -> SIX event
    """
    events = []

    # Pattern: digit followed by cricket context
    patterns = [
        (re.compile(r'\b4\s*(?:runs?|run|रन|धाव|चौका|फोर)\b', re.IGNORECASE), 'FOUR'),
        (re.compile(r'\b6\s*(?:runs?|run|रन|धाव|छक्का|सिक्स|षटकार)\b', re.IGNORECASE), 'SIX'),
        (re.compile(r'\b4\b'), 'FOUR'),  # Bare 4 in cricket context
        (re.compile(r'\b6\b'), 'SIX'),   # Bare 6 in cricket context
    ]

    for pattern, event_type in patterns:
        for match in pattern.finditer(text):
            events.append({
                'event': event_type,
                'matched_text': match.group(0),
                'position': match.start(),
                'number': 4 if event_type == 'FOUR' else 6
            })

    return events


def normalize_numbers(text: str, language: str = 'auto') -> NumberNormalizationResult:
    """
    Main number normalization function.
    language: 'hi', 'mr', 'en', 'hi_en', 'mr_en', or 'auto'
    """
    original = text
    all_numbers = []

    # Step 1: Normalize Devanagari digits first
    text, nums = normalize_devanagari_digits(text)
    all_numbers.extend(nums)

    # Step 2: Language-specific word normalization
    if language in ('hi', 'hi_en', 'auto'):
        text, nums = normalize_hindi_numbers(text)
        all_numbers.extend(nums)

    if language in ('mr', 'mr_en', 'auto'):
        text, nums = normalize_marathi_numbers(text)
        all_numbers.extend(nums)

    if language in ('en', 'hi_en', 'mr_en', 'auto'):
        text, nums = normalize_english_numbers(text)
        all_numbers.extend(nums)

    # Step 3: Detect cricket events from numbers
    cricket_events = detect_cricket_events_from_numbers(text)

    return NumberNormalizationResult(
        original_text=original,
        normalized_text=text,
        numbers_found=all_numbers,
        cricket_events=cricket_events
    )


def normalize_numbers_simple(text: str, language: str = 'auto') -> str:
    """Simple interface returning only normalized text."""
    result = normalize_numbers(text, language)
    return result.normalized_text


if __name__ == "__main__":
    test_cases = [
        ("कोहली ने चार रन बनाए", "hi"),
        ("कोहलीने चार धाव केल्या", "mr"),
        ("Kohli scored four runs", "en"),
        ("Virat ne चार रन मारे", "hi_en"),
        ("कोहलीने amazing six मारला", "mr_en"),
        ("He scored ४ runs", "hi"),
        ("The score is ६", "mr"),
        ("पहला ओवर", "hi"),
        ("पहिला ओव्हर", "mr"),
        ("First over", "en"),
    ]

    for text, lang in test_cases:
        result = normalize_numbers(text, lang)
        print(f"Input ({lang}): {text}")
        print(f"Output:       {result.normalized_text}")
        print(f"Numbers:      {result.numbers_found}")
        print(f"Cricket:      {result.cricket_events}")
        print("-" * 60)