#!/usr/bin/env python3
"""
Build IR document collection for BALLRIQ hybrid search.

Creates documents from:
- Commentary records
- Match summaries
- Player statistics
- Structured events
"""

import json
import csv
from pathlib import Path
from collections import defaultdict
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.nlp.preprocessing.pipeline import NLPPreprocessingPipeline


def load_jsonl(path):
    """Load JSONL file."""
    records = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_csv(path):
    """Load CSV file."""
    records = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def create_commentary_documents(commentary_records, pipeline):
    """Create documents from commentary records."""
    documents = []
    print(f"Creating commentary documents from {len(commentary_records)} records...")

    for i, record in enumerate(commentary_records):
        text = record.get('original_text', '')
        result = pipeline.process(text)

        # Build content combining original and preprocessed
        content = f"{text} {result.final_text}"

        doc = {
            "document_id": f"{record['commentary_id']}",
            "content": content,
            "language": record.get('language', 'unknown'),
            "match_id": record.get('match_id', ''),
            "over": record.get('over', 0),
            "ball": record.get('ball', 0),
            "event_type": record.get('event_label', 'OTHER'),
            "players": record.get('player_mentions', []),
            "teams": record.get('team_mentions', []),
            "timestamp": record.get('timestamp', ''),
            "source": "commentary",
            "dismissal_type": record.get('dismissal_type'),
            "preprocessed_text": result.final_text,
            "detected_language": result.detected_language,
            "entities": result.entities,
            "cricket_events": result.cricket_events,
            "confidence": record.get('confidence', 0.9)
        }
        documents.append(doc)

        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{len(commentary_records)}")

    return documents


def create_match_documents(matches, innings_list, batting_stats, bowling_stats):
    """Create match summary documents."""
    documents = []

    # Index innings by match_id
    innings_by_match = defaultdict(list)
    for inn in innings_list:
        innings_by_match[inn['match_id']].append(inn)

    # Index stats by match_id
    batting_by_match = defaultdict(list)
    for stat in batting_stats:
        batting_by_match[stat['match_id']].append(stat)

    bowling_by_match = defaultdict(list)
    for stat in bowling_stats:
        bowling_by_match[stat['match_id']].append(stat)

    for match in matches:
        mid = match['match_id']
        inns = innings_by_match.get(mid, [])
        bat_stats = batting_by_match.get(mid, [])
        bowl_stats = bowling_by_match.get(mid, [])

        # Build match summary content
        content_parts = [
            f"Match {mid}: {match['team_a']} vs {match['team_b']}",
            f"Tournament: {match.get('tournament', '')}",
            f"Venue: {match.get('venue', '')}",
            f"Date: {match.get('date', '')}",
            f"Format: {match.get('format', '')}",
            f"Result: {match.get('result', '')}",
            f"Winner: {match.get('winner', '')}",
        ]

        # Add innings info
        for inn in inns:
            content_parts.append(f"Innings {inn.get('innings_number', '')}: {inn.get('batting_team', '')} {inn.get('runs', '')}/{inn.get('wickets', '')} in {inn.get('overs', '')} overs")

        # Add top batting performers
        top_bat = sorted(bat_stats, key=lambda x: int(x.get('runs', 0)), reverse=True)[:3]
        for bat in top_bat:
            content_parts.append(f"{bat.get('player_name', '')} scored {bat.get('runs', '')} off {bat.get('balls', '')} balls")

        # Add top bowling performers
        top_bowl = sorted(bowl_stats, key=lambda x: int(x.get('wickets', 0)), reverse=True)[:3]
        for bowl in top_bowl:
            content_parts.append(f"{bowl.get('player_name', '')} took {bowl.get('wickets', '')} wickets for {bowl.get('runs', '')} runs")

        content = ". ".join(filter(None, content_parts))

        doc = {
            "document_id": f"{mid}_MATCH_SUMMARY",
            "content": content,
            "language": "en",
            "match_id": mid,
            "over": 0,
            "ball": 0,
            "event_type": "MATCH_SUMMARY",
            "players": [],
            "teams": [match.get('team_a', ''), match.get('team_b', '')],
            "timestamp": "",
            "source": "match_summary",
            "match_format": match.get('format', ''),
            "venue": match.get('venue', ''),
            "tournament": match.get('tournament', ''),
            "result": match.get('result', ''),
            "winner": match.get('winner', '')
        }
        documents.append(doc)

    return documents


