"""Application settings loaded from environment / .env file."""
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# D:\miniproject\backend\app\core\config.py -> project root is 4 levels up
BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

    DATABASE_URL: str = f"sqlite+aiosqlite:///{(BASE_DIR / 'data' / 'ballriq.db').as_posix()}"
    MODEL_DIR: Path = BASE_DIR / "models"
    DATA_DIR: Path = BASE_DIR / "data"

    LLM_API_KEY: str | None = None
    LLM_BASE_URL: str = ""

    HOST: str = "0.0.0.0"
    PORT: int = 8000


settings = Settings()