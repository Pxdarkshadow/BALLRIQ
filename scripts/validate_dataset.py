#!/usr/bin/env python3
"""
Data Validation Script for BALLRIQ Cricket Commentary Dataset

Validates raw data quality and produces a JSON report.
Checks: missing text, invalid languages, missing labels, duplicates, invalid timestamps, invalid match IDs, invalid event labels, encoding problems.
"""

import json
import csv
import re
from pathlib import Path
from datetime import datetime
from collections import Counter
import sys

# Valid values
VALID_LANGUAGES = {"hi", "mr", "en", "hi_en", "mr_en"}
VALID_EVENT_LABELS = {"FOUR", "SIX", "WICKET", "DOT", "SINGLE", "DOUBLE", "TRIPLE", "WIDE", "NO_BALL", "FIFTY", "CENTURY", "OTHER"}
VALID_DISMISSAL_TYPES = {"bowled", "caught", "lbw", "run_out", "stumped", "hit_wicket", None, "null", ""}
VALID_FORMATS = {"T20", "ODI", "Test"}

# Regex patterns
TIMESTAMP_PATTERN = re.compile(r"^\d{2}:\d{2}:\d{2}$")
MATCH_ID_PATTERN = re.compile(r"^M\d{3}$")
COMMENTARY_ID_PATTERN = re.compile(r"^M\d{3}_C_\d{4,5}$")
AUDIO_ID_PATTERN = re.compile(r"^M\d{3}_A_\d{3}$")

def load_match_ids(matches_path):
    """Load valid match IDs from matches.csv"""
    match_ids = set()
    with open(matches_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            match_ids.add(row['match_id'])
    return match_ids

def validate_commentary(commentary_path, valid_match_ids):
    """Validate commentary.jsonl"""
    results = {
        "total_records": 0,
        "valid_records": 0,
        "duplicate_records": 0,
        "missing_text": 0,
        "invalid_language": 0,
        "missing_label": 0,
        "invalid_event_label": 0,
        "invalid_timestamp": 0,
        "invalid_match_id": 0,
        "invalid_commentary_id": 0,
        "encoding_errors": 0,
        "invalid_dismissal_type": 0,
        "confidence_issues": 0,
        "issues": []
    }

    seen_ids = set()

    with open(commentary_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            results["total_records"] += 1
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                results["encoding_errors"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "encoding_error",
                    "message": str(e)
                })
                continue

            # Check duplicate commentary_id
            cid = record.get("commentary_id", "")
            if cid in seen_ids:
                results["duplicate_records"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "duplicate_id",
                    "commentary_id": cid
                })
            else:
                seen_ids.add(cid)

            # Validate commentary_id format
            if not COMMENTARY_ID_PATTERN.match(cid):
                results["invalid_commentary_id"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "invalid_commentary_id",
                    "commentary_id": cid
                })

            # Missing text
            if not record.get("original_text", "").strip():
                results["missing_text"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "missing_text",
                    "commentary_id": cid
                })

            # Invalid language
            lang = record.get("language", "")
            if lang not in VALID_LANGUAGES:
                results["invalid_language"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "invalid_language",
                    "commentary_id": cid,
                    "value": lang
                })

            # Missing label
            if not record.get("event_label"):
                results["missing_label"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "missing_label",
                    "commentary_id": cid
                })
            elif record.get("event_label") not in VALID_EVENT_LABELS:
                results["invalid_event_label"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "invalid_event_label",
                    "commentary_id": cid,
                    "value": record.get("event_label")
                })

            # Invalid timestamp
            ts = record.get("timestamp", "")
            if not TIMESTAMP_PATTERN.match(ts):
                results["invalid_timestamp"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "invalid_timestamp",
                    "commentary_id": cid,
                    "value": ts
                })

            # Invalid match_id
            mid = record.get("match_id", "")
            if mid not in valid_match_ids:
                results["invalid_match_id"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "invalid_match_id",
                    "commentary_id": cid,
                    "value": mid
                })

            # Invalid dismissal_type
            dismissal = record.get("dismissal_type")
            if dismissal and dismissal not in VALID_DISMISSAL_TYPES:
                results["invalid_dismissal_type"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "invalid_dismissal_type",
                    "commentary_id": cid,
                    "value": dismissal
                })

            # Confidence check
            conf = record.get("confidence")
            if conf is not None and (not isinstance(conf, (int, float)) or conf < 0 or conf > 1):
                results["confidence_issues"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "invalid_confidence",
                    "commentary_id": cid,
                    "value": conf
                })

            results["valid_records"] += 1

    return results

