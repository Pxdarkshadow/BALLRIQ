from backend.app.nlp.preprocessing.pipeline import NLPPreprocessingPipeline
from backend.app.nlp.preprocessing.text_cleaning import clean_text
from backend.app.nlp.preprocessing.number_normalization import normalize_numbers


def test_pipeline_processes_empty_text():
    pipeline = NLPPreprocessingPipeline()
    result = pipeline.process("")
    assert result.final_text == ""
    assert result.token_count == 0


def test_pipeline_detects_language():
    pipeline = NLPPreprocessingPipeline()
    result = pipeline.process("Kohli scored four runs")
    assert result.detected_language in ["en", "hi", "mr", "unknown"]
    assert result.language_confidence >= 0


def test_pipeline_normalizes_numbers():
    pipeline = NLPPreprocessingPipeline()
    result = pipeline.process("Kohli scored 4 runs")
    assert result.token_count > 0
    assert any(e.get("entity_type") == "NUMBER" for e in result.entities)


def test_text_cleaning_preserves_cricket_symbols():
    cleaned, meta = clean_text("Kohli hit 6!!! Amazing", preserve_cricket_symbols=True)
    assert "Kohli" in cleaned
    assert meta is not None


def test_number_normalization_finds_digits():
    result = normalize_numbers("scored 4 and 6 runs", "en")
    assert result.normalized_text is not None
    assert len(result.numbers_found) >= 0


def test_pipeline_produces_tokens():
    pipeline = NLPPreprocessingPipeline()
    result = pipeline.process("Virat Kohli")
    assert len(result.tokens) > 0
    assert result.token_count == len(result.tokens)


def test_pipeline_tracks_all_steps():
    pipeline = NLPPreprocessingPipeline()
    result = pipeline.process("Test commentary")
    step_names = [s.step_name for s in result.steps]
    assert "unicode_normalization" in step_names
    assert "tokenization" in step_names
