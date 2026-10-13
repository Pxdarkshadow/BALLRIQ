from pathlib import Path
from backend.app.core.config import settings

def test():
    tmp_path = Path("C:/Users/Lenovo/AppData/Local/Temp/abc")
    settings.DATA_DIR = tmp_path
    
    target_path = str(tmp_path / "commentary.txt")
    resolved = Path(target_path).resolve()
    print("Resolved target:", resolved)
    print("DATA_DIR resolved:", settings.DATA_DIR.resolve())
    print("is_relative_to:", resolved.is_relative_to(settings.DATA_DIR.resolve()))

test()
