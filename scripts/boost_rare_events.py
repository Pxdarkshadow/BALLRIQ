#!/usr/bin/env python3
"""
Targeted generator for rare event classes to reach 300+ per class.
"""

import json
import random
import csv
import hashlib

random.seed(42)

def load_matches():
    rows = []
    with open('data/raw/matches/matches.csv') as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows

matches = load_matches()
valid_match_ids = [m['match_id'] for m in matches]

# Current counts from existing data
current = {
    'DOT': 5368,
    'SINGLE': 3955,
    'DOUBLE': 947,
    'FOUR': 660,
    'SIX': 333,
    'WICKET': 300,
    'WIDE': 29,
    'NO_BALL': 14,
    'FIFTY': 21,
    'CENTURY': 0,
    'TRIPLE': 66,
    'OTHER': 322,
}

TARGET_MIN = 300

# Calculate needed
needed = {}
for ev, count in current.items():
    if count < TARGET_MIN:
        needed[ev] = TARGET_MIN - count

print("Events needing boost:", needed)

# English phrasing for rare events
EN_PHRASES = {
    "FIFTY": [
        "brings up his fifty, a well-crafted innings",
        "FIFTY! steady knock reaches the milestone",
        "fifty for him, anchored the innings",
        "reaches fifty with a gentle push",
        "half-century up, composed batting",
        "fifty comes up, great composure shown",
        "FIFTY reached with a single to midwicket",
        "milestone fifty, patient innings built",
    ],
    "CENTURY": [
        "brings up a magnificent CENTURY",
        "CENTURY! a statement knock",
        "hundred up, what an innings",
        "century reached with a glorious drive",
        "CENTURY! maiden ton for the batsman",
        "HUNDRED up, dominated the attack",
        "century completed with a boundary",
        "magnificent century, stands tall",
    ],
    "WIDE": [
        "wide called, too far down leg",
        "that's a wide, drifting down leg",
        "wide, sprayed down the leg side",
        "wide ball, too far outside off",
        "wide signalled, well outside off stump",
        "wide, bowler overcompensated",
    ],
    "NO_BALL": [
        "front foot no-ball, free hit coming",
        "overstepped, no-ball signalled",
        "no-ball, over the line",
        "no-ball, front foot well over",
        "no-ball called, free hit now",
        "overstepped the crease, no-ball",
    ],
    "TRIPLE": [
        "excellent running, three taken",
        "three runs, great timing",
        "driven deep, three through the gap",
        "superb placement, three to deep midwicket",
        "three runs stolen, great awareness",
        "races three, brilliant running",
    ],
}

HI_PHRASES = {
    "FIFTY": [
        "अर्धशतक, एक अच्छी पारी",
        "अर्धशतक! संयमित पारी",
        "उनका अर्धशतक, पारी का आधार",
        "अर्धशतक के लिए धैर्यवान बल्लेबाजी",
        "पचास पूरा, शानदार संयम",
        "अर्धशतक मील का पत्थर, मजबूत पारी",
    ],
    "CENTURY": [
        "शानदार शतक",
        "शतक! एक बड़ा बयान",
        "सौ पूरा, क्या पारी",
        "शतक हासिल, बेहतरीन ड्राइव के साथ",
        "पहला शतक! क्या पारी",
        "शतक पूरा, आक्रमण पर हावी",
    ],
    "WIDE": [
        "वाइड, बहुत दूर लेग पर",
        "वाइड, लेग साइड में",
        "वाइड, लेग साइड में बहाया",
        "वाइड बॉल, बहुत दूर ऑफ साइड",
        "वाइड इशारा, ऑफ स्टंप के बाहर",
        "वाइड, गेंदबाज ने ओवरकम्पेंसेट किया",
    ],
    "NO_BALL": [
        "फ्रंट फुट नो-बॉल, फ्री हिट",
        "समय से पहले गेंद, नो-बॉल",
        "नो-बॉल, लाइन के ऊपर",
        "फ्रंट फुट काफी आगे, नो-बॉल",
        "नो-बॉल की घोषणा, अब फ्री हिट",
        "क्रीज पार की, नो-बॉल",
    ],
    "TRIPLE": [
        "उत्कृष्ट दौड़, तीन लिए",
        "तीन रन, बढ़िया टाइमिंग",
        "गहरा ड्राइव, गैप से तीन",
        "शानदार प्लेसमेंट, तीन रन",
        "तीन रन चुराए, बढ़िया जागरूकता",
        "दौड़कर तीन, बेहतरीन रनिंग",
    ],
}