def validate_audio(audio_path, valid_match_ids):
    """Validate audio_metadata.jsonl"""
    results = {
        "total_records": 0,
        "valid_records": 0,
        "duplicate_records": 0,
        "missing_transcript": 0,
        "invalid_language": 0,
        "invalid_timestamp": 0,
        "invalid_match_id": 0,
        "invalid_audio_id": 0,
        "encoding_errors": 0,
        "duration_issues": 0,
        "issues": []
    }

    seen_ids = set()

    with open(audio_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            results["total_records"] += 1
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                results["encoding_errors"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "encoding_error",
                    "message": str(e)
                })
                continue

            aid = record.get("audio_id", "")
            if aid in seen_ids:
                results["duplicate_records"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "duplicate_id",
                    "audio_id": aid
                })
            else:
                seen_ids.add(aid)

            if not AUDIO_ID_PATTERN.match(aid):
                results["invalid_audio_id"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "invalid_audio_id",
                    "audio_id": aid
                })

            if not record.get("transcript", "").strip():
                results["missing_transcript"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "missing_transcript",
                    "audio_id": aid
                })

            lang = record.get("language", "")
            if lang not in {"hi", "mr", "en"}:
                results["invalid_language"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "invalid_language",
                    "audio_id": aid,
                    "value": lang
                })

            for ts_field in ["start_time", "end_time"]:
                ts = record.get(ts_field, "")
                if not TIMESTAMP_PATTERN.match(ts):
                    results["invalid_timestamp"] += 1
                    results["issues"].append({
                        "line": line_num,
                        "type": "invalid_timestamp",
                        "audio_id": aid,
                        "field": ts_field,
                        "value": ts
                    })

            mid = record.get("match_id", "")
            if mid not in valid_match_ids:
                results["invalid_match_id"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "invalid_match_id",
                    "audio_id": aid,
                    "value": mid
                })

            dur = record.get("duration")
            if dur is not None and (not isinstance(dur, (int, float)) or dur <= 0):
                results["duration_issues"] += 1
                results["issues"].append({
                    "line": line_num,
                    "type": "invalid_duration",
                    "audio_id": aid,
                    "value": dur
                })

            results["valid_records"] += 1

    return results

