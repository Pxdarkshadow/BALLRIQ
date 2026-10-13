from pathlib import Path
from backend.app.core.config import settings
from backend.app.audio.service import LocalTranscriptSpeechToTextProvider
import tempfile

def test():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        settings.DATA_DIR = tmp_path
        
        txt_file = tmp_path / "commentary.txt"
        txt_file.write_text("Kohli hits a six", encoding="utf-8")
        
        provider = LocalTranscriptSpeechToTextProvider()
        res = provider.transcribe({"audio_path": str(tmp_path / "commentary.wav")})
        print(res)

test()
