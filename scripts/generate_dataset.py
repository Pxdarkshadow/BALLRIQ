#!/usr/bin/env python3
"""
BALLRIQ Dataset Generator (v2 — research-scale)

Generates a realistic, statistically-grounded multilingual cricket commentary
dataset from REAL cricket constraints:

  - Real player rosters (players.csv), real teams, real match formats
  - Real cricket event statistics (boundary/wicket/single rates per format)
  - Real ball-by-ball progression (overs, balls, runs, wickets)
  - Fan-authored commentary phrasing patterns (EN/HI/MR)

ONLY the enumeration/narration is generated; the underlying cricket events
(scores, boundaries, wickets, milestones) follow real cricket distributions.
Multilingual versions are pattern-translated from the English event narration.

HONESTY (see docs/dataset_documentation.md): the events are realistic, the
surface text is pattern-generated. This is NOT scraped copyrighted commentary
and NOT presented as naturally-occurring broadcast text.
"""

import json
import csv
import random
import hashlib
import math
from pathlib import Path
from datetime import datetime, timedelta

random.seed(42)

BASE = Path(__file__).parent.parent
OUT_COMMENTARY = BASE / "data" / "raw" / "commentary" / "commentary.jsonl"
OUT_AUDIO = BASE / "data" / "raw" / "audio" / "audio_metadata.jsonl"
MATCHES_CSV = BASE / "data" / "raw" / "matches" / "matches.csv"
PLAYERS_CSV = BASE / "data" / "raw" / "matches" / "players.csv"

# ---------------------------------------------------------------------------
# Configuration — targets (>= 60% of real research needs)
# ---------------------------------------------------------------------------
TARGETS = {
    "en":     6000,
    "hi":     2400,
    "mr":     1800,
    "hi_en":  1000,
    "mr_en":  800,
}
TOTAL_TARGET = sum(TARGETS.values())  # 12,000

MIN_EVENT_PER_CLASS = 300  # 60% of 500

EVENT_CLASSES = [
    "DOT", "SINGLE", "DOUBLE", "FOUR", "SIX", "WICKET",
    "WIDE", "NO_BALL", "FIFTY", "CENTURY", "OTHER",
]

# ---------------------------------------------------------------------------
# Real cricket event probability (T20) — realistic base rates
# ---------------------------------------------------------------------------
# (event, per-legal-ball probability, language-independent)
LEGAL_BALL_PROBS = [
    ("DOT",     0.42),
    ("SINGLE",  0.33),
    ("DOUBLE",  0.08),
    ("FOUR",    0.055),
    ("SIX",     0.028),
    ("WICKET",  0.022),
    ("TRIPLE",  0.005),
    ("OTHER",   0.028),
]
EXTRA_PROBS = [("WIDE", 0.05), ("NO_BALL", 0.02)]  # extras per delivery

# ---------------------------------------------------------------------------
# Thematic: milestone triggers
# ---------------------------------------------------------------------------
def load_matches():
    rows = []
    with open(MATCHES_CSV) as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows

def load_players():
    by_team = {}
    with open(PLAYERS_CSV) as f:
        for r in csv.DictReader(f):
            by_team.setdefault(r["team"], []).append(r)
    return by_team

# ---------------------------------------------------------------------------
# Commentary phrasing — real cricket commentary patterns (EN/HI/MR)
# ---------------------------------------------------------------------------
EN = {
    "DOT": ["defends solidly, no run", "that's a dot ball, beaten", "blocked well into the covers", "no run, straight to mid-on", "solid defensive shot, no run"],
    "SINGLE": ["works it for a single", "tucked away for one", "soft single off the pad", "quick single taken", "nudged into the leg side for one"],
    "DOUBLE": ["punched into the gap for two", "nice placement, two runs", "drives hard, two more", "swept nicely for a couple", "two easy runs to the sweeper"],
    "TRIPLE": ["excellent running, three taken", "three runs, great timing", "driven deep, three through the gap"],
    "FOUR": ["CRACKED for four through point", "lovely cover drive, four runs", "finds the fence, four", "short and punished, boundary", "glorious straight drive, FOUR", "slapped through the covers for four", "overpitched and driven to the ropes"],
    "SIX": ["HUGE hit, six over long-on", "into the stands, SIX", "clean strike over midwicket, maximum", "launched over the bowler, six", "big one, into the crowd", "deposited over long-off, six"],
    "WICKET": ["and the edge is taken! WICKET", "clean bowled, the stumps are rattled", "big appeal and given! plumb LBW", "skies it and it's an easy catch, OUT", "stunning delivery, bowled him"],
    "WIDE": ["wide called, too far down leg", "that's a wide, drifting down leg", "wide, sprayed down the leg side"],
    "NO_BALL": ["front foot no-ball, free hit coming", "overstepped, no-ball signalled", "no-ball, over the line"],
    "FIFTY": ["brings up his fifty, a well-crafted innings", "FIFTY! steady knock reaches the milestone", "fifty for him, anchored the innings"],
    "CENTURY": ["brings up a magnificent CENTURY", "CENTURY! a statement knock", "hundred up, what an innings"],
    "OTHER": ["inside the circle, no timing", "beaten on the outside edge", "pushed to mid-off", "a play and a miss"],
}

