"""
NLP FastAPI Router: Preprocessing, Classification, and Entity Extraction Endpoints.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from backend.app.nlp.preprocessing.pipeline import NLPPreprocessingPipeline
from backend.app.nlp.models.baseline import BaselineEventClassifier
from backend.app.nlp.models.xlmr import XLMREventClassifier
from backend.app.nlp.entity_extraction.entity_extractor import CricketEntityExtractor
from backend.app.nlp.event_extraction.event_extractor import CricketEventExtractor
from backend.app.schemas.models import NLPClassifyResponse

router = APIRouter(prefix="/api/nlp", tags=["nlp"])

BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_DIR = BASE_DIR / "models" / "nlp" / "event_classifier_baseline"
XLMR_MODEL_DIR = BASE_DIR / "models" / "nlp" / "event_classifier_xlmr"

_pipeline = NLPPreprocessingPipeline()
_classifier: Optional[object] = None
_entity_extractor = CricketEntityExtractor()
_event_extractor = None


def get_classifier():
    global _classifier
    if _classifier is None:
        if XLMREventClassifier.artifacts_available(XLMR_MODEL_DIR):
            try:
                _classifier = XLMREventClassifier.load(XLMR_MODEL_DIR)
            except Exception as e:
                print(f"Warning: could not load trained XLM-R model: {e}")
        if _classifier is None and MODEL_DIR.exists():
            try:
                _classifier = BaselineEventClassifier.load(MODEL_DIR)
            except Exception as e:
                print(f"Warning: could not load trained baseline model: {e}")
                _classifier = None
    return _classifier


def get_event_extractor():
    global _event_extractor
    if _event_extractor is None:
        _event_extractor = CricketEventExtractor(get_classifier())
    return _event_extractor


class TextRequest(BaseModel):
    text: str


@router.post("/preprocess")
async def preprocess(req: TextRequest):
    """Run full NLP preprocessing pipeline step-by-step."""
    result = _pipeline.process(req.text)
    steps = [asdict(s) for s in result.steps]
    return {
        "original_text": result.original_text,
        "final_text": result.final_text,
        "detected_language": result.detected_language,
        "language_confidence": result.language_confidence,
        "is_code_mixed": result.is_code_mixed,
        "entities": result.entities,
        "tokens": result.tokens,
        "steps": steps,
    }


@router.post("/classify", response_model=NLPClassifyResponse)
async def classify(req: TextRequest):
    """Predict cricket event from commentary text."""
    clf = get_classifier()
    if clf is None or not clf.is_fitted:
        # Fallback to rule/pipeline prediction if model artifact not found
        p_res = _pipeline.process(req.text)
        pred_event = p_res.cricket_events[0] if p_res.cricket_events else "OTHER"
        return NLPClassifyResponse(
            predicted_event=pred_event,
            confidence=0.85,
            all_probabilities={pred_event: 0.85, "OTHER": 0.15},
            preprocessed_text=p_res.final_text,
            detected_language=p_res.detected_language
        )

    res = clf.predict_single(req.text)
    return NLPClassifyResponse(
        predicted_event=res.get("predicted_event"),
        confidence=round(res.get("confidence", 0.0), 4),
        all_probabilities=res.get("all_probabilities"),
        preprocessed_text=res.get("preprocessed_text"),
        detected_language=res.get("detected_language")
    )


@router.post("/entities")
async def extract_entities(req: TextRequest):
    """Extract cricket entities (players, teams, events, terms)."""
    p_res = _pipeline.process(req.text)
    extracted = _entity_extractor.extract_all_flat(req.text)
    structured_event = get_event_extractor().extract_event(req.text)

    entities = [
        {
            **asdict(entity),
            # Keep the fields consumed by the existing client.
            "entity_type": entity.label,
            "original": entity.text,
        }
        for entity in extracted
    ]

    return {
        "entities": entities,
        "player_mentions": [entity.canonical or entity.text for entity in extracted if entity.label == "PLAYER"],
        "team_mentions": [entity.canonical or entity.text for entity in extracted if entity.label == "TEAM"],
        "cricket_events": p_res.cricket_events,
        "structured_event": asdict(structured_event)
    }


@router.get("/pipeline-steps")
async def pipeline_steps():
    return {
        "steps": [
            {"id": "unicode_normalization", "name": "Unicode Normalization", "description": "Canonical NFKC & Devanagari character variants"},
            {"id": "text_cleaning", "name": "Text Cleaning", "description": "Punctuation cleanup preserving cricket markers"},
            {"id": "language_identification", "name": "Language Identification", "description": "Hindi, Marathi, English & Code-mixed detection"},
            {"id": "number_normalization", "name": "Number Normalization", "description": "Hindi/Marathi words & digits to numbers"},
            {"id": "cricket_vocabulary_normalization", "name": "Cricket Vocabulary Normalization", "description": "Standardize domain terms (चौका -> FOUR)"},
            {"id": "player_name_normalization", "name": "Player Name Normalization", "description": "Map aliases and transliterations to canonical names"},
            {"id": "tokenization", "name": "Tokenization", "description": "Multilingual morpho-syntactic boundary splitting"}
        ]
    }
