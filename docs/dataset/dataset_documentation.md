# BALLRIQ Cricket Commentary Dataset Documentation

## Overview

This document describes the three datasets used in the BALLRIQ project, their sources, characteristics, and usage within the NLP and Information Retrieval pipelines.

---

## DATASET A — Structured Cricket Match Data

### Dataset Name
**BALLRIQ Match Metadata Dataset**

### Source
- **Primary**: Cricsheet (https://cricsheet.org/) — ball-by-ball cricket data under CC0 license
- **Supplementary**: ESPNcricinfo match summaries (manually collected for tournament/format metadata)
- **Synthetic**: Match IDs, formatted metadata for demonstration matches

### Data Type
Structured tabular data (CSV/JSON)

### Number of Records
- **Matches**: 50 (25 T20, 15 ODI, 10 Test)
- **Players**: ~600 unique players across matches
- **Innings**: 100 (2 per match)
- **Batting records**: ~1,200
- **Bowling records**: ~1,000

### Languages
English (metadata only — player names, venue, tournament names)

### Features / Columns

**matches.csv**
| Column | Type | Description |
|--------|------|-------------|
| match_id | string | Unique identifier (format: M{###}) |
| date | date | Match date (YYYY-MM-DD) |
| format | enum | T20, ODI, Test |
| tournament | string | Series/tournament name |
| venue | string | Stadium, City, Country |
| team_a | string | Team A name |
| team_b | string | Team B name |
| winner | string | Winning team |
| result | string | Result description (e.g., "India won by 5 wickets") |
| toss_winner | string | Team that won toss |
| toss_decision | enum | bat/field |

**players.csv**
| Column | Type | Description |
|--------|------|-------------|
| player_id | string | Unique identifier |
| name | string | Full name |
| team | string | National/IPL team |
| role | enum | batsman, bowler, allrounder, wicketkeeper |
| batting_style | string | Right-hand/Left-hand |
| bowling_style | string | Pace/Spin details |

**innings.csv**
| Column | Type | Description |
|--------|------|-------------|
| innings_id | string | Unique identifier |
| match_id | string | Foreign key to matches |
| innings_number | int | 1 or 2 |
| batting_team | string | Team batting |
| bowling_team | string | Team bowling |
| total_runs | int | Runs scored |
| wickets | int | Wickets lost |
| overs | float | Overs faced |
| target | int | Target (2nd innings) |

**batting_stats.csv**
| Column | Type | Description |
|--------|------|-------------|
| record_id | string | Unique identifier |
| match_id | string | Foreign key |
| innings_id | string | Foreign key |
| player_id | string | Foreign key |
| runs | int | Runs scored |
| balls | int | Balls faced |
| fours | int | Number of 4s |
| sixes | int | Number of 6s |
| strike_rate | float | Runs per 100 balls |
| dismissal | string | How out (or "not out") |

**bowling_stats.csv**
| Column | Type | Description |
|--------|------|-------------|
| record_id | string | Unique identifier |
| match_id | string | Foreign key |
| innings_id | string | Foreign key |
| player_id | string | Foreign key |
| overs | float | Overs bowled |
| runs_conceded | int | Runs given |
| wickets | int | Wickets taken |
| economy | float | Runs per over |
| wides | int | Wides bowled |
| no_balls | int | No balls bowled |

### Purpose in Project
- Match UI (header, score, teams, venue)
- Statistics tabs (team, batting, bowling)
- Player cards and profiles
- RAG context (ground truth for answers)
- IR metadata filtering (match_id, over, ball, player, event_type)

### Preprocessing Applied
- Schema validation
- Duplicate match_id removal
- Date normalization (ISO 8601)
- Player name standardization using player_aliases.json
- Team name standardization

### Train/Validation/Test Split
**Split by match_id** to prevent leakage:
- Train: 35 matches (70%)
- Validation: 7 matches (15%)
- Test: 8 matches (15%)

### Limitations
- Limited to public Cricsheet data (mostly international matches)
- No ball-by-ball commentary text in source (added in Dataset B)
- Player metadata incomplete for older matches

---

## DATASET B — Multilingual Cricket Commentary Dataset

### Dataset Name
**BALLRIQ Multilingual Commentary Corpus (CMCC)**

### Source
- **Base English commentary**: Cricsheet ball-by-ball text + ESPNcricinfo commentary logs
- **Hindi translations**: Professional translators (5 annotators) + synthetic augmentation
- **Marathi translations**: Professional translators (3 annotators) + synthetic augmentation
- **Code-mixed variants**: Generated via rule-based mixing (English nouns + Hindi/Marathi verbs)
- **Self-created annotations**: 2,000 manually labelled Hindi/Marathi commentary samples with event labels

### Data Type
Structured text with labels (CSV/JSONL)

### Number of Records
| Language | Records | Source |
|----------|---------|--------|
| English (base) | 10,000 | Cricsheet + ESPNcricinfo |
| Hindi (translated) | 8,000 | Human translation + augmentation |
| Marathi (translated) | 6,000 | Human translation + augmentation |
| Code-mixed HI-EN | 3,000 | Synthetic |
| Code-mixed MR-EN | 2,000 | Synthetic |
| **Total** | **29,000** | |

### Languages
- Hindi (hi) — Devanagari script
- Marathi (mr) — Devanagari script
- English (en) — Latin script
- Code-mixed HI-EN
- Code-mixed MR-EN

### Features / Columns

**commentary.jsonl** (one record per line)
| Field | Type | Description |
|-------|------|-------------|
| commentary_id | string | Unique ID (format: M{###}_C_{####}) |
| match_id | string | Foreign key to matches.csv |
| language | enum | hi, mr, en, hi_en, mr_en |
| original_text | string | Raw commentary text |
| normalized_text | string | Preprocessed text (after pipeline) |
| timestamp | string | Match time (HH:MM:SS) |
| over | int | Over number (0-19 for T20) |
| ball | int | Ball number (1-6) |
| player_mentions | list[string] | Player names mentioned |
| team_mentions | list[string] | Team names mentioned |
| event_label | enum | FOUR, SIX, WICKET, DOT, SINGLE, DOUBLE, TRIPLE, WIDE, NO_BALL, FIFTY, CENTURY, OTHER |
| dismissal_type | string | bowled, caught, lbw, run_out, stumped, hit_wicket, null |
| is_synthetic | boolean | True if translated/augmented |
| translator_id | string | Annotator ID (for human) or "synthetic" |
| confidence | float | Annotation confidence (0-1) |

### Example Records

**Hindi (human translated)**
```json
{
  "commentary_id": "M001_C_0018",
  "match_id": "M001",
  "language": "hi",
  "original_text": "कोहली ने शानदार कवर ड्राइव खेला और गेंद सीमा रेखा के बाहर चली गई",
  "normalized_text": "कोहली ने शानदार कवर ड्राइव खेला और गेंद सीमा रेखा के बाहर चली गई",
  "timestamp": "00:18:45",
  "over": 18,
  "ball": 2,
  "player_mentions": ["Virat Kohli"],
  "team_mentions": ["India"],
  "event_label": "FOUR",
  "dismissal_type": null,
  "is_synthetic": false,
  "translator_id": "annotator_03",
  "confidence": 0.95
}
```

**Marathi (human translated)**
```json
{
  "commentary_id": "M001_C_0019",
  "match_id": "M001",
  "language": "mr",
  "original_text": "कोहलीने अप्रतिम कव्हर ड्राइव्ह मारला आणि चेंडू सीमारेषेबाहेर गेला",
  "normalized_text": "कोहलीने अप्रतिम कव्हर ड्राइव्ह मारला आणि चेंडू सीमारेषेबाहेर गेला",
  "timestamp": "00:18:45",
  "over": 18,
  "ball": 2,
  "player_mentions": ["Virat Kohli"],
  "team_mentions": ["India"],
  "event_label": "FOUR",
  "dismissal_type": null,
  "is_synthetic": false,
  "translator_id": "annotator_mr_02",
  "confidence": 0.93
}
```

**Code-mixed HI-EN (synthetic)**
```json
{
  "commentary_id": "M001_C_0020",
  "match_id": "M001",
  "language": "hi_en",
  "original_text": "Kohli ne शानदार four maara",
  "normalized_text": "कोहली ने शानदार four मारा",
  "timestamp": "00:18:45",
  "over": 18,
  "ball": 2,
  "player_mentions": ["Virat Kohli"],
  "team_mentions": ["India"],
  "event_label": "FOUR",
  "dismissal_type": null,
  "is_synthetic": true,
  "translator_id": "synthetic_mixer_v1",
  "confidence": 0.85
}
```

### Purpose in Project
- Core NLP training data (event classification)
- Language identification training/evaluation
- Entity extraction (player, team, cricket terms)
- Event extraction (structured events from text)
- IR document collection (commentary as documents)
- Cross-lingual retrieval evaluation

### Preprocessing Applied
- Unicode normalization (NFC)
- Text cleaning (remove excess punctuation, fix encoding)
- Language detection labels added
- Number normalization (Hindi/Marathi words → digits)
- Cricket vocabulary normalization (synonyms → canonical)
- Player name normalization (aliases → canonical)
- Tokenization (indic-nlp for Hindi/Marathi, NLTK for English)

### Train/Validation/Test Split
**Split by match_id** (same splits as Dataset A):
- Train: 20,300 records (matches M001-M035)
- Validation: 4,350 records (matches M036-M042)
- Test: 4,350 records (matches M043-M050)

Stratified by event_label within each split.

### Limitations
- Translated data may not capture natural commentary style
- Code-mixed data is synthetic (rule-based)
- Limited Marathi data (harder to source)
- Class imbalance: DOT/OTHER dominate, WICKET/FIFTY/CENTURY rare
- No audio alignment (separate Dataset C)

---

## DATASET C — Cricket Audio Dataset

### Dataset Name
**BALLRIQ Cricket Audio Corpus (CCAC)**

### Source
- **Public domain cricket commentary**: All India Radio archives (public domain)
- **YouTube cricket highlights**: Creative Commons licensed content (manually verified)
- **Synthetic TTS**: Generated using Indic TTS models (Coqui TTS, VITS) for Hindi/Marathi
- **Self-recorded**: 50 samples recorded by project team for validation

### Data Type
Audio files (WAV, 16kHz, mono) + metadata (JSON)

### Number of Records
| Language | Duration | Clips | Source |
|----------|----------|-------|--------|
| Hindi | 45 min | 150 | Public domain + TTS |
| Marathi | 30 min | 100 | Public domain + TTS |
| English | 20 min | 50 | Public domain |
| **Total** | **95 min** | **300** | |

### Languages
- Hindi (hi)
- Marathi (mr)
- English (en)

### Features / Columns

**audio_metadata.jsonl**
| Field | Type | Description |
|-------|------|-------------|
| audio_id | string | Unique ID (format: M{###}_A_{###}) |
| match_id | string | Foreign key to matches.csv |
| language | enum | hi, mr, en |
| audio_path | string | Relative path to WAV file |
| duration | float | Duration in seconds |
| transcript | string | Ground truth transcript |
| start_time | string | Match timestamp start (HH:MM:SS) |
| end_time | string | Match timestamp end (HH:MM:SS) |
| over | int | Over number |
| ball | int | Ball number |
| speaker | string | Commentator name (if known) |
| source_type | enum | public_domain, creative_commons, tts, self_recorded |
| quality_score | float | Audio quality rating (0-1) |

### Example Record
```json
{
  "audio_id": "M001_A_001",
  "match_id": "M001",
  "language": "hi",
  "audio_path": "data/raw/audio/M001_A_001.wav",
  "duration": 8.5,
  "transcript": "कोहली ने शानदार कवर ड्राइव खेला और गेंद चार रन के लिए चली गई",
  "start_time": "00:18:42",
  "end_time": "00:18:50",
  "over": 18,
  "ball": 2,
  "speaker": "Commentator A",
  "source_type": "tts",
  "quality_score": 0.92
}
```

### Purpose in Project
- Speech-to-text pipeline demonstration
- Audio preprocessing (noise reduction, segmentation)
- Language identification from audio
- End-to-end NLP pipeline (audio → transcript → events)
- Timestamp alignment with ball-by-ball data

### Preprocessing Applied
- Resample to 16kHz mono
- Voice activity detection (VAD) for segmentation
- Loudness normalization (EBU R128)
- Noise reduction (spectral gating)
- Format conversion to WAV

### Train/Validation/Test Split
**Split by match_id** (aligned with Dataset A/B):
- Train: 210 clips (matches M001-M035)
- Validation: 45 clips (matches M036-M042)
- Test: 45 clips (matches M043-M050)

### Limitations
- Mostly TTS-generated (not natural broadcast audio)
- Limited duration (academic demo scale)
- No background crowd noise in TTS samples
- Marathi audio especially scarce
- No speaker diarization

---

## Cross-Dataset Relationships

```
matches.csv (50)
    │
    ├── innings.csv (100) ──────────────────┐
    ├── batting_stats.csv (1,200) ──────────┤
    ├── bowling_stats.csv (1,000) ──────────┤   → Dataset A
    └── players.csv (600) ──────────────────┘
    │
    ├── commentary.jsonl (29,000) ──────────→ Dataset B
    │       │
    │       └── event_label links to structured events
    │
    └── audio_metadata.jsonl (300) ─────────→ Dataset C
            │
            └── transcript aligns with commentary.original_text
```

---

## License & Usage

| Dataset | License | Notes |
|---------|---------|-------|
| Dataset A (Matches) | CC0 (Cricsheet) | Free for any use |
| Dataset B (Commentary) | Custom Academic | Human translations: project-owned; Synthetic: CC-BY-4.0 |
| Dataset C (Audio) | Mixed | Public domain: PD; CC: CC-BY; TTS: project-owned; Self-recorded: project-owned |

**Important**: Dataset B translations and Dataset C TTS audio are **clearly labelled as synthetic/augmented** via `is_synthetic` and `source_type` fields. They are NOT presented as naturally occurring broadcast commentary.

---

## Data Access

All raw data stored in:
```
data/raw/
├── matches/
│   ├── matches.csv
│   ├── players.csv
│   ├── innings.csv
│   ├── batting_stats.csv
│   └── bowling_stats.csv
├── commentary/
│   └── commentary.jsonl
├── audio/
│   ├── audio_metadata.jsonl
│   └── *.wav
└── player_data/
    └── (additional player metadata)
```

Processed data (after pipeline) in:
```
data/processed/
├── nlp/
│   ├── train.csv
│   ├── validation.csv
│   └── test.csv
└── ir/
    ├── documents.jsonl
    ├── queries.json
    └── qrels.json
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-29 | Initial documentation |

---

## Contact

For questions about this dataset, refer to the project repository or contact the BALLRIQ development team.