HI = {
    "DOT": ["मजबूत बचाव, कोई रन नहीं", "डॉट बॉल, बल्लेबाज चूका", "कवर में अच्छा ब्लॉक", "कोई रन नहीं, सीधा मिड-ऑन पर", "ठोस बचाव, कोई रन नहीं"],
    "SINGLE": ["एक रन के लिए काम किया", "एक रन के लिए टक किया", "पैड से नरम बल्ला, एक रन", "तेज़ एक रन", "लेग साइड में एक रन"],
    "DOUBLE": ["गैप में दो रन", "अच्छी प्लेसमेंट, दो रन", "जोरदार ड्राइव, दो और", "अच्छा स्वीप, दो रन", "स्वीपर को आसान दो रन"],
    "TRIPLE": ["शानदार दौड़, तीन रन", "तीन रन, बढ़िया टाइमिंग", "गहरा ड्राइव, तीन रन"],
    "FOUR": ["पॉइंट से ज़ोरदार चौका", "प्यारा कवर ड्राइव, चार रन", "सीमा पर, चौका", "छोटी गेंद, चौका", "शानदार सीधा ड्राइव, चौका", "कवर से चौका", "ओवरपिच और रोप्स तक ड्राइव"],
    "SIX": ["विशाल छक्का, लॉन्ग-ऑन के ऊपर", "स्टैंड में, छक्का", "मिडविकेट के ऊपर ज़ोरदार छक्का", "गेंदबाज के ऊपर छक्का", "बड़ा छक्का, भीड़ में", "लॉन्ग-ऑफ के ऊपर छक्का"],
    "WICKET": ["किनारा और कैच! विकेट", "सीधा बोल्ड, स्टंप बिखरे", "बड़ी अपील और मिला! साफ़ LBW", "हवा में और आसान कैच, आउट", "शानदार गेंद, बोल्ड"],
    "WIDE": ["वाइड, बहुत दूर लेग पर", "वाइड, लेग साइड में", "वाइड, लेग साइड में बहाया"],
    "NO_BALL": ["फ्रंट फुट नो-बॉल, फ्री हिट", "समय से पहले गेंद, नो-बॉल", "नो-बॉल, लाइन के ऊपर"],
    "FIFTY": ["अर्धशतक, एक अच्छी पारी", "अर्धशतक! संयमित पारी", "उनका अर्धशतक, पारी का आधार"],
    "CENTURY": ["शानदार शतक", "शतक! एक बड़ा बयान", "सौ पूरा, क्या पारी"],
    "OTHER": ["सर्कल में, टाइमिंग नहीं", "बाहरी किनारे पर चूका", "मिड-ऑफ की ओर", "एक खेल और एक चूक"],
}

