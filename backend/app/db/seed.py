"""Seed the SQLite DB from raw CSVs and JSONL files (sync sqlite3).

Run: python -m backend.app.db.seed
Fresh DB is rebuilt per run (tables dropped/recreated).
"""
import csv
import json
import sqlite3
from pathlib import Path

from backend.app.core.config import settings

DATA_DIR = settings.DATA_DIR
MATCHES = DATA_DIR / "raw" / "matches"
COMMENTARY = DATA_DIR / "raw" / "commentary" / "commentary.jsonl"
AUDIO = DATA_DIR / "raw" / "audio" / "audio_metadata.jsonl"
DB_PATH = settings.DATA_DIR / "ballriq.db"

TABLES = [
    """CREATE TABLE IF NOT EXISTS matches (
        match_id TEXT PRIMARY KEY,
        date TEXT, format TEXT, tournament TEXT, venue TEXT,
        team_a TEXT, team_b TEXT, winner TEXT, result TEXT,
        toss_winner TEXT, toss_decision TEXT)""",
    """CREATE TABLE IF NOT EXISTS players (
        player_id TEXT PRIMARY KEY,
        name TEXT, team TEXT, role TEXT,
        batting_style TEXT, bowling_style TEXT)""",
    """CREATE TABLE IF NOT EXISTS innings (
        id TEXT PRIMARY KEY,
        match_id TEXT NOT NULL REFERENCES matches(match_id),
        innings_number INTEGER, batting_team TEXT, bowling_team TEXT,
        total_runs INTEGER, wickets INTEGER, overs REAL, target INTEGER)""",
    """CREATE TABLE IF NOT EXISTS batting_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id TEXT, match_id TEXT NOT NULL REFERENCES matches(match_id),
        innings_id TEXT NOT NULL REFERENCES innings(id),
        player_id TEXT REFERENCES players(player_id),
        runs INTEGER, balls INTEGER, fours INTEGER, sixes INTEGER,
        strike_rate REAL, dismissal TEXT)""",
    """CREATE TABLE IF NOT EXISTS bowling_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id TEXT, match_id TEXT NOT NULL REFERENCES matches(match_id),
        innings_id TEXT NOT NULL REFERENCES innings(id),
        player_id TEXT REFERENCES players(player_id),
        overs REAL, runs_conceded INTEGER, wickets INTEGER,
        economy REAL, wides INTEGER, no_balls INTEGER)""",
    """CREATE TABLE IF NOT EXISTS commentary (
        commentary_id TEXT PRIMARY KEY,
        match_id TEXT NOT NULL REFERENCES matches(match_id),
        language TEXT, original_text TEXT, normalized_text TEXT,
        timestamp TEXT, over INTEGER, ball INTEGER,
        player_mentions TEXT, team_mentions TEXT,
        event_label TEXT, dismissal_type TEXT,
        is_synthetic INTEGER, translator_id TEXT, confidence REAL)""",
    """CREATE TABLE IF NOT EXISTS audio (
        audio_id TEXT PRIMARY KEY,
        match_id TEXT NOT NULL REFERENCES matches(match_id),
        language TEXT, audio_path TEXT, duration REAL, transcript TEXT,
        start_time TEXT, end_time TEXT, over INTEGER, ball INTEGER,
        speaker TEXT, source_type TEXT, quality_score REAL)""",
    """CREATE TABLE IF NOT EXISTS extracted_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id TEXT NOT NULL REFERENCES matches(match_id),
        event_type TEXT, event_subtype TEXT, player TEXT, team TEXT,
        bowler TEXT, batter TEXT, fielder TEXT, dismissal_type TEXT, runs INTEGER,
        over INTEGER, ball INTEGER, importance_score REAL, confidence REAL, raw_text TEXT,
        commentary_id TEXT REFERENCES commentary(commentary_id))""",
]

INT_FIELDS = {"is_synthetic"}


def load_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def field(row: dict, col: str):
    """Coerce a CSV/JSON value into a sqlite-friendly value: '' -> None, JSON-encode lists."""
    v = row.get(col)
    if v is None:
        return None
    if isinstance(v, list):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    s = v.strip() if isinstance(v, str) else v
    if s == "":
        return None
    return s


def insert(conn: sqlite3.Connection, table: str, row: dict) -> int:
    """Insert one row, projecting row keys that exist on the target table."""
    cols = [c for c in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    col_names = {c[1] for c in cols}
    cols_in_row = [(c, field(row, c)) for c in col_names if c in row]
    if not cols_in_row:
        return 0
    names = ", ".join(c for c, _ in cols_in_row)
    placeholders = ", ".join("?" for _ in cols_in_row)
    conn.execute(
        f"INSERT OR IGNORE INTO {table} ({names}) VALUES ({placeholders})",
        [v for _, v in cols_in_row],
    )
    return 1


def seed() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        for ddl in TABLES:
            conn.execute(f"DROP TABLE IF EXISTS {ddl.split('(')[0].split()[-1]}")
        for ddl in TABLES:
            conn.execute(ddl)
        conn.commit()

        counts = {}
        for csv_name, table, key_map in [
            ("matches.csv", "matches", {}),
            ("players.csv", "players", {}),
            ("innings.csv", "innings", {"innings_id": "id"}),
            ("batting_stats.csv", "batting_stats", {}),
            ("bowling_stats.csv", "bowling_stats", {}),
        ]:
            rows = load_csv(MATCHES / csv_name)
            renamed = [{key_map.get(k, k): v for k, v in r.items()} for r in rows]
            counts[table] = sum(insert(conn, table, r) for r in renamed)

        for table, path in [("commentary", COMMENTARY), ("audio", AUDIO)]:
            rows = load_jsonl(path)
            counts[table] = sum(insert(conn, table, r) for r in rows)

        conn.commit()
        for table, n in counts.items():
            print(f"{table}: {n} rows inserted")
    finally:
        conn.close()


if __name__ == "__main__":
    seed()