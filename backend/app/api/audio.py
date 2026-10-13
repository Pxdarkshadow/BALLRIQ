"""Audio endpoints for metadata, transcript analysis, and STT capability status."""
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

from backend.app.audio.service import AudioAnalysisService

router = APIRouter(prefix="/api/audio", tags=["audio"])
service = AudioAnalysisService()


class AudioRecord(BaseModel):
    source_id: str | None = None
    filename: str | None = None
    content_type: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)
    duration_seconds: float | None = Field(default=None, ge=0)
    audio_path: str | None = None
    transcript_path: str | None = None


class TranscriptRequest(AudioRecord):
    transcript: str = Field(min_length=1)


@router.post("/metadata")
async def audio_metadata(audio: AudioRecord):
    """Return submitted audio metadata without reading or transcribing media."""
    return {"metadata": service.metadata(audio.model_dump())}


@router.post("/analyze")
async def analyze_transcript(request: TranscriptRequest):
    """Normalize and run existing NLP only on an explicitly supplied transcript."""
    return {
        "metadata": service.metadata(request.model_dump(exclude={"transcript"})),
        "transcript_status": "provided",
        **service.analyze_transcript(request.transcript),
    }


@router.post("/transcribe")
async def transcribe_audio(audio: AudioRecord, response: Response):
    """Attempt STT through a configured provider; default is explicitly unavailable."""
    result = service.transcribe(audio.model_dump())
    if result["status"] == "capability_unavailable":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif result["status"] == "rejected":
        response.status_code = status.HTTP_400_BAD_REQUEST
    return {"metadata": service.metadata(audio.model_dump()), **result}
