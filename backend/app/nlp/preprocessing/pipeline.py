"""
NLP Preprocessing Pipeline

Orchestrates all preprocessing steps:
1. Unicode Normalization
2. Text Cleaning
3. Language Identification
4. Number Normalization
5. Cricket Vocabulary Normalization
5. Player Name Normalization
6. Tokenization

Produces structured output with metadata for each step.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Import preprocessing modules
from .unicode_normalization import unicode_normalization_pipeline
from .text_cleaning import clean_text
from .language_processing import identify_language, LanguageResult
from .number_normalization import normalize_numbers, NumberNormalizationResult
from .cricket_normalization import normalize_cricket_terms, CricketNormalizationResult
from .player_normalization import normalize_player_names, PlayerNormalizationResult
from .tokenization import tokenize, TokenizationResult


@dataclass
class PreprocessingStepResult:
    step_name: str
    input_text: str
    output_text: str
    metadata: Dict
    success: bool
    error: Optional[str] = None


@dataclass
class PreprocessingResult:
    original_text: str
    final_text: str
    detected_language: str
    language_confidence: float
    is_code_mixed: bool
    steps: List[PreprocessingStepResult]
    entities: List[Dict]
    tokens: List[str]
    token_count: int
    cricket_events: List[Dict]
    timestamp: str


class NLPPreprocessingPipeline:
    """Complete NLP preprocessing pipeline for cricket commentary."""

    def __init__(self, vocab_path: Optional[str] = None, aliases_path: Optional[str] = None):
        self.vocab_path = vocab_path
        self.aliases_path = aliases_path

    def process(self, text: str, language: str = 'auto') -> PreprocessingResult:
        """
        Run full preprocessing pipeline on input text.
        """
        if not text:
            return PreprocessingResult(
                original_text="",
                final_text="",
                detected_language="unknown",
                language_confidence=0.0,
                is_code_mixed=False,
                steps=[],
                entities=[],
                tokens=[],
                token_count=0,
                cricket_events=[],
                timestamp=datetime.now().isoformat()
            )

        original = text
        current_text = text
        steps = []
        all_entities = []
        cricket_events = []

        # Step 1: Unicode Normalization
        try:
            current_text, meta = unicode_normalization_pipeline(current_text)
            steps.append(PreprocessingStepResult(
                step_name="unicode_normalization",
                input_text=text,
                output_text=current_text,
                metadata=meta,
                success=True
            ))
        except Exception as e:
            steps.append(PreprocessingStepResult(
                step_name="unicode_normalization",
                input_text=text,
                output_text=current_text,
                metadata={},
                success=False,
                error=str(e)
            ))

        # Step 2: Text Cleaning
        try:
            current_text, meta = clean_text(current_text, preserve_cricket_symbols=True)
            steps.append(PreprocessingStepResult(
                step_name="text_cleaning",
                input_text=steps[-1].output_text if steps else text,
                output_text=current_text,
                metadata=meta,
                success=True
            ))
        except Exception as e:
            steps.append(PreprocessingStepResult(
                step_name="text_cleaning",
                input_text=steps[-1].output_text if steps else text,
                output_text=current_text,
                metadata={},
                success=False,
                error=str(e)
            ))

        # Step 3: Language Identification
        try:
            lang_result = identify_language(current_text)
            steps.append(PreprocessingStepResult(
                step_name="language_identification",
                input_text=current_text,
                output_text=current_text,
                metadata={
                    "language": lang_result.language,
                    "confidence": lang_result.confidence,
                    "is_code_mixed": lang_result.is_code_mixed,
                    "scores": lang_result.scores
                },
                success=True
            ))
        except Exception as e:
            lang_result = LanguageResult('unknown', 0.0, False, {})
            steps.append(PreprocessingStepResult(
                step_name="language_identification",
                input_text=current_text,
                output_text=current_text,
                metadata={},
                success=False,
                error=str(e)
            ))

        # Step 4: Number Normalization
        try:
            num_result = normalize_numbers(current_text, lang_result.language)
            current_text = num_result.normalized_text
            cricket_events.extend(num_result.cricket_events)
            all_entities.extend([
                {**n, 'entity_type': 'NUMBER'} for n in num_result.numbers_found
            ])
            steps.append(PreprocessingStepResult(
                step_name="number_normalization",
                input_text=steps[-1].output_text if steps else current_text,
                output_text=current_text,
                metadata={
                    "numbers_found": len(num_result.numbers_found),
                    "cricket_events_detected": len(num_result.cricket_events)
                },
                success=True
            ))
        except Exception as e:
            steps.append(PreprocessingStepResult(
                step_name="number_normalization",
                input_text=steps[-1].output_text if steps else current_text,
                output_text=current_text,
                metadata={},
                success=False,
                error=str(e)
            ))

        # Step 5: Cricket Vocabulary Normalization
        try:
            cricket_result = normalize_cricket_terms(current_text)
            current_text = cricket_result.normalized_text
            all_entities.extend([
                {**t, 'entity_type': 'CRICKET_TERM'} for t in cricket_result.terms_mapped
            ])
            steps.append(PreprocessingStepResult(
                step_name="cricket_vocabulary_normalization",
                input_text=steps[-1].output_text if steps else current_text,
                output_text=current_text,
                metadata={
                    "terms_mapped": len(cricket_result.terms_mapped),
                    "terms": cricket_result.terms_mapped
                },
                success=True
            ))
        except Exception as e:
            steps.append(PreprocessingStepResult(
                step_name="cricket_vocabulary_normalization",
                input_text=steps[-1].output_text if steps else current_text,
                output_text=current_text,
                metadata={},
                success=False,
                error=str(e)
            ))

        # Step 6: Player Name Normalization
        try:
            player_result = normalize_player_names(current_text)
            current_text = player_result.normalized_text
            all_entities.extend([
                {**p, 'entity_type': 'PLAYER'} for p in player_result.players_found
            ])
            steps.append(PreprocessingStepResult(
                step_name="player_name_normalization",
                input_text=steps[-1].output_text if steps else current_text,
                output_text=current_text,
                metadata={
                    "players_found": len(player_result.players_found),
                    "players": player_result.players_found
                },
                success=True
            ))
        except Exception as e:
            steps.append(PreprocessingStepResult(
                step_name="player_name_normalization",
                input_text=steps[-1].output_text if steps else current_text,
                output_text=current_text,
                metadata={},
                success=False,
                error=str(e)
            ))

        # Step 7: Tokenization
        try:
            token_result = tokenize(current_text, lang_result.language)
            steps.append(PreprocessingStepResult(
                step_name="tokenization",
                input_text=current_text,
                output_text=current_text,
                metadata={
                    "token_count": token_result.token_count,
                    "method_used": token_result.method_used,
                    "tokens": token_result.tokens
                },
                success=True
            ))
            tokens = token_result.tokens
        except Exception as e:
            tokens = []
            steps.append(PreprocessingStepResult(
                step_name="tokenization",
                input_text=current_text,
                output_text=current_text,
                metadata={},
                success=False,
                error=str(e)
            ))

        return PreprocessingResult(
            original_text=original,
            final_text=current_text,
            detected_language=lang_result.language,
            language_confidence=lang_result.confidence,
            is_code_mixed=lang_result.is_code_mixed,
            steps=steps,
            entities=all_entities,
            tokens=tokens,
            token_count=len(tokens),
            cricket_events=cricket_events,
            timestamp=datetime.now().isoformat()
        )

    def process_batch(self, texts: List[str], language: str = 'auto') -> List[PreprocessingResult]:
        """Process multiple texts."""
        return [self.process(text, language) for text in texts]

    def save_result(self, result: PreprocessingResult, output_path: str):
        """Save preprocessing result to JSON."""
        # Convert dataclasses to dict
        data = asdict(result)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def preprocess_commentary_record(record: Dict, pipeline: NLPPreprocessingPipeline) -> Dict:
    """
    Process a single commentary record from the dataset.
    Adds preprocessing results to the record.
    """
    text = record.get('original_text', '')
    result = pipeline.process(text)

    # Add preprocessing output to record
    record['preprocessed_text'] = result.final_text
    record['detected_language'] = result.detected_language
    record['language_confidence'] = result.language_confidence
    record['is_code_mixed'] = result.is_code_mixed
    record['preprocessing_steps'] = [asdict(s) for s in result.steps]
    record['entities'] = result.entities
    record['tokens'] = result.tokens
    record['token_count'] = result.token_count
    record['cricket_events'] = result.cricket_events
    record['preprocessing_timestamp'] = result.timestamp

    return record


def run_pipeline_on_dataset(input_path: str, output_path: str, language: str = 'auto'):
    """Run pipeline on entire commentary dataset."""
    pipeline = NLPPreprocessingPipeline()

    with open(input_path, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f]

    print(f"Processing {len(records)} records...")

    processed = []
    for i, record in enumerate(records):
        processed.append(preprocess_commentary_record(record, pipeline))
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(records)}")

    # Save processed records
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for record in processed:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

    print(f"Saved {len(processed)} processed records to {output_path}")

    # Generate preprocessing report
    generate_preprocessing_report(processed, output_dir / "preprocessing_report.json")


def generate_preprocessing_report(processed_records: List[Dict], report_path: Path):
    """Generate preprocessing summary report."""
    total = len(processed_records)
    if total == 0:
        return

    lang_dist = {}
    step_stats = {}
    entity_types = {}
    total_tokens = 0

    for record in processed_records:
        lang = record.get('detected_language', 'unknown')
        lang_dist[lang] = lang_dist.get(lang, 0) + 1

        for entity in record.get('entities', []):
            etype = entity.get('entity_type', 'UNKNOWN')
            entity_types[etype] = entity_types.get(etype, 0) + 1

        total_tokens += record.get('token_count', 0)

        for step in record.get('preprocessing_steps', []):
            step_name = step['step_name']
            if step_name not in step_stats:
                step_stats[step_name] = {'success': 0, 'failed': 0, 'changed': 0}
            if step['success']:
                step_stats[step_name]['success'] += 1
                if step['metadata'].get('changed', False):
                    step_stats[step_name]['changed'] += 1
            else:
                step_stats[step_name]['failed'] += 1

    report = {
        "total_records": total,
        "language_distribution": lang_dist,
        "entity_type_distribution": entity_types,
        "total_tokens": total_tokens,
        "average_tokens_per_record": total_tokens / total if total > 0 else 0,
        "step_statistics": step_stats,
        "generated_at": datetime.now().isoformat()
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Preprocessing report saved to {report_path}")


if __name__ == "__main__":
    pipeline = NLPPreprocessingPipeline()

    test_cases = [
        "कोहली   ने  शानदार!!!  चौका मारा",
        "Virat ne amazing four मारा और six भी लगाया",
        "बुमराहने छान यॉर्कर टाकली आणि विकेट घेतला",
        "Kohli scored 4 runs with a cover drive",
        "कोहलीने अप्रतिम कव्हर ड्राइव्ह मारला आणि चेंडू चार रन के लिए गई",
    ]

    for test in test_cases:
        result = pipeline.process(test)
        print(f"\n{'='*60}")
        print(f"Original: {result.original_text}")
        print(f"Final:    {result.final_text}")
        print(f"Language: {result.detected_language} (conf: {result.language_confidence:.2f})")
        print(f"Code-mixed: {result.is_code_mixed}")
        print(f"Tokens ({result.token_count}): {result.tokens}")
        print(f"Entities: {result.entities}")
        print(f"Cricket Events: {result.cricket_events}")
        print(f"Steps:")
        for step in result.steps:
            status = "✓" if step.success else "✗"
            print(f"  {status} {step.step_name}: {step.metadata}")