"""FastAPI dependency helpers."""
from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.db.database import SessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


def get_data_dir() -> Path:
    return settings.DATA_DIR


def get_model_dir() -> Path:
    return settings.MODEL_DIR