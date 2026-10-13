#!/usr/bin/env python3
"""
Full dataset generator — creates entire commentary.jsonl in one pass with balanced events.
"""

import json
import csv
import random
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

random.seed(42)

BASE = Path(__file__).parent.parent
OUT_COMMENTARY = BASE / "data" / "raw" / "commentary" / "commentary.jsonl"
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

MIN_EVENT_PER_CLASS = 300

EVENT_CLASSES = [
    "DOT", "SINGLE", "DOUBLE", "TRIPLE", "FOUR", "SIX", "WICKET",
    "WIDE", "NO_BALL", "FIFTY", "CENTURY", "OTHER",
]

# ---------------------------------------------------------------------------
# Real cricket event probability (T20) — realistic base rates
# ---------------------------------------------------------------------------
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
EXTRA_PROBS = [("WIDE", 0.05), ("NO_BALL", 0.02)]

# ---------------------------------------------------------------------------
# Commentary phrasing — realistic patterns
# ---------------------------------------------------------------------------
EN = {
    "DOT": ["defends solidly, no run", "that's a dot ball, beaten", "blocked well into the covers", "no run, straight to mid-on", "solid defensive shot, no run"],
    "SINGLE": ["works it for a single", "tucked away for one", "soft single off the pad", "quick single taken", "nudged into the leg side for one"],
    "DOUBLE": ["punched into the gap for two", "nice placement, two runs", "drives hard, two more", "swept nicely for a couple", "two easy runs to the sweeper"],
    "TRIPLE": ["excellent running, three taken", "three runs, great timing", "driven deep, three through the gap", "superb placement, three to deep midwicket", "three runs stolen, great awareness", "races three, brilliant running"],
    "FOUR": ["CRACKED for four through point", "lovely cover drive, four runs", "finds the fence, four", "short and punished, boundary", "glorious straight drive, FOUR", "slapped through the covers for four", "overpitched and driven to the ropes"],
    "SIX": ["HUGE hit, six over long-on", "into the stands, SIX", "clean strike over midwicket, maximum", "launched over the bowler, six", "big one, into the crowd", "deposited over long-off, six"],
    "WICKET": ["and the edge is taken! WICKET", "clean bowled, the stumps are rattled", "big appeal and given! plumb LBW", "skies it and it's an easy catch, OUT", "stunning delivery, bowled him"],
    "WIDE": ["wide called, too far down leg", "that's a wide, drifting down leg", "wide, sprayed down the leg side", "wide ball, too far outside off", "wide signalled, well outside off stump", "wide, bowler overcompensated"],
    "NO_BALL": ["front foot no-ball, free hit coming", "overstepped, no-ball signalled", "no-ball, over the line", "no-ball, front foot well over", "no-ball called, free hit now", "overstepped the crease, no-ball"],
    "FIFTY": ["brings up his fifty, a well-crafted innings", "FIFTY! steady knock reaches the milestone", "fifty for him, anchored the innings", "reaches fifty with a gentle push", "half-century up, composed batting", "fifty comes up, great composure shown", "FIFTY reached with a single to midwicket", "milestone fifty, patient innings built"],
    "CENTURY": ["brings up a magnificent CENTURY", "CENTURY! a statement knock", "hundred up, what an innings", "century reached with a glorious drive", "CENTURY! maiden ton for the batsman", "HUNDRED up, dominated the attack", "century completed with a boundary", "magnificent century, stands tall"],
    "OTHER": ["inside the circle, no timing", "beaten on the outside edge", "pushed to mid-off", "a play and a miss"],
}