MR_PHRASES = {
    "FIFTY": [
        "अर्धशतक, एक चांगली खेळी",
        "अर्धशतक! संयमी खेळी",
        "त्याचे अर्धशतक, खेळीचा आधार",
        "अर्धशटकारसाठी धैर्यवान बल्लेबाजी",
        "पन्नास पूर्ण, छान संयम",
        "अर्धशतक मैलाचा पत्थर, मजबूत खेळी",
    ],
    "CENTURY": [
        "भव्य शतक",
        "शतक! एक मोठे विधान",
        "शंभर पूर्ण, काय खेळी",
        "शतक मिळाले, भव्य ड्राइव्हने",
        "पहिला शतक! काय खेळी",
        "शतक पूर्ण, आक्रमणावर प्रभुत्व",
    ],
    "WIDE": [
        "वाईड, खूप दूर लेगला",
        "वाईड, लेग साईडमध्ये",
        "वाईड, लेग साईडमध्ये टाकला",
        "वाईड चेंडू, खूप दूर ऑफ साईड",
        "वाईड निर्देश, ऑफ स्टंपच्या बाहेर",
        "वाईड, गोलंदाजने ओवरकम्पेंसेट केले",
    ],
    "NO_BALL": [
        "फ्रंट फुट नो-बॉल, फ्री हिट",
        "लवकर टाकले, नो-बॉल",
        "नो-बॉल, रेषेच्या वर",
        "फ्रंट फुट खूप आगाडी, नो-बॉल",
        "नो-बॉल घोषित, आता फ्री हिट",
        "रेषा लांघली, नो-बॉल",
    ],
    "TRIPLE": [
        "उत्कृष्ट धाव, तीन घेतले",
        "तीन धावा, छान टायमिंग",
        "खोल ड्राइव्ह, गॅपमधून तीन",
        "छान प्लेसमेंट, तीन धावा",
        "तीन धावा चोरले, छान जागरूकता",
        "धावून तीन, उत्तम रनिंग",
    ],
}

def pick_phrase(phrases):
    return random.choice(phrases)

def make_record(match_id, event, over, ball, language, ts, dismiss, players_mentions, is_synth, confidence):
    text = ""
    if language == "en":
        text = pick_phrase(EN_PHRASES[event])
    elif language == "hi":
        text = pick_phrase(HI_PHRASES[event])
    elif language == "mr":
        text = pick_phrase(MR_PHRASES[event])
    else:
        # code-mixed
        base_dict = HI_PHRASES if language == "hi_en" else MR_PHRASES
        base = pick_phrase(base_dict[event])
        en_word = pick_phrase(EN_PHRASES[event]).split()[-1]
        text = base.replace(base.split()[-1], f"{base.split()[-1]} {en_word}")

    if players_mentions and random.random() < 0.7:
        pname = players_mentions[0]
        parts = text.split()
        insert_at = 1 if language == "en" else random.randint(1, max(1, len(parts)-1))
        parts.insert(insert_at, pname)
        text = " ".join(parts)

    return {
        "commentary_id": f"M{abs(hash(f'{match_id}{event}')) % 900 + 100:03d}_C_{random.randint(10000,99999):05d}",
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
        "translator_id": "rare_event_generator",
        "confidence": round(confidence, 3),
    }

def ts_for(over, ball):
    per_ball = 40
    dist = (over - 1) * 6 * per_ball + (ball - 1) * per_ball
    t0 = datetime(2024, 6, 15, 10, 0, 0)
    t = t0 + timedelta(seconds=dist)
    return t.strftime("%H:%M:%S")

from datetime import datetime, timedelta

new_records = []

for event, need in needed.items():
    if need <= 0:
        continue
    print(f"Generating {need} more {event} records...")

    # Generate across languages proportionally
    lang_targets = {
        'en': need * 3,
        'hi': need,
        'mr': need,
        'hi_en': need // 2,
        'mr_en': need // 2,
    }

    for lang, n in lang_targets.items():
        for _ in range(n):
            match_id = random.choice(valid_match_ids)
            over = random.randint(1, 20)
            ball = random.randint(1, 6)
            dismiss = None
            if event == "WICKET":
                dismiss = random.choice(['bowled', 'caught', 'lbw', 'run_out'])

            players = [random.choice(['Virat Kohli', 'Rohit Sharma', 'Bumrah', 'Hardik Pandya', 'Steve Smith', 'David Warner'])]

            rec = make_record(
                match_id, event, over, ball, lang,
                ts_for(over, ball), dismiss, players,
                lang in ('hi_en', 'mr_en'), 0.88
            )
            new_records.append(rec)

print(f"Generated {len(new_records)} additional records")

# Append to existing file
with open('data/raw/commentary/commentary.jsonl', 'a', encoding='utf-8') as f:
    for rec in new_records:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

print("Appended to commentary.jsonl")

# Verify
with open('data/raw/commentary/commentary.jsonl', encoding='utf-8') as f:
    all_records = [json.loads(l) for l in f]

from collections import Counter
lang = Counter(r['language'] for r in all_records)
ev = Counter(r['event_label'] for r in all_records)

print(f"\nTotal records: {len(all_records)}")
print(f"Language: {dict(lang)}")
print(f"Events: {dict(ev)}")