def create_player_documents(players, batting_stats, bowling_stats, matches):
    """Create player statistics documents per match."""
    documents = []

    # Index match info
    match_info = {m['match_id']: m for m in matches}

    # Index batting stats by match_id and player
    batting_by_match_player = defaultdict(list)
    for stat in batting_stats:
        key = (stat['match_id'], stat.get('player_id', ''), stat.get('player_name', ''))
        batting_by_match_player[key].append(stat)

    # Index bowling stats
    bowling_by_match_player = defaultdict(list)
    for stat in bowling_stats:
        key = (stat['match_id'], stat.get('player_id', ''), stat.get('player_name', ''))
        bowling_by_match_player[key].append(stat)

    # Create documents for each player-match combination
    all_keys = set(batting_by_match_player.keys()) | set(bowling_by_match_player.keys())

    for (mid, pid, pname) in all_keys:
        if not pid or not pname:
            continue

        bat_stats = batting_by_match_player.get((mid, pid, pname), [])
        bowl_stats = bowling_by_match_player.get((mid, pid, pname), [])

        match = match_info.get(mid, {})
        team_a = match.get('team_a', '')
        team_b = match.get('team_b', '')

        content_parts = [
            f"Player {pname} in match {mid}: {team_a} vs {team_b}"
        ]

        # Batting stats
        for bat in bat_stats:
            runs = bat.get('runs', 0)
            balls = bat.get('balls', 0)
            fours = bat.get('fours', 0)
            sixes = bat.get('sixes', 0)
            sr = bat.get('strike_rate', '')
            content_parts.append(f"Batting: {runs} runs off {balls} balls, {fours} fours, {sixes} sixes, SR {sr}")

        # Bowling stats
        for bowl in bowl_stats:
            overs = bowl.get('overs', 0)
            runs = bowl.get('runs_conceded', bowl.get('runs', 0))
            wickets = bowl.get('wickets', 0)
            econ = bowl.get('economy', '')
            content_parts.append(f"Bowling: {overs} overs, {runs} runs, {wickets} wickets, Econ {econ}")

        content = ". ".join(filter(None, content_parts))

        doc = {
            "document_id": f"{mid}_PLAYER_{pid}",
            "content": content,
            "language": "en",
            "match_id": mid,
            "over": 0,
            "ball": 0,
            "event_type": "PLAYER_STATS",
            "players": [pname],
            "teams": [team_a, team_b] if team_a else [],
            "timestamp": "",
            "source": "player_stats",
            "player_id": pid,
            "player_name": pname,
            "batting_runs": sum(int(b.get('runs', 0)) for b in bat_stats),
            "bowling_wickets": sum(int(b.get('wickets', 0)) for b in bowl_stats)
        }
        documents.append(doc)

    return documents


def create_event_documents(commentary_records):
    """Create structured event documents from commentary with events."""
    documents = []
    event_types = {'FOUR', 'SIX', 'WICKET', 'FIFTY', 'CENTURY'}

    for record in commentary_records:
        event_label = record.get('event_label', '')
        if event_label not in event_types:
            continue

        text = record.get('original_text', '')
        players = record.get('player_mentions', [])

        content = f"Event: {event_label}. {text}"

        doc = {
            "document_id": f"{record['commentary_id']}_EVENT",
            "content": content,
            "language": record.get('language', 'unknown'),
            "match_id": record.get('match_id', ''),
            "over": record.get('over', 0),
            "ball": record.get('ball', 0),
            "event_type": event_label,
            "players": players,
            "teams": record.get('team_mentions', []),
            "timestamp": record.get('timestamp', ''),
            "source": "event",
            "dismissal_type": record.get('dismissal_type')
        }
        documents.append(doc)

    return documents