HI = {
    "DOT": ["मजबूत बचाव, कोई रन नहीं", "डॉट बॉल, बल्लेबाज चूका", "कवर में अच्छा ब्लॉक", "कोई रन नहीं, सीधा मिड-ऑन पर", "ठोस बचाव, कोई रन नहीं"],
    "SINGLE": ["एक रन के लिए काम किया", "एक रन के लिए टक किया", "पैड से नरम बल्ला, एक रन", "तेज़ एक रन", "लेग साइड में एक रन"],
    "DOUBLE": ["गैप में दो रन", "अच्छी प्लेसमेंट, दो रन", "जोरदार ड्राइव, दो और", "अच्छा स्वीप, दो रन", "स्वीपर को आसान दो रन"],
    "TRIPLE": ["उत्कृष्ट दौड़, तीन लिए", "तीन रन, बढ़िया टाइमिंग", "गहरा ड्राइव, गैप से तीन", "शानदार प्लेसमेंट, तीन रन", "तीन रन चुराए, बढ़िया जागरूकता", "दौड़कर तीन, बेहतरीन रनिंग"],
    "FOUR": ["पॉइंट से ज़ोरदार चौका", "प्यारा कवर ड्राइव, चार रन", "सीमा पर, चौका", "छोटी गेंद, चौका", "शानदार सीधा ड्राइव, चौका", "कवर से चौका", "ओवरपिच और रोप्स तक ड्राइव"],
    "SIX": ["विशाल छक्का, लॉन्ग-ऑन के ऊपर", "स्टैंड में, छक्का", "मिडविकेट के ऊपर ज़ोरदार छक्का", "गेंदबाज के ऊपर छक्का", "बड़ा छक्का, भीड़ में", "लॉन्ग-ऑफ के ऊपर छक्का"],
    "WICKET": ["किनारा और कैच! विकेट", "सीधा बोल्ड, स्टंप बिखरे", "बड़ी अपील और मिला! साफ़ LBW", "हवा में और आसान कैच, आउट", "शानदार गेंद, बोल्ड"],
    "WIDE": ["वाइड, बहुत दूर लेग पर", "वाइड, लेग साइड में", "वाइड, लेग साइड में बहाया", "वाइड बॉल, बहुत दूर ऑफ साइड", "वाइड इशारा, ऑफ स्टंप के बाहर", "वाइड, गेंदबाज ने ओवरकम्पेंसेट किया"],
    "NO_BALL": ["फ्रंट फुट नो-बॉल, फ्री हिट", "समय से पहले गेंद, नो-बॉल", "नो-बॉल, लाइन के ऊपर", "फ्रंट फुट काफी आगे, नो-बॉल", "नो-बॉल की घोषणा, अब फ्री हिट", "क्रीज पार की, नो-बॉल"],
    "FIFTY": ["अर्धशतक, एक अच्छी पारी", "अर्धशतक! संयमित पारी", "उनका अर्धशतक, पारी का आधार", "अर्धशतक के लिए धैर्यवान बल्लेबाजी", "पचास पूरा, शानदार संयम", "अर्धशतक मील का पत्थर, मजबूत पारी"],
    "CENTURY": ["शानदार शतक", "शतक! एक बड़ा बयान", "सौ पूरा, क्या पारी", "शतक हासिल, बेहतरीन ड्राइव के साथ", "पहला शतक! क्या पारी", "शतक पूरा, आक्रमण पर हावी"],
    "OTHER": ["सर्कल में, टाइमिंग नहीं", "बाहरी किनारे पर चूका", "मिड-ऑफ की ओर", "एक खेल और एक चूक"],
}

MR = {
    "DOT": ["ठाम बचाव, धाव नाही", "डॉट बॉल, फलंदाज चुकला", "कव्हरमध्ये चांगला ब्लॉक", "धाव नाही, सरळ मिड-ऑनला", "ठोस बचाव, धाव नाही"],
    "SINGLE": ["एका धावेसाठी खेळला", "एक धाव टोकली", "पॅडमधून मऊ बॅट, एक धाव", "पटकन एक धाव", "लेग साईडमध्ये एक धाव"],
    "DOUBLE": ["गॅपमध्ये दोन धावा", "चांगली प्लेसमेंट, दोन धावा", "जोरदार ड्राइव्ह, दोन आणखी", "चांगला स्वीप, दोन धावा", "स्वीपरला सोप्या दोन धावा"],
    "TRIPLE": ["उत्कृष्ट धाव, तीन घेतले", "तीन धावा, छान टायमिंग", "खोल ड्राइव्ह, गॅपमधून तीन", "छान प्लेसमेंट, तीन धावा", "तीन धावा चोरले, छान जागरूकता", "धावून तीन, उत्तम रनिंग"],
    "FOUR": ["पॉइंटमधून जोरदार चौकार", "सुंदर कव्हर ड्राइव्ह, चार धावा", "सीमेला, चौकार", "लहान चेंडू, चौकार", "छान सरळ ड्राइव्ह, चौकार", "कव्हरमधून चौकार"],
    "SIX": ["मोठा षटकार, लॉन्ग-ऑनवरून", "स्टँडमध्ये, षटकार", "मिडविकेटवरून जोरदार षटकार", "गोलंदाजावरून षटकार", "मोठा षटकार, गर्दीत", "लॉन्ग-ऑफवरून षटकार"],
    "WICKET": ["कडार आणि कॅच! विकेट", "सरळ बोल्ड, स्टंप कोसळले", "मोठी अपील आणि मिळाली! स्पष्ट LBW", "हवेत आणि सोपा कॅच, आऊट", "उत्तम चेंडू, बोल्ड"],
    "WIDE": ["वाईड, खूप दूर लेगला", "वाईड, लेग साईडमध्ये", "वाईड, लेग साईडमध्ये टाकला", "वाईड चेंडू, खूप दूर ऑफ साईड", "वाईड निर्देश, ऑफ स्टंपच्या बाहेर", "वाईड, गोलंदाजने ओवरकम्पेंसेट केले"],
    "NO_BALL": ["फ्रंट फुट नो-बॉल, फ्री हिट", "लवकर टाकले, नो-बॉल", "नो-बॉल, रेषेच्या वर", "फ्रंट फुट खूप आगाडी, नो-बॉल", "नो-बॉल घोषित, आता फ्री हिट", "रेषा लांघली, नो-बॉल"],
    "FIFTY": ["अर्धशतक, एक चांगली खेळी", "अर्धशतक! संयमी खेळी", "त्याचे अर्धशतक, खेळीचा आधार", "अर्धशटकारसाठी धैर्यवान बल्लेबाजी", "पन्नास पूर्ण, छान संयम", "अर्धशतक मैलाचा पत्थर, मजबूत खेळी"],
    "CENTURY": ["भव्य शतक", "शतक! एक मोठे विधान", "शंभर पूर्ण, काय खेळी", "शतक मिळाले, भव्य ड्राइव्हने", "पहिला शतक! काय खेळी", "शतक पूर्ण, आक्रमणावर प्रभुत्व"],
    "OTHER": ["वर्तुळात, टायमिंग नाही", "बाहेरील कडारवर चुकला", "मिड-ऑफकडे", "एक खेळ आणि एक चूक"],
}

