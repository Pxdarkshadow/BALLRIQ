"""Generate cleaned, language-detected, and annotation files from raw commentary."""
import sys, json, re, csv
sys.path.insert(0, 'D:/miniproject')

URL_PATTERN = re.compile(r'https?://\S+')
HTML_PATTERN = re.compile(r'<[^>]+>')

def clean_text(text):
    text = text.strip()
    text = URL_PATTERN.sub('', text)
    text = HTML_PATTERN.sub('', text)
    return text.strip()

# 1. Cleaned commentary (first 50 lines)
print("=== Cleaning commentary (first 50 records) ===")
with open('D:/miniproject/data/raw/commentary/commentary.jsonl', 'r', encoding='utf-8') as f:
    lines = [f.readline() for _ in range(50) if f.readline()]

cleaned = []
for line in lines:
    if not line.strip():
        continue
    rec = json.loads(line)
    rec['original_text'] = clean_text(rec['original_text'])
    if 'normalized_text' in rec:
        rec['normalized_text'] = clean_text(rec['normalized_text'])
    cleaned.append(json.dumps(rec, ensure_ascii=False))

with open('D:/miniproject/data/interim/cleaned/cleaned_commentary.jsonl', 'w', encoding='utf-8') as f:
    f.write('\n'.join(cleaned) + '\n')
print(f"Cleaned: {len(cleaned)} records written")

# 2. Language detected (ALL records)
print("\n=== Language detection (all records) ===")
from backend.app.nlp.preprocessing.language_processing import identify_language

detected = []
with open('D:/miniproject/data/raw/commentary/commentary.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if not line.strip():
            continue
        rec = json.loads(line)
        lang_result = identify_language(rec['original_text'])
        out = {
            'commentary_id': rec['commentary_id'],
            'original_text': rec['original_text'],
            'language': rec.get('language', ''),
            'detected_language': lang_result.language,
            'language_confidence': round(lang_result.confidence, 4),
            'is_code_mixed': lang_result.is_code_mixed,
            'scores': {k: round(v, 4) for k, v in lang_result.scores.items()}
        }
        detected.append(json.dumps(out, ensure_ascii=False))
        if i % 1000 == 0:
            print(f"  Processed {i} records...")

with open('D:/miniproject/data/interim/language_detected/detected_languages.jsonl', 'w', encoding='utf-8') as f:
    f.write('\n'.join(detected) + '\n')
print(f"Language detected: {len(detected)} records written")

# 3. Annotations CSV (first 100 records)
print("\n=== Creating annotation CSV (first 100 records) ===")
with open('D:/miniproject/data/raw/commentary/commentary.jsonl', 'r', encoding='utf-8') as f:
    rows = []
    for i, line in enumerate(f, 1):
        if i > 100:
            break
        if not line.strip():
            continue
        rec = json.loads(line)
        rows.append({
            'text': rec['original_text'],
            'event_label': rec.get('event_label', 'OTHER'),
            'annotated_by': 'auto_extract',
            'date': '2026-09-09'
        })

with open('D:/miniproject/data/annotations/event_labels.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['text', 'event_label', 'annotated_by', 'date'])
    writer.writeheader()
    writer.writerows(rows)
print(f"Annotations CSV: {len(rows)} rows written")
print("\nAll data files generated successfully.")
