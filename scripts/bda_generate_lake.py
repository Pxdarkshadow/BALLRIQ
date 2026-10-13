"""
BDA Lakehouse Generator: Converts CSV/JSONL cricket data into Partitioned Parquet Lakehouse.
Storage Structure:
  data/lake/
    ├── matches/ (partitioned by format)
    ├── commentary/ (partitioned by language)
    ├── batting_stats/
    ├── bowling_stats/
    ├── players/
    └── ball_events/
"""
from pathlib import Path
import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
LAKE_DIR = DATA_DIR / "lake"


def generate_lakehouse():
    LAKE_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating Parquet Lakehouse in", LAKE_DIR)

    # 1. Matches
    matches_csv = RAW_DIR / "matches" / "matches.csv"
    if matches_csv.exists():
        df_matches = pd.read_csv(matches_csv)
        matches_lake = LAKE_DIR / "matches"
        df_matches.to_parquet(matches_lake, partition_cols=["format"], index=False)
        print(f"-> Matches lake generated: {len(df_matches)} rows, partitioned by format")

    # 2. Commentary
    commentary_jsonl = RAW_DIR / "commentary" / "commentary.jsonl"
    if commentary_jsonl.exists():
        records = []
        with open(commentary_jsonl, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        df_comm = pd.DataFrame(records)
        if not df_comm.empty:
            # Ensure player_mentions and team_mentions are strings for parquet compatibility
            if "player_mentions" in df_comm.columns:
                df_comm["player_mentions"] = df_comm["player_mentions"].apply(lambda x: json.dumps(x) if isinstance(x, list) else str(x))
            if "team_mentions" in df_comm.columns:
                df_comm["team_mentions"] = df_comm["team_mentions"].apply(lambda x: json.dumps(x) if isinstance(x, list) else str(x))

            comm_lake = LAKE_DIR / "commentary"
            df_comm.to_parquet(comm_lake, partition_cols=["language"], index=False)
            print(f"-> Commentary lake generated: {len(df_comm)} rows, partitioned by language")

    # 3. Batting Stats
    batting_csv = RAW_DIR / "matches" / "batting_stats.csv"
    if batting_csv.exists():
        df_batting = pd.read_csv(batting_csv)
        df_batting.to_parquet(LAKE_DIR / "batting_stats.parquet", index=False)
        print(f"-> Batting stats lake generated: {len(df_batting)} rows")

    # 4. Bowling Stats
    bowling_csv = RAW_DIR / "matches" / "bowling_stats.csv"
    if bowling_csv.exists():
        df_bowling = pd.read_csv(bowling_csv)
        df_bowling.to_parquet(LAKE_DIR / "bowling_stats.parquet", index=False)
        print(f"-> Bowling stats lake generated: {len(df_bowling)} rows")

    # 5. Players & Profiles
    players_csv = RAW_DIR / "matches" / "players.csv"
    if players_csv.exists():
        df_players = pd.read_csv(players_csv)
        df_players.to_parquet(LAKE_DIR / "players.parquet", index=False)
        print(f"-> Players lake generated: {len(df_players)} rows")

    # 6. Synthesize Granular Ball Events Table from Commentary & Match Data for BDA Analytics
    if commentary_jsonl.exists():
        ball_events = []
        for r in records:
            event_type = r.get("event_label", "OTHER")
            over = int(r.get("over", 0))
            ball = int(r.get("ball", 1))
            runs = 0
            if event_type == "FOUR":
                runs = 4
            elif event_type == "SIX":
                runs = 6
            elif event_type == "SINGLE":
                runs = 1
            elif event_type == "DOUBLE":
                runs = 2
            elif event_type == "TRIPLE":
                runs = 3
            elif event_type == "DOT":
                runs = 0

            # Match phase
            if over < 6:
                phase = "Powerplay"
            elif over < 16:
                phase = "Middle"
            else:
                phase = "Death"

            ball_events.append({
                "commentary_id": r.get("commentary_id", ""),
                "match_id": r.get("match_id", ""),
                "over": over,
                "ball": ball,
                "phase": phase,
                "language": r.get("language", "en"),
                "event_label": event_type,
                "runs": runs,
                "is_wicket": 1 if event_type == "WICKET" else 0,
                "is_boundary": 1 if event_type in ["FOUR", "SIX"] else 0,
                "is_dot": 1 if event_type == "DOT" else 0,
                "text_length": len(r.get("original_text", "")),
            })
        df_events = pd.DataFrame(ball_events)
        df_events.to_parquet(LAKE_DIR / "ball_events.parquet", index=False)
        print(f"-> Ball Events table generated: {len(df_events)} rows")

    print("\nParquet Lakehouse generated successfully!")


if __name__ == "__main__":
    generate_lakehouse()
