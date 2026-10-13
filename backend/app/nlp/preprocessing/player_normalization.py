"""
Player Name Normalization

Maps player name variants to canonical forms using player_aliases.json.
Handles Hindi, Marathi, English, and abbreviated forms.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PlayerNormalizationResult:
    original_text: str
    normalized_text: str
    players_found: List[Dict]


class PlayerNameNormalizer:
    """Normalizes player names to canonical forms."""

    def __init__(self, aliases_path: Optional[str] = None):
        if aliases_path is None:
            aliases_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "player_aliases.json"

        with open(aliases_path, 'r', encoding='utf-8') as f:
            self.aliases_data = json.load(f)

        # Build reverse mapping: alias -> canonical info
        self.alias_to_canonical = {}
        self.canonical_names = set()

        for player_id, info in self.aliases_data.items():
            canonical = info['canonical']
            self.canonical_names.add(canonical)
            for alias in info['aliases']:
                self.alias_to_canonical[alias.lower()] = {
                    'canonical': canonical,
                    'player_id': player_id
                }

        # Build regex pattern (longest aliases first)
        all_aliases = sorted(self.alias_to_canonical.keys(), key=len, reverse=True)
        escaped = [re.escape(a) for a in all_aliases]
        # Word boundary that works with Devanagari
        self.pattern = re.compile(r'(?<!\w)(' + '|'.join(escaped) + r')(?!\w)', re.IGNORECASE)

    def normalize(self, text: str) -> PlayerNormalizationResult:
        """Normalize player names in text."""
        original = text
        players_found = []

        def replace(match):
            alias = match.group(0).lower()
            info = self.alias_to_canonical.get(alias)
            if info:
                players_found.append({
                    'original': match.group(0),
                    'canonical': info['canonical'],
                    'player_id': info['player_id'],
                    'position': match.start(),
                    'alias_lower': alias
                })
                return info['canonical']
            return match.group(0)

        normalized = self.pattern.sub(replace, text)

        return PlayerNormalizationResult(
            original_text=original,
            normalized_text=normalized,
            players_found=players_found
        )

    def get_canonical(self, name: str) -> Optional[str]:
        """Get canonical name for an alias."""
        info = self.alias_to_canonical.get(name.lower())
        return info['canonical'] if info else None

    def get_player_id(self, name: str) -> Optional[str]:
        """Get player ID for an alias."""
        info = self.alias_to_canonical.get(name.lower())
        return info['player_id'] if info else None

    def is_player_name(self, name: str) -> bool:
        """Check if name is a known player alias."""
        return name.lower() in self.alias_to_canonical


def normalize_player_names(text: str, aliases_path: Optional[str] = None) -> PlayerNormalizationResult:
    """Convenience function for player name normalization."""
    normalizer = PlayerNameNormalizer(aliases_path)
    return normalizer.normalize(text)


# Additional player name patterns for common cricket contexts
PLAYER_CONTEXT_PATTERNS = [
    # "X bowled Y" patterns
    (re.compile(r'\b(\w+)\s+(?:bowled|बोल्ड|बोल्ड\s+किया)\s+(\w+)', re.IGNORECASE), 'bowler_batter'),
    (re.compile(r'\b(\w+)\s+(?:caught|कॅच|कैच)\s+(?:by|ने)\s+(\w+)', re.IGNORECASE), 'fielder_bowler'),
    (re.compile(r'\b(\w+)\s+(?:lbw|एलबीडब्ल्यू)\s+(\w+)', re.IGNORECASE), 'batter_bowler'),
    # "X to Y" patterns
    (re.compile(r'\b(\w+)\s+to\s+(\w+)', re.IGNORECASE), 'bowler_batter'),
    # Scoring patterns
    (re.compile(r'\b(\w+)\s+(?:scored|made|hit|मारा|मारला)\s+(\d+)', re.IGNORECASE), 'batter_runs'),
]


def extract_player_context(text: str, normalizer: PlayerNameNormalizer) -> List[Dict]:
    """Extract structured player-context relationships from text."""
    contexts = []

    for pattern, ctx_type in PLAYER_CONTEXT_PATTERNS:
        for match in pattern.finditer(text):
            player1 = match.group(1)
            player2 = match.group(2)

            # Try to normalize both
            p1_info = normalizer.alias_to_canonical.get(player1.lower())
            p2_info = normalizer.alias_to_canonical.get(player2.lower())

            contexts.append({
                'type': ctx_type,
                'player1': {'original': player1, 'canonical': p1_info['canonical'] if p1_info else player1},
                'player2': {'original': player2, 'canonical': p2_info['canonical'] if p2_info else player2},
                'matched_text': match.group(0),
                'position': match.start()
            })

    return contexts


if __name__ == "__main__":
    normalizer = PlayerNameNormalizer()

    test_cases = [
        "कोहली ने शानदार कवर ड्राइव खेला",
        "Kohli played a brilliant cover drive",
        "विराट कोहली ने चार रन बनाए",
        "Virat hit a four",
        "बुमराह ने वॉर्नर को बोल्ड किया",
        "Bumrah bowled Warner",
        "पांड्या ने मिडविकेट के ऊपर से छक्का मारा",
        "Pandya smashed a six over midwicket",
        "रोहित शर्मा ने शतक लगाया",
        "Rohit Sharma scored a century",
        "Kohli to Bumrah",
        "रोहित ने बुमराह को चौका मारा",
    ]

    for test in test_cases:
        result = normalizer.normalize(test)
        contexts = extract_player_context(test, normalizer)
        print(f"Input:    {test}")
        print(f"Normalized: {result.normalized_text}")
        print(f"Players:    {result.players_found}")
        print(f"Contexts:   {contexts}")
        print("-" * 60)