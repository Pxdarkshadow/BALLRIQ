from backend.app.nlp.preprocessing.pipeline import NLPPreprocessingPipeline
import json
import sys

# Force UTF-8 encoding for stdout
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pipeline = NLPPreprocessingPipeline()

test_records = [
    {'commentary_id': 'M001_C_0001', 'original_text': 'बुमराह ने शानदार यॉर्कर डाली और बल्लेबाज को चकमा दिया।', 'language': 'hi'},
    {'commentary_id': 'M001_C_0002', 'original_text': 'चौका! वॉर्नर ने कवर से चार रन बनाए।', 'language': 'hi'},
    {'commentary_id': 'M001_C_0003', 'original_text': 'विकेट! बुमराह ने सीधा बोल्ड कर दिया। वॉर्नर पवेलियन लौटे।', 'language': 'hi'},
    {'commentary_id': 'M001_C_0017', 'original_text': 'बुमराहने छान यॉर्कर टाकली आणि फलंदाजला चकवले।', 'language': 'mr'},
    {'commentary_id': 'M001_C_0025', 'original_text': 'Virat ne शानदार four मारा', 'language': 'hi_en'},
]

print('Testing pipeline on sample records...')
for record in test_records:
    result = pipeline.process(record['original_text'])
    out = {
        'input': record['original_text'],
        'output': result.final_text,
        'language': result.detected_language,
        'confidence': result.language_confidence,
        'code_mixed': result.is_code_mixed,
        'tokens': result.tokens,
        'entities': len(result.entities),
        'cricket_events': result.cricket_events
    }
    print(json.dumps(out, ensure_ascii=False))