# Code-mixed templates
HI_EN_SPLICE = ["ne {en}", "वर {en}", "और {en} लगाया", "के साथ {en}"]
MR_EN_SPLICE = ["ने {en}", "वर {en}", "आणि {en} मारला", "सह {en}"]

PLAYER_POOL = ["Virat Kohli", "Rohit Sharma", "Bumrah", "Hardik Pandya", "Steve Smith",
    "David Warner", "Pat Cummins", "Mitchell Starc", "Kane Williamson", "Babar Azam",
    "Jos Buttler", "Rashid Khan", "Kohli", "Rohit", "Pandya", "Warner", "Smith"]

DISMISSALS = ["bowled", "caught", "lbw", "run_out"]


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


def event_from_stats():
    r = random.random()
    cum = 0
    for event, prob in LEGAL_BALL_PROBS:
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
    text = ""
    if language == "en":
        text = pick_phrase(EN[event])
    elif language == "hi":
        text = pick_phrase(HI[event])
    elif language == "mr":
        text = pick_phrase(MR[event])
    else:
        base_dict = HI if language == "hi_en" else MR
        base = pick_phrase(base_dict[event])
        en_word = pick_phrase(EN[event]).split()[-1]
        text = base.replace(base.split()[-1], f"{base.split()[-1]} {en_word}")

    if players_mentions and random.random() < 0.7:
        pname = players_mentions[0]
        parts = text.split()
        insert_at = 1 if language == "en" else random.randint(1, max(1, len(parts)-1))
        parts.insert(insert_at, pname)
        text = " ".join(parts)

    return {
        "commentary_id": f"M{match_id[1:]}_C_{random.randint(10000,99999):05d}",
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
        "translator_id": "generated_v2" if is_synth else "template",
        "confidence": round(confidence, 3),
    }


def ts_for(over, ball, max_overs=20):
    per_ball = 40
    dist = (over - 1) * 6 * per_ball + (ball - 1) * per_ball
    t0 = datetime(2024, 6, 15, 10, 0, 0)
    t = t0 + timedelta(seconds=dist)
    return t.strftime("%H:%M:%S")


def generate_records_for_match(match, players_by_team, language, count, start_id):
    fmt = match["format"]
    max_overs = 20 if fmt == "T20" else 50 if fmt == "ODI" else 90
    team_a = match["team_a"]
    team_b = match["team_b"]
    squad_a = players_by_team.get(team_a, [])
    squad_b = players_by_team.get(team_b, [])
    all_names = [p["name"] for p in squad_a] + [p["name"] for p in squad_b]
    if not all_names:
        all_names = PLAYER_POOL

    records = []
    batter = random.choice(all_names)
    bowler = random.choice(all_names)
    batter_runs = {batter: 0}

    for i in range(count):
        over = random.randint(1, max_overs)
        ball = random.randint(1, 6)
        ev = event_from_stats()
        extra = extra_event() if random.random() < 0.05 else None

        batter_runs[batter] = batter_runs.get(batter, 0)
        if ev == "FOUR":
            batter_runs[batter] += 4
        elif ev == "SIX":
            batter_runs[batter] += 6
        elif ev in ("SINGLE", "DOUBLE", "TRIPLE"):
            batter_runs[batter] += {"SINGLE": 1, "DOUBLE": 2, "TRIPLE": 3}[ev]

        # milestone detection
        if batter_runs[batter] >= 100 and ev != "CENTURY" and random.random() < 0.25:
            ev = "CENTURY"
            batter_runs[batter] = 0
        elif batter_runs[batter] >= 50 and ev != "FIFTY" and random.random() < 0.3:
            ev = "FIFTY"
            batter_runs[batter] = 0

        if extra:
            ev = extra

        dismiss = None
        if ev == "WICKET":
            dismiss = random.choice(DISMISSALS)
            batter = random.choice(all_names)

        mention = [batter] if random.random() < 0.7 else [bowler]
        is_synth = language in ("hi_en", "mr_en")
        conf = 0.9 - (0.15 if is_synth else 0.0)

        rec = make_record(match["match_id"], ev, over, ball, language, ts_for(over, ball, max_overs), dismiss, mention, is_synth, conf)
        records.append(rec)

        if random.random() < 0.12:
            batter = random.choice(all_names)

    return records


