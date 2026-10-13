from fastapi.testclient import TestClient
from pathlib import Path
import pytest

from backend.app.main import app
from backend.app.audio.service import normalize_transcript
from backend.app.core.config import settings


client = TestClient(app)


def test_normalize_transcript_preserves_words():
    assert normalize_transcript("  Virat\tKohli  scored four  ") == "Virat Kohli scored four"


def test_analyze_only_uses_provided_transcript():
    response = client.post(
        "/api/audio/analyze",
        json={"filename": "commentary.wav", "transcript": "Virat Kohli hit a four"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["transcript_status"] == "provided"
    assert body["normalized_transcript"] == "Virat Kohli hit a four"
    assert body["nlp"]["tokens"]


def test_transcription_reports_unavailable_capability():
    response = client.post("/api/audio/transcribe", json={"filename": "commentary.wav"})
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "capability_unavailable"
    assert body["transcript"] is None


def test_transcription_reads_sidecar_file_if_in_data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path)
    txt_file = tmp_path / "commentary.txt"
    txt_file.write_text("Kohli hits a six", encoding="utf-8")

    response = client.post(
        "/api/audio/transcribe", 
        json={"audio_path": str(tmp_path / "commentary.wav")}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["transcript"] == "Kohli hits a six"
    assert body["provider"] == "sidecar-txt"
    assert "nlp" in body
    assert body["nlp"]["final_text"]


def test_transcription_rejects_paths_outside_data_dir(tmp_path, monkeypatch):
    # Create mock DATA_DIR inside tmp_path
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setattr(settings, "DATA_DIR", data_dir)
    
    # Secret file outside DATA_DIR
    secret_file = tmp_path / "passwords.txt"
    secret_file.write_text("secret_password", encoding="utf-8")
