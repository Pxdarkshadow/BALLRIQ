"""Dependency-light audio helpers.

Raw audio is never treated as text: transcript analysis only runs on text a
caller supplied or a configured speech-to-text provider actually returned.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict
from pathlib import Path
from typing import Any, Protocol

from backend.app.core.config import settings
from backend.app.nlp.preprocessing.pipeline import NLPPreprocessingPipeline


class SpeechToTextProvider(Protocol):
    """Contract for a future configured speech-to-text integration."""

    def transcribe(self, audio: dict[str, Any]) -> dict[str, Any]: ...


class UnavailableSpeechToTextProvider:
    """Safe default when no local model or external provider is configured."""

    def transcribe(self, audio: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "capability_unavailable",
            "transcript": None,
            "message": "Speech-to-text is not configured; raw audio was not transcribed.",
        }


class LocalTranscriptSpeechToTextProvider:
    """Read a sidecar .txt file next to an audio path. No acoustic model."""

    def transcribe(self, audio: dict[str, Any]) -> dict[str, Any]:
        transcript_path = audio.get("transcript_path")
        audio_path = audio.get("audio_path")

        # Determine which .txt to look for
        candidate = transcript_path or (
            audio_path and str(Path(audio_path).with_suffix(".txt"))
        )
        if not candidate:
            return UnavailableSpeechToTextProvider().transcribe(audio)

        resolved = Path(candidate).resolve()
        data_dir = settings.DATA_DIR.resolve()

        # Security: reject paths outside DATA_DIR
        if not resolved.is_relative_to(data_dir):
            return {"status": "rejected", "message": "Path outside data directory."}

        if not resolved.exists():
            return UnavailableSpeechToTextProvider().transcribe(audio)

        text = resolved.read_text(encoding="utf-8").strip()
        if not text:
            return UnavailableSpeechToTextProvider().transcribe(audio)

        return {
            "status": "ok",
            "transcript": text,
            "provider": "sidecar-txt",
            "language": None,
        }


def normalize_transcript(transcript: str) -> str:
    """Normalize Unicode and whitespace without altering the speaker's words."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", transcript)).strip()


class AudioAnalysisService:
    def __init__(self, provider: SpeechToTextProvider | None = None) -> None:
        self.pipeline = NLPPreprocessingPipeline()
        self.provider = provider or LocalTranscriptSpeechToTextProvider()

    def metadata(self, audio: dict[str, Any]) -> dict[str, Any]:
        """Return caller-declared metadata; no file inspection is implied."""
        return {key: value for key, value in audio.items() if value is not None}

    def analyze_transcript(self, transcript: str) -> dict[str, Any]:
        normalized = normalize_transcript(transcript)
        result = self.pipeline.process(normalized)
        return {
            "transcript": transcript,
            "normalized_transcript": normalized,
            "nlp": {
                "final_text": result.final_text,
                "detected_language": result.detected_language,
                "language_confidence": result.language_confidence,
                "is_code_mixed": result.is_code_mixed,
                "tokens": result.tokens,
                "entities": result.entities,
                "cricket_events": result.cricket_events,
                "steps": [asdict(step) for step in result.steps],
            },
        }

    def transcribe(self, audio: dict[str, Any]) -> dict[str, Any]:
        result = self.provider.transcribe(audio)
        if result.get("status") == "ok" and result.get("transcript"):
            # Also run NLP so the endpoint is useful in one call
            result["nlp"] = self.analyze_transcript(result["transcript"])["nlp"]
        return result