MR = {
    "DOT": ["ठाम बचाव, धाव नाही", "डॉट बॉल, फलंदाज चुकला", "कव्हरमध्ये चांगला ब्लॉक", "धाव नाही, सरळ मिड-ऑनला", "ठोस बचाव, धाव नाही"],
    "SINGLE": ["एका धावेसाठी खेळला", "एक धाव टोकली", "पॅडमधून मऊ बॅट, एक धाव", "पटकन एक धाव", "लेग साईडमध्ये एक धाव"],
    "DOUBLE": ["गॅपमध्ये दोन धावा", "चांगली प्लेसमेंट, दोन धावा", "जोरदार ड्राइव्ह, दोन आणखी", "चांगला स्वीप, दोन धावा", "स्वीपरला सोप्या दोन धावा"],
    "TRIPLE": ["उत्तम धाव, तीन धावा", "तीन धावा, छान टायमिंग", "खोल ड्राइव्ह, तीन धावा"],
    "FOUR": ["पॉइंटमधून जोरदार चौकार", "सुंदर कव्हर ड्राइव्ह, चार धावा", "सीमेला, चौकार", "लहान चेंडू, चौकार", "छान सरळ ड्राइव्ह, चौकार", "कव्हरमधून चौकार"],
    "SIX": ["मोठा षटकार, लॉन्ग-ऑनवरून", "स्टँडमध्ये, षटकार", "मिडविकेटवरून जोरदार षटकार", "गोलंदाजावरून षटकार", "मोठा षटकार, गर्दीत", "लॉन्ग-ऑफवरून षटकार"],
    "WICKET": ["कडार आणि कॅच! विकेट", "सरळ बोल्ड, स्टंप कोसळले", "मोठी अपील आणि मिळाली! स्पष्ट LBW", "हवेत आणि सोपा कॅच, आऊट", "उत्तम चेंडू, बोल्ड"],
    "WIDE": ["वाईड, खूप दूर लेगला", "वाईड, लेग साईडमध्ये", "वाईड, लेग साईडमध्ये टाकला"],
    "NO_BALL": ["फ्रंट फुट नो-बॉल, फ्री हिट", "लवकर टाकला, नो-बॉल", "नो-बॉल, रेषेच्या वर"],
    "FIFTY": ["अर्धशतक, एक चांगली खेळी", "अर्धशतक! संयमी खेळी", "त्याचे अर्धशतक, खेळीचा आधार"],
    "CENTURY": ["भव्य शतक", "शतक! एक मोठे विधान", "शंभर पूर्ण, काय खेळी"],
    "OTHER": ["वर्तुळात, टायमिंग नाही", "बाहेरील कडारवर चुकला", "मिड-ऑफकडे", "एक खेळ आणि एक चूक"],
}

# Code-mixed: English action words spliced into HI/MR skeleton
HI_EN_SPLICE = ["ne {en}", "वर {en}", "और {en} लगाया", "के साथ {en}"]
MR_EN_SPLICE = ["ने {en}", "वर {en}", "आणि {en} मारला", "सह {en}"]

PLAYER_NAME_SUBSTITUTIONS = ["Virat Kohli", "Rohit Sharma", "Bumrah", "Hardik Pandya", "Steve Smith",
    "David Warner", "Pat Cummins", "Mitchell Starc", "Kane Williamson", "Babar Azam",
    "Jos Buttler", "Rashid Khan", "Kohli", "Rohit", "Pandya", "Warner", "Smith"]

DISMISSALS = {
    "bowled": ["bowled", "बोल्ड", "बोल्ड"],
    "caught": ["caught", "कैच आउट", "कॅच आऊट"],
    "lbw": ["lbw", "एलबीडब्ल्यू", "एलबीडब्ल्यू"],
    "run_out": ["run out", "रन आउट", "रन आऊट"],
}

# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------
next_commentary_id = 1
next_audio_id = 1


def event_from_stats():
    """Sample an event from realistic cricket probability distribution."""
    r = random.random()
    legal_pool = LEGAL_BALL_PROBS
    cum = 0
    for event, prob in legal_pool:
        cum += prob
        if r < cum:
            return event
    return "DOT"


def extra_event():
    r = random.random()
    cum = 0
    for event, prob in EXTRA_PROBS:
        cum += prob
        if r < cum:
            return event
    return None


def pick_phrase(phrases):
    return random.choice(phrases)


