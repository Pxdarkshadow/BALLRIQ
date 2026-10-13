"""
Language Identification for Cricket Commentary

Detects:
- hi: Hindi
- mr: Marathi
- en: English
- hi_en: Code-mixed Hindi-English
- mr_en: Code-mixed Marathi-English
"""

import re
from typing import Tuple, Dict, List
from dataclasses import dataclass


# Character range patterns
DEVANAGARI_PATTERN = re.compile(r'[ऀ-ॿ]')
LATIN_PATTERN = re.compile(r'[a-zA-Z]')

# Language-specific word indicators
HINDI_INDICATORS = {
    'ने', 'को', 'से', 'का', 'के', 'की', 'पर', 'में', 'और', 'या', 'है', 'था', 'थी', 'थे',
    'हैं', 'हो', 'हुए', 'हुआ', 'हुई', 'कर', 'किया', 'करे', 'करना', 'किया',
    'गया', 'गई', 'गए', 'आया', 'आई', 'आए', 'दिया', 'दिया', 'ली', 'लिया',
    'बना', 'बनी', 'बने', 'मारा', 'मारी', 'मारे', 'खेला', 'खेली', 'खेले',
    'बल्लेबाज', 'गेंदबाज', 'विकेट', 'रन', 'ओवर', 'गेंद', 'मैच', 'जीत', 'हार',
    'शतक', 'अर्धशतक', 'चौका', 'छक्का', 'बाद', 'आउट', 'नॉट', 'आउट',
    'कवर', 'ड्राइव', 'यॉर्कर', 'बाउंड्री', 'स्ट्राइक', 'रेट', 'साझेदारी',
    'पावरप्ले', 'डेथ', 'ओवर', 'मैच', 'टॉस', 'बल्लेबाजी', 'गेंदबाजी'
}

MARATHI_INDICATORS = {
    'ने', 'ला', 'चा', 'ची', 'चे', 'मध्ये', 'आणि', 'किंवा', 'आहे', 'होता', 'होती', 'होते',
    'आहात', 'हो', 'झाले', 'झाला', 'झाली', 'झाले', 'केले', 'केली', 'केला',
    'गेल', 'गेला', 'गेल्या', 'आले', 'आला', 'आली', 'दिले', 'दिला', 'दिली',
    'बनवले', 'बनवला', 'बनवली', 'मारला', 'मारली', 'मारले', 'खेळला', 'खेळली', 'खेळले',
    'घेतला', 'घेतली', 'घेतले', 'मिळाले', 'मिळाला', 'मिळाली',
    'फलंदाज', 'बॉलर', 'विकेट', 'धाव', 'ओव्हर', 'चेंडू', 'सामना', 'जिंक', 'हार',
    'शतक', 'अर्धशतक', 'चौका', 'षटकार', 'बाद', 'आउट', 'नॉट', 'आउट',
    'कव्हर', 'ड्राइव्ह', 'यॉर्कर', 'बाउंड्री', 'स्ट्राइक', 'रेट', 'संधी',
    'पॉवरप्ले', 'डेथ', 'ओव्हर', 'सामना', 'टॉस', 'बॅटिंग', 'बॉलिंग',
    'आणि', 'किंवा', 'परंतु', 'तर', 'असे', 'असले', 'असली', 'असलेले',
    'होईल', 'होतील', 'होतील', 'झाली', 'झाले', 'झालेल',
    'करते', 'करत', 'करतो', 'करते', 'केला', 'केली', 'केले',
    'पाहिले', 'पाहिला', 'पाहिली', 'समजले', 'समजला', 'समजली'
}

ENGLISH_INDICATORS = {
    'the', 'and', 'or', 'is', 'was', 'were', 'are', 'been', 'being', 'have', 'has', 'had',
    'do', 'did', 'does', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
    'to', 'for', 'from', 'in', 'on', 'at', 'by', 'with', 'of', 'a', 'an',
    'bowler', 'batter', 'batsman', 'wicket', 'run', 'over', 'ball', 'match', 'win', 'loss',
    'century', 'fifty', 'four', 'six', 'out', 'not', 'out', 'boundary',
    'cover', 'drive', 'yorker', 'strike', 'rate', 'partnership',
    'powerplay', 'death', 'over', 'match', 'toss', 'batting', 'bowling',
    'caught', 'bowled', 'lbw', 'run', 'stumped', 'hit', 'wicket',
    'he', 'she', 'it', 'they', 'we', 'you', 'i', 'my', 'your', 'his', 'her', 'their', 'our'
}

# Code-mixed patterns
HINDI_ENGLISH_MIX_PATTERN = re.compile(r'[ऀ-ॿ].*[a-zA-Z]|[a-zA-Z].*[ऀ-ॿ]')
MARATHI_ENGLISH_MIX_PATTERN = re.compile(r'[ऀ-ॿ].*[a-zA-Z]|[a-zA-Z].*[ऀ-ॿ]')


@dataclass
class LanguageResult:
    language: str
    confidence: float
    is_code_mixed: bool
    scores: Dict[str, float]


def detect_script_ratio(text: str) -> Dict[str, float]:
    """Calculate ratio of Devanagari vs Latin characters."""
    total_chars = len([c for c in text if not c.isspace()])
    if total_chars == 0:
        return {'devanagari': 0.0, 'latin': 0.0, 'other': 0.0}

    devanagari_count = len(DEVANAGARI_PATTERN.findall(text))
    latin_count = len(LATIN_PATTERN.findall(text))
    other_count = total_chars - devanagari_count - latin_count

    return {
        'devanagari': devanagari_count / total_chars,
        'latin': latin_count / total_chars,
        'other': other_count / total_chars
    }