def create_sample_queries(documents, output_path):
    """Create sample queries for evaluation."""
    queries = [
        {"query_id": "Q001", "query": "Virat Kohli boundaries", "language": "en", "match_id": "M001"},
        {"query_id": "Q002", "query": "कितने विकेट गिरे", "language": "hi", "match_id": "M001"},
        {"query_id": "Q003", "query": "सर्वाधिक धावा कोणी केल्या", "language": "mr", "match_id": "M001"},
        {"query_id": "Q004", "query": "Bumrah wickets", "language": "en", "match_id": "M002"},
        {"query_id": "Q005", "query": "पावरप्ले में रन", "language": "hi", "match_id": "M002"},
        {"query_id": "Q006", "query": "कोहली ने शतक बनाया", "language": "hi", "match_id": "M003"},
        {"query_id": "Q007", "query": "Rohit Sharma sixes", "language": "en", "match_id": "M003"},
        {"query_id": "Q008", "query": "मैच का टर्निंग पॉइंट", "language": "hi", "match_id": "M004"},
        {"query_id": "Q009", "query": "match turning point", "language": "en", "match_id": "M004"},
        {"query_id": "Q010", "query": "सामन्यातील टर्निंग पॉइंट", "language": "mr", "match_id": "M004"},
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for q in queries:
            f.write(json.dumps(q, ensure_ascii=False) + '\n')

    print(f"Created {len(queries)} sample queries at {output_path}")
    return queries


def create_heuristic_qrels(documents, queries, output_path):
    """Create heuristic relevance judgments: same match_id = relevant."""
    qrels = []

    # Index documents by match_id
    docs_by_match = defaultdict(list)
    for doc in documents:
        docs_by_match[doc['match_id']].append(doc['document_id'])

    for query in queries:
        mid = query['match_id']
        relevant = docs_by_match.get(mid, [])
        if relevant:
            qrels.append({
                "query_id": query['query_id'],
                "relevant_documents": relevant[:20]  # Limit to top 20 per query
            })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for qrel in qrels:
            f.write(json.dumps(qrel, ensure_ascii=False) + '\n')

    print(f"Created {len(qrels)} qrels at {output_path}")


def main():
    base_path = Path(__file__).parent.parent

    # Load data
    print("Loading data...")
    commentary = load_jsonl(base_path / "data" / "raw" / "commentary" / "commentary.jsonl")
    matches = load_csv(base_path / "data" / "raw" / "matches" / "matches.csv")
    batting = load_csv(base_path / "data" / "raw" / "matches" / "batting_stats.csv")
    bowling = load_csv(base_path / "data" / "raw" / "matches" / "bowling_stats.csv")
    innings = load_csv(base_path / "data" / "raw" / "matches" / "innings.csv")
    players = load_csv(base_path / "data" / "raw" / "matches" / "players.csv")

    print(f"  Commentary: {len(commentary)}")
    print(f"  Matches: {len(matches)}")
    print(f"  Batting stats: {len(batting)}")
    print(f"  Bowling stats: {len(bowling)}")
    print(f"  Innings: {len(innings)}")
    print(f"  Players: {len(players)}")

    # Initialize pipeline
    pipeline = NLPPreprocessingPipeline()

    # Create documents
    all_docs = []

    print("\nCreating commentary documents...")
    comm_docs = create_commentary_documents(commentary, pipeline)
    all_docs.extend(comm_docs)
    print(f"  Commentary docs: {len(comm_docs)}")

    print("Creating match summary documents...")
    match_docs = create_match_documents(matches, innings, batting, bowling)
    all_docs.extend(match_docs)
    print(f"  Match docs: {len(match_docs)}")

    print("Creating player statistics documents...")
    player_docs = create_player_documents(players, batting, bowling, matches)
    all_docs.extend(player_docs)
    print(f"  Player docs: {len(player_docs)}")

    print("Creating event documents...")
    event_docs = create_event_documents(commentary)
    all_docs.extend(event_docs)
    print(f"  Event docs: {len(event_docs)}")

    # Save documents
    output_dir = base_path / "data" / "processed" / "ir"
    output_dir.mkdir(parents=True, exist_ok=True)

    docs_path = output_dir / "documents.jsonl"
    with open(docs_path, 'w', encoding='utf-8') as f:
        for doc in all_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')

    print(f"\nTotal documents: {len(all_docs)}")
    print(f"Saved to {docs_path}")

    # Stats
    by_type = defaultdict(int)
    by_lang = defaultdict(int)
    for doc in all_docs:
        by_type[doc['source']] += 1
        by_lang[doc['language']] += 1

    print(f"By type: {dict(by_type)}")
    print(f"By language: {dict(by_lang)}")

    # Create queries and qrels
    queries_path = output_dir / "queries.json"
    queries = create_sample_queries(all_docs, queries_path)

    qrels_path = output_dir / "qrels.json"
    create_heuristic_qrels(all_docs, queries, qrels_path)

    print("\nDone!")


if __name__ == "__main__":
    main()