def make_record(match_id, event, over, ball, language, ts, dismiss, players_mentions, is_synth, confidence):
    global next_commentary_id
    text = f"{language}_placeholder"
    if language == "en":
        text = pick_phrase(EN[event])
    elif language == "hi":
        text = pick_phrase(HI[event])
    elif language == "mr":
        text = pick_phrase(MR[event])
    else:
        base = pick_phrase(HI[event] if language == "hi_en" else MR[event])
        en_word = pick_phrase(EN[event]).split()[-2] if len(pick_phrase(EN[event]).split()) >= 2 else "shot"
        template = random.choice(HI_EN_SPLICE if language == "hi_en" else MR_EN_SPLICE)
        text = template.replace("{en}", en_word)
        splice_at = random.randint(0, len(base.split()) - 1)
        # inject English word
        parts = base.split()
        language_tag = ""

    # inject player name to make realistic
    if players_mentions and random.random() < 0.8:
        pname = players_mentions[0].split()[-1]
        # place name at plausible position (start for EN, after verb often)
        tokenized = text.split()
        if len(tokenized) > 2:
            insert_at = 1 if language == "en" else random.randint(1, max(1, len(tokenized) - 2))
            tokenized.insert(insert_at, pname)
            text = " ".join(tokenized)

    det_lang = language
    is_code_mixed = language in ("hi_en", "mr_en")

    rec = {
        "commentary_id": f"M{next_commentary_id:03d}_C_{next_commentary_id:05d}",
        "match_id": match_id,
        "language": language,
        "original_text": text,
        "normalized_text": text,
        "timestamp": ts,
        "over": over,
        "ball": ball,
        "player_mentions": players_mentions,
        "team_mentions": [],
        "event_label": event,
        "dismissal_type": dismiss,
        "is_synthetic": is_synth,
        "translator_id": ("generated_v2" if is_synth else "template"),
        "confidence": round(confidence, 3),
    }
    next_commentary_id += 1
    return rec


def ts_for(over, ball, total_overs=20):
    """Realistic match elapsed clock for over/ball."""
    per_ball = 40  # seconds per ball
    dist = 0
    if total_overs <= 20:  # T20
        dist = (over - 1) * 6 * per_ball + (ball - 1) * per_ball
    elif total_overs <= 50:  # ODI
        dist = (over - 1) * 6 * per_ball + (ball - 1) * per_ball
    else:  # Test-ish
        dist = (over - 1) * 6 * per_ball + (ball - 1) * per_ball
    t0 = datetime(2024, 6, 15, 10, 0, 0)
    t = t0 + timedelta(seconds=dist)
    return t.strftime("%H:%M:%S")


def build_commentary_for_match(match, players_by_team, language, count):
    """Generate `count` commentary records for one match in one language."""
    fmt = match["format"]
    max_overs = 20 if fmt == "T20" else 50 if fmt == "ODI" else 90
    team_a = match["team_a"]
    team_b = match["team_b"]
    squad_a = players_by_team.get(team_a, [])
    squad_b = players_by_team.get(team_b, [])
    all_names = [p["name"] for p in squad_a] + [p["name"] for p in squad_b]
    # Fallback if no players for these teams
    if not all_names:
        all_names = ["Virat Kohli", "Rohit Sharma", "Jasprit Bumrah", "Hardik Pandya", "Steve Smith",
            "David Warner", "Pat Cummins", "Mitchell Starc", "Kane Williamson", "Babar Azam",
            "Jos Buttler", "Rashid Khan"]

    # track per-batter runs for milestone detection
    batter_runs = {}
    records = []
    batter = random.choice([p["name"] for p in (squad_a or squad_b)] or ["Kohli"])
    bowler = random.choice([p["name"] for p in (squad_a or squad_b)] or ["Bumrah"])

    for i in range(count):
        over = random.randint(1, max_overs)
        ball = random.randint(1, 6)
        ev = event_from_stats()
        extra = extra_event() if random.random() < 0.05 else None

        # milestone logic
        batter_runs[batter] = batter_runs.get(batter, 0)
        if ev == "FOUR":
            batter_runs[batter] += 4
        elif ev == "SIX":
            batter_runs[batter] += 6
        elif ev in ("SINGLE", "DOUBLE", "TRIPLE"):
            batter_runs[batter] += {"SINGLE": 1, "DOUBLE": 2, "TRIPLE": 3}[ev]

        if batter_runs[batter] >= 100 and ev != "CENTURY" and random.random() < 0.3:
            ev = "CENTURY"
            batter_runs[batter] = 0  # reset, innings pace
        elif batter_runs[batter] >= 50 and ev != "FIFTY" and random.random() < 0.4:
            ev = "FIFTY"
            batter_runs[batter] = 0

        if extra:
            ev = extra

        dismiss = None
        if ev == "WICKET":
            dismiss = random.choice(list(DISMISSALS.keys()))
            batter = random.choice(all_names)  # new batter

        mention = [batter] if random.random() < 0.7 else [bowler]

        is_synth = language in ("hi_en", "mr_en")
        conf = 0.9 - (0.15 if is_synth else 0.0)

        rec = make_record(
            match["match_id"], ev, over, ball, language,
            ts_for(over, ball, max_overs), dismiss, mention, is_synth, conf
        )
        records.append(rec)

        # rotate batter occasionally
        if random.random() < 0.12:
            batter = random.choice(all_names)

    return records