def detect_vocabulary_language(text: str) -> Dict[str, float]:
    """Score text based on language-specific vocabulary."""
    words = set(text.lower().split())
    if not words:
        return {'hi': 0.0, 'mr': 0.0, 'en': 0.0}

    hi_score = len(words & HINDI_INDICATORS) / len(words)
    mr_score = len(words & MARATHI_INDICATORS) / len(words)
    en_score = len(words & ENGLISH_INDICATORS) / len(words)

    return {'hi': hi_score, 'mr': mr_score, 'en': en_score}


def is_code_mixed(text: str, script_ratio: Dict[str, float]) -> Tuple[bool, str]:
    """
    Detect if text is code-mixed.
    Returns (is_mixed, mixed_type) where mixed_type is 'hi_en', 'mr_en', or ''.
    """
    dev_ratio = script_ratio['devanagari']
    lat_ratio = script_ratio['latin']

    # Significant presence of both scripts
    if dev_ratio > 0.15 and lat_ratio > 0.15:
        # Check vocabulary to determine which Indian language
        vocab_scores = detect_vocabulary_language(text)
        if vocab_scores['hi'] > vocab_scores['mr']:
            return True, 'hi_en'
        elif vocab_scores['mr'] > 0:
            return True, 'mr_en'
        else:
            # Default to Hindi-English if unclear
            return True, 'hi_en'

    return False, ''


def identify_language(text: str) -> LanguageResult:
    """
    Main language identification function.
    Returns LanguageResult with language code, confidence, and code-mixed flag.
    """
    if not text or not text.strip():
        return LanguageResult(
            language='unknown',
            confidence=0.0,
            is_code_mixed=False,
            scores={'hi': 0.0, 'mr': 0.0, 'en': 0.0}
        )

    # Get script ratios
    script_ratio = detect_script_ratio(text)

    # Get vocabulary scores
    vocab_scores = detect_vocabulary_language(text)

    # Check for code-mixing
    is_mixed, mixed_type = is_code_mixed(text, script_ratio)

    if is_mixed:
        # Code-mixed detected
        primary = mixed_type.split('_')[0]  # hi or mr
        confidence = 0.7 + 0.3 * (vocab_scores[primary] + script_ratio['devanagari'])
        confidence = min(confidence, 0.95)

        return LanguageResult(
            language=mixed_type,
            confidence=confidence,
            is_code_mixed=True,
            scores=vocab_scores
        )

    # Not code-mixed: determine primary language
    dev_ratio = script_ratio['devanagari']
    lat_ratio = script_ratio['latin']

    if dev_ratio > 0.6:
        # Primarily Devanagari - decide Hindi vs Marathi
        if vocab_scores['mr'] > vocab_scores['hi']:
            return LanguageResult(
                language='mr',
                confidence=0.8 + 0.2 * vocab_scores['mr'],
                is_code_mixed=False,
                scores=vocab_scores
            )
        else:
            return LanguageResult(
                language='hi',
                confidence=0.8 + 0.2 * vocab_scores['hi'],
                is_code_mixed=False,
                scores=vocab_scores
            )
    elif lat_ratio > 0.6:
        # Primarily Latin - English
        return LanguageResult(
            language='en',
            confidence=0.85 + 0.15 * vocab_scores['en'],
            is_code_mixed=False,
            scores=vocab_scores
        )
    else:
        # Ambiguous - use vocabulary scores
        max_lang = max(vocab_scores, key=vocab_scores.get)
        max_score = vocab_scores[max_lang]

        if max_score > 0.1:
            return LanguageResult(
                language=max_lang,
                confidence=0.5 + 0.3 * max_score,
                is_code_mixed=False,
                scores=vocab_scores
            )
        else:
            # Default based on script
            if dev_ratio > lat_ratio:
                return LanguageResult(
                    language='hi',
                    confidence=0.4,
                    is_code_mixed=False,
                    scores=vocab_scores
                )
            else:
                return LanguageResult(
                    language='en',
                    confidence=0.4,
                    is_code_mixed=False,
                    scores=vocab_scores
                )


def identify_language_detailed(text: str) -> Dict:
    """
    Detailed language identification with all scores.
    """
    result = identify_language(text)
    script_ratio = detect_script_ratio(text)
    vocab_scores = detect_vocabulary_language(text)

    return {
        'language': result.language,
        'confidence': result.confidence,
        'is_code_mixed': result.is_code_mixed,
        'vocabulary_scores': vocab_scores,
        'script_ratio': script_ratio,
        'text_length': len(text),
        'word_count': len(text.split())
    }


def batch_identify(texts: List[str]) -> List[LanguageResult]:
    """Identify language for multiple texts."""
    return [identify_language(text) for text in texts]


if __name__ == "__main__":
    test_cases = [
        "कोहली ने शानदार कवर ड्राइव खेला और गेंद चार रन के लिए चली गई",
        "कोहलीने अप्रतिम कव्हर ड्राइव्ह मारला आणि चेंडू सीमारेषेबाहेर गेला",
        "Kohli played a brilliant cover drive for four runs",
        "Virat ne शानदार four मारा",
        "कोहलीने amazing six मारला",
        "Bumrah bowled a yorker and the batter was beaten",
        "बुमराह ने यॉर्कर डाली",
        "What a shot by Kohli!",
    ]

    for test in test_cases:
        result = identify_language_detailed(test)
        print(f"Text: {test[:60]}...")
        print(f"  Language: {result['language']}, Confidence: {result['confidence']:.2f}, Code-mixed: {result['is_code_mixed']}")
        print(f"  Script: {result['script_ratio']}")
        print(f"  Vocab:  {result['vocabulary_scores']}")
        print()