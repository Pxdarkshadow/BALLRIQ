"""
Named Entity Recognition for cricket commentary.
Uses dictionary matching + fuzzy matching + rule patterns.
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from difflib import get_close_matches


@dataclass
class Entity:
    text: str
    label: str  # PLAYER, TEAM, EVENT, CRICKET_TERM
    start: int
    end: int
    confidence: float
    canonical: Optional[str] = None  # Normalized form


class CricketEntityExtractor:
    def __init__(self):
        # Load cricket vocabulary
        project_root = Path(__file__).parent.parent.parent.parent.parent
        vocab_path = project_root / "data" / "cricket_vocabulary.json"
        with open(vocab_path, "r", encoding="utf-8") as f:
            self.cricket_vocab = json.load(f)

        # Build reverse mapping: variant -> canonical
        self.variant_to_canonical = {}
        for canonical, variants in self.cricket_vocab.items():
            for v in variants:
                self.variant_to_canonical[v.lower()] = canonical

        # Load player aliases
        aliases_path = project_root / "data" / "player_aliases.json"
        with open(aliases_path, "r", encoding="utf-8") as f:
            self.player_aliases = json.load(f)

        # Build player alias mapping
        self.alias_to_canonical = {}
        for player_id, player_data in self.player_aliases.items():
            canonical = player_data["canonical"]
            self.alias_to_canonical[canonical.lower()] = canonical
            for alias in player_data["aliases"]:
                self.alias_to_canonical[alias.lower()] = canonical

        # Common team names
        self.team_names = {
            "india", "australia", "england", "pakistan", "south africa",
            "new zealand", "sri lanka", "west indies", "bangladesh",
            "afghanistan", "ireland", "zimbabwe", "netherlands", "scotland",
            "भारत", "ऑस्ट्रेलिया", "इंग्लैंड", "पाकिस्तान", "दक्षिण अफ्रीका",
            "न्यूजीलैंड", "श्रीलंका", "वेस्टइंडीज", "बांग्लादेश", "अफगानिस्तान",
            "भारतीय", "ऑस्ट्रेलियाई", "अंग्रेजी", "पाकिस्तानी"
        }

        # Cricket term patterns (regex for complex terms)
        self.cricket_patterns = [
            (r'\b(powerplay|power play)\b', 'CRICKET_TERM'),
            (r'\b(death overs?|deth overs?)\b', 'CRICKET_TERM'),
            (r'\b(middle overs?)\b', 'CRICKET_TERM'),
            (r'\b(strike rate)\b', 'CRICKET_TERM'),
            (r'\b(economy rate|economy)\b', 'CRICKET_TERM'),
            (r'\b(run rate|required run rate)\b', 'CRICKET_TERM'),
            (r'\b(partnership)\b', 'CRICKET_TERM'),
            (r'\b(century|hundred)\b', 'CRICKET_TERM'),
            (r'\b(half century|fifty)\b', 'CRICKET_TERM'),
            (r'\b(yorker)\b', 'CRICKET_TERM'),
            (r'\b(bouncer)\b', 'CRICKET_TERM'),
            (r'\b(googly|leg break|off break)\b', 'CRICKET_TERM'),
            (r'\b(maiden over)\b', 'CRICKET_TERM'),
            (r'\b(follow on)\b', 'CRICKET_TERM'),
            (r'\b(declaration)\b', 'CRICKET_TERM'),
        ]

        # Compile patterns
        self.compiled_patterns = [(re.compile(p, re.IGNORECASE), label) for p, label in self.cricket_patterns]

    def extract_players(self, text: str) -> List[Entity]:
        """Extract player names using alias dictionary + fuzzy matching."""
        entities = []
        words = text.split()

        # Check single words and bigrams
        for i in range(len(words)):
            # Single word
            word = words[i].lower().strip('.,!?;:')
            if word in self.alias_to_canonical:
                canonical = self.alias_to_canonical[word]
                entities.append(Entity(
                    text=words[i],
                    label="PLAYER",
                    start=text.find(words[i]),
                    end=text.find(words[i]) + len(words[i]),
                    confidence=0.9,
                    canonical=canonical
                ))

            # Bigram
            if i + 1 < len(words):
                bigram = f"{words[i]} {words[i+1]}".lower().strip('.,!?;:')
                if bigram in self.alias_to_canonical:
                    canonical = self.alias_to_canonical[bigram]
                    entities.append(Entity(
                        text=f"{words[i]} {words[i+1]}",
                        label="PLAYER",
                        start=text.find(f"{words[i]} {words[i+1]}"),
                        end=text.find(f"{words[i]} {words[i+1]}") + len(f"{words[i]} {words[i+1]}"),
                        confidence=0.95,
                        canonical=canonical
                    ))

        # Fuzzy matching for remaining
        all_aliases = list(self.alias_to_canonical.keys())
        for i in range(len(words)):
            word = words[i].lower().strip('.,!?;:')
            if len(word) > 3 and word not in self.alias_to_canonical:
                matches = get_close_matches(word, all_aliases, n=1, cutoff=0.85)
                if matches:
                    canonical = self.alias_to_canonical[matches[0]]
                    entities.append(Entity(
                        text=words[i],
                        label="PLAYER",
                        start=text.find(words[i]),
                        end=text.find(words[i]) + len(words[i]),
                        confidence=0.7,
                        canonical=canonical
                    ))

        # Deduplicate by position
        return self._deduplicate_entities(entities)

    def extract_teams(self, text: str) -> List[Entity]:
        """Extract team names."""
        entities = []
        text_lower = text.lower()

        for team in self.team_names:
            if team in text_lower:
                start = text_lower.find(team)
                # Find actual case in original text
                actual = text[start:start+len(team)]
                entities.append(Entity(
                    text=actual,
                    label="TEAM",
                    start=start,
                    end=start + len(team),
                    confidence=0.85,
                    canonical=team.title()
                ))

        return self._deduplicate_entities(entities)

    def extract_cricket_terms(self, text: str) -> List[Entity]:
        """Extract cricket terminology using vocab + patterns."""
        entities = []
        text_lower = text.lower()

        # Vocabulary-based
        for variant, canonical in self.variant_to_canonical.items():
            if variant in text_lower:
                start = text_lower.find(variant)
                actual = text[start:start+len(variant)]
                entities.append(Entity(
                    text=actual,
                    label="CRICKET_TERM",
                    start=start,
                    end=start + len(variant),
                    confidence=0.9,
                    canonical=canonical
                ))

        # Pattern-based
        for pattern, label in self.compiled_patterns:
            for match in pattern.finditer(text):
                entities.append(Entity(
                    text=match.group(),
                    label=label,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.85,
                    canonical=match.group().upper()
                ))

        return self._deduplicate_entities(entities)

    def extract_events(self, text: str) -> List[Entity]:
        """Extract event mentions (FOUR, SIX, WICKET, etc.)."""
        event_labels = {"FOUR", "SIX", "WICKET", "DOT", "SINGLE", "DOUBLE", "TRIPLE", "WIDE", "NO_BALL", "FIFTY", "CENTURY"}
        entities = []
        text_lower = text.lower()

        event_variants = {
            "FOUR": ["four", "4 runs", "चौका", "चार रन", "फोर", "चार"],
            "SIX": ["six", "6 runs", "छक्का", "सहा धावा", "सिक्स", "छह"],
            "WICKET": ["wicket", "out", "बाद", "आउट", "विकेट", "बाद झाला"],
            "DOT": ["dot", "डॉट", "शून्य"],
            "SINGLE": ["single", "1 run", "एक रन", "एक"],
            "DOUBLE": ["double", "2 runs", "दो रन", "दो"],
            "TRIPLE": ["triple", "3 runs", "तीन रन", "तीन"],
            "WIDE": ["wide", "वाइड", "वाईड"],
            "NO_BALL": ["no ball", "नो बॉल", "नो बाल"],
        }

        for event, variants in event_variants.items():
            for variant in variants:
                if variant in text_lower:
                    start = text_lower.find(variant)
                    actual = text[start:start+len(variant)]
                    entities.append(Entity(
                        text=actual,
                        label="EVENT",
                        start=start,
                        end=start + len(variant),
                        confidence=0.8,
                        canonical=event
                    ))

        return self._deduplicate_entities(entities)

    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove overlapping entities, keep highest confidence."""
        if not entities:
            return []

        # Sort by start position, then by confidence desc
        entities.sort(key=lambda e: (e.start, -e.confidence))

        result = []
        for ent in entities:
            # Check overlap with existing
            overlap = False
            for existing in result:
                if not (ent.end <= existing.start or ent.start >= existing.end):
                    overlap = True
                    break
            if not overlap:
                result.append(ent)

        return result

    def extract_all(self, text: str) -> Dict[str, List[Entity]]:
        """Extract all entity types."""
        return {
            "players": self.extract_players(text),
            "teams": self.extract_teams(text),
            "cricket_terms": self.extract_cricket_terms(text),
            "events": self.extract_events(text)
        }

    def extract_all_flat(self, text: str) -> List[Entity]:
        """Extract all entities as flat list."""
        all_entities = []
        for entities in self.extract_all(text).values():
            all_entities.extend(entities)
        # Sort by position
        all_entities.sort(key=lambda e: e.start)
        return self._deduplicate_entities(all_entities)


if __name__ == "__main__":
    extractor = CricketEntityExtractor()

    test_texts = [
        "कोहली ने शानदार कवर ड्राइव खेला और गेंद सीमा रेखा के बाहर चली गई",
        "Virat Kohli hit a magnificent four through cover",
        "बुमराह ने यॉर्कर डाली और रोहित आउट हो गए",
        "India won by 5 wickets against Australia in the powerplay",
        "Rohit Sharma scored a century in the death overs"
    ]

    for text in test_texts:
        print(f"\nText: {text}")
        result = extractor.extract_all(text)
        for label, entities in result.items():
            if entities:
                print(f"  {label}: {[(e.text, e.canonical, e.confidence) for e in entities]}")