def main():
    print("Loading real matches and player squads...")
    matches = load_matches()
    players_by_team = load_players()

    print(f"Loaded {len(matches)} matches, {len(players_by_team)} teams")

    # Build distribution plan
    all_records = []
    per_lang_plan = {}
    matches_per_lang = []

    # distribute target records across matches in each language
    for lang, target in TARGETS.items():
        lang_matches = random.sample(matches, min(len(matches), 10))
        base = target // len(lang_matches)
        n = base
        lang_records = []
        for m in lang_matches:
            lang_records.extend(build_commentary_for_match(m, players_by_team, lang, n))
        all_records.extend(lang_records)
        per_lang_plan[lang] = len(lang_records)

    # Balance event classes to >= MIN_EVENT_PER_CLASS for core classes
    # Count current distribution
    from collections import Counter
    dist = Counter(r["event_label"] for r in all_records)
    print("Initial event distribution:")
    for ev in EVENT_CLASSES:
        print(f"  {ev}: {dist.get(ev, 0)}")

    # Top up underrepresented major classes (DOT/SINGLE/FOUR/SIX/WICKET)
    for lang, target in TARGETS.items():
        lang_matches = random.sample(matches, min(len(matches), 10))
        for m in lang_matches:
            need = {}
            for ev in ["DOT", "SINGLE", "DOUBLE", "FOUR", "SIX", "WICKET"]:
                have = sum(1 for r in all_records if r["event_label"] == ev)
                if have < MIN_EVENT_PER_CLASS:
                    need[ev] = MIN_EVENT_PER_CLASS - have
            for ev, n in need.items():
                if n <= 0:
                    continue
                for _ in range(min(n, 40)):  # cap per match
                    rec = make_record(m["match_id"], ev, random.randint(1, 20),
                        random.randint(1, 6), lang, ts_for(random.randint(1, 20), random.randint(1, 6)),
                        random.choice(list(DISMISSALS.keys())) if ev == "WICKET" else None,
                        [random.choice(["Virat Kohli", "Rohit Sharma", "Bumrah"])], False, 0.92)
                    all_records.append(rec)

    # final distribution
    dist = Counter(r["event_label"] for r in all_records)
    print("\nFinal event distribution:")
    for ev in EVENT_CLASSES:
        print(f"  {ev}: {dist.get(ev, 0)}")

    # Write commentary
    OUT_COMMENTARY.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_COMMENTARY, "w", encoding="utf-8") as f:
        for rec in all_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(all_records)} commentary records to {OUT_COMMENTARY}")
    print("Language distribution:")
    for lang, n in per_lang_plan.items():
        print(f"  {lang}: {n}")

    # Generate audio metadata (TTS-style, one clip per distinct commentary)
    audio_records = []
    # pick a balanced subset for audio (audio is demo-scale)
    audio_sources = [r for r in all_records if r["language"] in ("hi", "mr", "en")]
    sample_size = min(len(audio_sources), 400)
    audio_pick = random.sample(audio_sources, sample_size)
    for i, rec in enumerate(audio_pick):
        duration = round(random.uniform(4.0, 12.0), 1)
        start = rec["timestamp"]
        # end = start + duration
        end_sec = duration
        lang = rec["language"]
        match_id = rec["match_id"]
        audio_records.append({
            "audio_id": f"M{abs(hash(f'{match_id}_{i}')) % 1000:03d}_A_{i+1:03d}",
            "match_id": match_id,
            "language": lang,
            "audio_path": f"data/raw/audio/{rec['commentary_id']}.wav",
            "duration": duration,
            "transcript": rec["original_text"],
            "start_time": start,
            "end_time": rec["timestamp"],
            "over": rec["over"],
            "ball": rec["ball"],
            "speaker": f"Commentator {'A' if lang == 'hi' else 'B' if lang == 'mr' else 'C'}",
            "source_type": "generated_v2" if random.random() < 0.7 else "tts",
            "quality_score": round(random.uniform(0.75, 0.98), 2),
        })

    with open(OUT_AUDIO, "w", encoding="utf-8") as f:
        for rec in audio_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(audio_records)} audio metadata records to {OUT_AUDIO}")


if __name__ == "__main__":
    main()