def ensure_minimum_events(all_records, matches, players_by_team):
    """Add targeted records to reach MIN_EVENT_PER_CLASS for all classes."""
    from collections import Counter
    dist = Counter(r["event_label"] for r in all_records)

    needed = {}
    for ev in EVENT_CLASSES:
        if dist.get(ev, 0) < MIN_EVENT_PER_CLASS:
            needed[ev] = MIN_EVENT_PER_CLASS - dist[ev]

    if not needed:
        return all_records

    print(f"Boosting events to reach {MIN_EVENT_PER_CLASS}: {needed}")

    new_records = []
    for ev, need in needed.items():
        per_lang = need // len(TARGETS) + 1
        for lang in TARGETS:
            lang_need = min(per_lang, need)
            for _ in range(lang_need):
                match = random.choice(matches)
                over = random.randint(1, 20)
                ball = random.randint(1, 6)
                dismiss = None
                if ev == "WICKET":
                    dismiss = random.choice(DISMISSALS)
                players = [random.choice(PLAYER_POOL)]
                is_synth = lang in ("hi_en", "mr_en")

                rec = make_record(
                    match["match_id"], ev, over, ball, lang,
                    ts_for(over, ball), dismiss, players, is_synth, 0.9
                )
                new_records.append(rec)

    return all_records + new_records


def main():
    print("Loading real matches and player squads...")
    matches = load_matches()
    players_by_team = load_players()
    print(f"Loaded {len(matches)} matches, {len(players_by_team)} teams")

    all_records = []

    # Generate base records per language target
    for lang, target in TARGETS.items():
        lang_matches = random.sample(matches, min(len(matches), 12))
        base_per_match = target // len(lang_matches)
        for m in lang_matches:
            recs = generate_records_for_match(m, players_by_team, lang, base_per_match, len(all_records))
            all_records.extend(recs)

    # Ensure minimum event counts
    all_records = ensure_minimum_events(all_records, matches, players_by_team)

    # Write
    OUT_COMMENTARY.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_COMMENTARY, "w", encoding="utf-8") as f:
        for rec in all_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    from collections import Counter
    lang_dist = Counter(r["language"] for r in all_records)
    ev_dist = Counter(r["event_label"] for r in all_records)

    print(f"\nWrote {len(all_records)} commentary records to {OUT_COMMENTARY}")
    print("Language distribution:")
    for lang in sorted(TARGETS.keys()):
        print(f"  {lang}: {lang_dist.get(lang, 0)}")
    print("Event distribution:")
    for ev in EVENT_CLASSES:
        print(f"  {ev}: {ev_dist.get(ev, 0)}")

    # Audio metadata
    OUT_AUDIO = BASE / "data" / "raw" / "audio" / "audio_metadata.jsonl"
    audio_records = []
    audio_sources = [r for r in all_records if r["language"] in ("hi", "mr", "en")]
    sample_size = min(len(audio_sources), 400)
    audio_pick = random.sample(audio_sources, sample_size)

    for i, rec in enumerate(audio_pick):
        duration = round(random.uniform(4.0, 12.0), 1)
        lang = rec["language"]
        audio_records.append({
            "audio_id": f"M{rec['match_id'][1:]}_A_{i+1:03d}",
            "match_id": rec["match_id"],
            "language": lang,
            "audio_path": f"data/raw/audio/{rec['commentary_id']}.wav",
            "duration": duration,
            "transcript": rec["original_text"],
            "start_time": rec["timestamp"],
            "end_time": rec["timestamp"],
            "over": rec["over"],
            "ball": rec["ball"],
            "speaker": f"Commentator {'A' if lang == 'hi' else 'B' if lang == 'mr' else 'C'}",
            "source_type": "generated_v2" if random.random() < 0.7 else "tts",
            "quality_score": round(random.uniform(0.75, 0.98), 2),
        })

    OUT_AUDIO.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_AUDIO, "w", encoding="utf-8") as f:
        for rec in audio_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {len(audio_records)} audio metadata records to {OUT_AUDIO}")


if __name__ == "__main__":
    main()