def validate_matches(matches_path):
    """Validate matches.csv"""
    results = {
        "total_records": 0,
        "valid_records": 0,
        "duplicate_match_id": 0,
        "invalid_date": 0,
        "invalid_format": 0,
        "missing_fields": 0,
        "issues": []
    }

    seen_ids = set()

    with open(matches_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results["total_records"] += 1

            mid = row.get("match_id", "")
            if mid in seen_ids:
                results["duplicate_match_id"] += 1
                results["issues"].append({
                    "type": "duplicate_match_id",
                    "match_id": mid
                })
            else:
                seen_ids.add(mid)

            # Validate date
            try:
                datetime.strptime(row.get("date", ""), "%Y-%m-%d")
            except ValueError:
                results["invalid_date"] += 1
                results["issues"].append({
                    "type": "invalid_date",
                    "match_id": mid,
                    "value": row.get("date")
                })

            # Validate format
            if row.get("format") not in VALID_FORMATS:
                results["invalid_format"] += 1
                results["issues"].append({
                    "type": "invalid_format",
                    "match_id": mid,
                    "value": row.get("format")
                })

            # Check required fields
            required = ["match_id", "date", "format", "tournament", "venue", "team_a", "team_b", "winner", "result"]
            for field in required:
                if not row.get(field, "").strip():
                    results["missing_fields"] += 1
                    results["issues"].append({
                        "type": "missing_field",
                        "match_id": mid,
                        "field": field
                    })

            results["valid_records"] += 1

    return results

def validate_players(players_path):
    """Validate players.csv"""
    results = {
        "total_records": 0,
        "valid_records": 0,
        "duplicate_player_id": 0,
        "missing_fields": 0,
        "issues": []
    }

    seen_ids = set()

    with open(players_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results["total_records"] += 1

            pid = row.get("player_id", "")
            if pid in seen_ids:
                results["duplicate_player_id"] += 1
                results["issues"].append({
                    "type": "duplicate_player_id",
                    "player_id": pid
                })
            else:
                seen_ids.add(pid)

            required = ["player_id", "name", "team", "role"]
            for field in required:
                if not row.get(field, "").strip():
                    results["missing_fields"] += 1
                    results["issues"].append({
                        "type": "missing_field",
                        "player_id": pid,
                        "field": field
                    })

            results["valid_records"] += 1

    return results

def validate_innings(innings_path, valid_match_ids):
    """Validate innings.csv"""
    results = {
        "total_records": 0,
        "valid_records": 0,
        "invalid_match_id": 0,
        "invalid_innings_number": 0,
        "issues": []
    }

    with open(innings_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results["total_records"] += 1

            mid = row.get("match_id", "")
            if mid not in valid_match_ids:
                results["invalid_match_id"] += 1
                results["issues"].append({
                    "type": "invalid_match_id",
                    "innings_id": row.get("innings_id"),
                    "value": mid
                })

            try:
                inn_num = int(row.get("innings_number", 0))
                if inn_num not in [1, 2]:
                    results["invalid_innings_number"] += 1
                    results["issues"].append({
                        "type": "invalid_innings_number",
                        "innings_id": row.get("innings_id"),
                        "value": inn_num
                    })
            except ValueError:
                results["invalid_innings_number"] += 1
                results["issues"].append({
                    "type": "invalid_innings_number",
                    "innings_id": row.get("innings_id"),
                    "value": row.get("innings_number")
                })

            results["valid_records"] += 1

    return results

def main():
    base_path = Path(__file__).parent.parent / "data" / "raw"

    # Load valid match IDs first
    matches_path = base_path / "matches" / "matches.csv"
    valid_match_ids = load_match_ids(matches_path)
    print(f"Loaded {len(valid_match_ids)} valid match IDs")

    # Validate each dataset
    print("Validating matches...")
    match_results = validate_matches(matches_path)

    print("Validating players...")
    players_path = base_path / "matches" / "players.csv"
    player_results = validate_players(players_path)

    print("Validating innings...")
    innings_path = base_path / "matches" / "innings.csv"
    innings_results = validate_innings(innings_path, valid_match_ids)

    print("Validating commentary...")
    commentary_path = base_path / "commentary" / "commentary.jsonl"
    commentary_results = validate_commentary(commentary_path, valid_match_ids)

    print("Validating audio...")
    audio_path = base_path / "audio" / "audio_metadata.jsonl"
    audio_results = validate_audio(audio_path, valid_match_ids)

    # Aggregate report
    report = {
        "validation_timestamp": datetime.now().isoformat(),
        "matches": match_results,
        "players": player_results,
        "innings": innings_results,
        "commentary": commentary_results,
        "audio": audio_results,
        "summary": {
            "total_matches": match_results["total_records"],
            "total_players": player_results["total_records"],
            "total_innings": innings_results["total_records"],
            "total_commentary": commentary_results["total_records"],
            "total_audio": audio_results["total_records"],
            "total_issues": (
                len(match_results["issues"]) +
                len(player_results["issues"]) +
                len(innings_results["issues"]) +
                len(commentary_results["issues"]) +
                len(audio_results["issues"])
            )
        }
    }

    # Output report
    output_path = Path(__file__).parent.parent / "reports" / "data_quality" / "data_quality_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nValidation complete. Report saved to {output_path}")
    print(f"Summary:")
    print(f"  Matches: {match_results['valid_records']}/{match_results['total_records']} valid")
    print(f"  Players: {player_results['valid_records']}/{player_results['total_records']} valid")
    print(f"  Innings: {innings_results['valid_records']}/{innings_results['total_records']} valid")
    print(f"  Commentary: {commentary_results['valid_records']}/{commentary_results['total_records']} valid")
    print(f"  Audio: {audio_results['valid_records']}/{audio_results['total_records']} valid")
    print(f"  Total issues: {report['summary']['total_issues']}")

    return 0 if report['summary']['total_issues'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())