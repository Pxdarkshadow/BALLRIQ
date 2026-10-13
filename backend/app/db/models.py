"""SQLAlchemy ORM models mirroring the raw BALLRIQ data columns (CSV/JSONL)."""
from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base


class Match(Base):
    __tablename__ = "matches"

    match_id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[str | None] = mapped_column(String, nullable=True)
    format: Mapped[str | None] = mapped_column(String, nullable=True)
    tournament: Mapped[str | None] = mapped_column(String, nullable=True)
    venue: Mapped[str | None] = mapped_column(String, nullable=True)
    team_a: Mapped[str | None] = mapped_column(String, nullable=True)
    team_b: Mapped[str | None] = mapped_column(String, nullable=True)
    winner: Mapped[str | None] = mapped_column(String, nullable=True)
    result: Mapped[str | None] = mapped_column(String, nullable=True)
    toss_winner: Mapped[str | None] = mapped_column(String, nullable=True)
    toss_decision: Mapped[str | None] = mapped_column(String, nullable=True)


class Player(Base):
    __tablename__ = "players"

    player_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    team: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    batting_style: Mapped[str | None] = mapped_column(String, nullable=True)
    bowling_style: Mapped[str | None] = mapped_column(String, nullable=True)


class Innings(Base):
    __tablename__ = "innings"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # natural key = innings_id
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.match_id"))
    innings_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    batting_team: Mapped[str | None] = mapped_column(String, nullable=True)
    bowling_team: Mapped[str | None] = mapped_column(String, nullable=True)
    total_runs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wickets: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overs: Mapped[float | None] = mapped_column(Float, nullable=True)
    target: Mapped[int | None] = mapped_column(Integer, nullable=True)


class BattingStat(Base):
    __tablename__ = "batting_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: Mapped[str | None] = mapped_column(String, nullable=True)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.match_id"))
    innings_id: Mapped[str] = mapped_column(ForeignKey("innings.id"))
    player_id: Mapped[str | None] = mapped_column(ForeignKey("players.player_id"), nullable=True)
    runs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    balls: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sixes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    strike_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    dismissal: Mapped[str | None] = mapped_column(String, nullable=True)


class BowlingStat(Base):
    __tablename__ = "bowling_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: Mapped[str | None] = mapped_column(String, nullable=True)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.match_id"))
    innings_id: Mapped[str] = mapped_column(ForeignKey("innings.id"))
    player_id: Mapped[str | None] = mapped_column(ForeignKey("players.player_id"), nullable=True)
    overs: Mapped[float | None] = mapped_column(Float, nullable=True)
    runs_conceded: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wickets: Mapped[int | None] = mapped_column(Integer, nullable=True)
    economy: Mapped[float | None] = mapped_column(Float, nullable=True)
    wides: Mapped[int | None] = mapped_column(Integer, nullable=True)
    no_balls: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Commentary(Base):
    __tablename__ = "commentary"

    commentary_id: Mapped[str] = mapped_column(String, primary_key=True)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.match_id"))
    language: Mapped[str | None] = mapped_column(String, nullable=True)
    original_text: Mapped[str | None] = mapped_column(String, nullable=True)
    normalized_text: Mapped[str | None] = mapped_column(String, nullable=True)
    timestamp: Mapped[str | None] = mapped_column(String, nullable=True)
    over: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ball: Mapped[int | None] = mapped_column(Integer, nullable=True)
    player_mentions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    team_mentions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    event_label: Mapped[str | None] = mapped_column(String, nullable=True)
    dismissal_type: Mapped[str | None] = mapped_column(String, nullable=True)
    is_synthetic: Mapped[int | None] = mapped_column(Integer, nullable=True)
    translator_id: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)


class Audio(Base):
    __tablename__ = "audio"

    audio_id: Mapped[str] = mapped_column(String, primary_key=True)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.match_id"))
    language: Mapped[str | None] = mapped_column(String, nullable=True)
    audio_path: Mapped[str | None] = mapped_column(String, nullable=True)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    transcript: Mapped[str | None] = mapped_column(String, nullable=True)
    start_time: Mapped[str | None] = mapped_column(String, nullable=True)
    end_time: Mapped[str | None] = mapped_column(String, nullable=True)
    over: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ball: Mapped[int | None] = mapped_column(Integer, nullable=True)
    speaker: Mapped[str | None] = mapped_column(String, nullable=True)
    source_type: Mapped[str | None] = mapped_column(String, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)


class ExtractedEvent(Base):
    __tablename__ = "extracted_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.match_id"))
    event_type: Mapped[str | None] = mapped_column(String, nullable=True)
    event_subtype: Mapped[str | None] = mapped_column(String, nullable=True)
    player: Mapped[str | None] = mapped_column(String, nullable=True)
    team: Mapped[str | None] = mapped_column(String, nullable=True)
    bowler: Mapped[str | None] = mapped_column(String, nullable=True)
    batter: Mapped[str | None] = mapped_column(String, nullable=True)
    fielder: Mapped[str | None] = mapped_column(String, nullable=True)
    dismissal_type: Mapped[str | None] = mapped_column(String, nullable=True)
    runs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    over: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ball: Mapped[int | None] = mapped_column(Integer, nullable=True)
    importance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(String, nullable=True)
    commentary_id: Mapped[str | None] = mapped_column(ForeignKey("commentary.commentary_id"), nullable=True)