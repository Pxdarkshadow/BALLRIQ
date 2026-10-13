"""
Cricket Event Extraction - converts unstructured commentary into structured events.
Combines NLP event classification with rule-based attribute extraction.
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from backend.app.nlp.entity_extraction.entity_extractor import CricketEntityExtractor, Entity
from backend.app.nlp.models.baseline import BaselineEventClassifier


@dataclass
class StructuredEvent:
    """Structured cricket event extracted from commentary."""
    event_type: str          # FOUR, SIX, WICKET, DOT, SINGLE, etc.
    event_subtype: str       # e.g., BOWLED, CAUGHT, LBW for WICKET
    batsman: Optional[str]   # Batsman involved
    bowler: Optional[str]    # Bowler involved
    fielder: Optional[str]   # Fielder (for catches, run outs)
    runs: int                # Runs scored
    over: Optional[float]    # Over number
    ball: Optional[int]      # Ball number
    commentary_id: Optional[str]  # Source commentary ID
    confidence: float        # Extraction confidence
    importance_score: float  # Match importance (0-1)
    raw_text: str            # Original commentary text


class CricketEventExtractor:
    """
    Two-stage event extraction:
    1. MODEL → Event classification (FOUR, SIX, WICKET, etc.)
    2. RULE SYSTEM → Structured attribute extraction (batsman, bowler, dismissal type, etc.)
    """

    def __init__(self, event_classifier=None):
        self.entity_extractor = CricketEntityExtractor()
        self.event_classifier = event_classifier

        # Dismissal type patterns
        self.dismissal_patterns = {
            "BOWLED": [r"\b(bowled|बोल्ड|क्लीन बोल्ड)\b"],
            "CAUGHT": [r"\b(caught|कैच|कॅच)\b", r"\bcaught (behind|behind the wicket|and bowled)\b"],
            "LBW": [r"\b(lbw|l\.?b\.?w\.?|एलबीडब्ल्यू|पगबाधा)\b"],
            "RUN_OUT": [r"\b(run.?out|रन.?आउट|रन.?आउट)\b"],
            "STUMPED": [r"\b(stumped|स्टम्प|स्टम्प्ड)\b"],
            "HIT_WICKET": [r"\b(hit.?wicket|हिट.?विकेट)\b"],
            "HANDLED_BALL": [r"\b(handled.?ball|हैंडल्ड.?बॉल)\b"],
            "OBSTRUCTING": [r"\b(obstructing|ऑब्स्ट्रक्टिंग)\b"],
            "TIMED_OUT": [r"\b(timed.?out|टाइम.?आउट)\b"],
        }

        # Fielder patterns for catches
        self.catch_fielder_patterns = [
            r"caught\s+(\w+\s+\w+)\s+b\s+(\w+\s+\w+)",
            r"caught\s+(\w+)\s+b\s+(\w+\s+\w+)",
            r"c\s+(\w+\s+\w+)\s+b\s+(\w+\s+\w+)",
        ]

        # Bowler patterns
        self.bowler_patterns = [
            r"(\w+\s+\w+)\s+(?:bowls?|bowling|डालत|डालते)",
            r"(\w+\s+\w+)\s+(?:to|vs\.?|against)\s+(\w+\s+\w+)",
        ]

        # Over/ball patterns
        self.over_patterns = [
            r"(\d+\.\d+)\s*(?:over|ov|ओवर)",
            r"over\s+(\d+\.\d+)",
            r"(\d+\.\d+)",
        ]

    def classify_event(self, text: str) -> Dict:
        """Stage 1: Classify event type using NLP model."""

        if self.event_classifier and self.event_classifier.is_fitted:
            result = self.event_classifier.predict_single(text)
            return {
                "event_type": result["predicted_event"],
                "confidence": result["confidence"],
                "all_probabilities": result["all_probabilities"]
            }
        else:
            # Fallback: rule-based classification
            return self._rule_based_classify(text)

    def _rule_based_classify(self, text: str) -> Dict:
        """Fallback rule-based event classification."""
        text_lower = text.lower()

        # Check for explicit event keywords
        if any(w in text_lower for w in ["four", "चौका", "चार रन", "फोर", "बाउंड्री"]):
            return {"event_type": "FOUR", "confidence": 0.85, "all_probabilities": {}}
        elif any(w in text_lower for w in ["six", "छक्का", "सहा धावा", "सिक्स", "छह रन"]):
            return {"event_type": "SIX", "confidence": 0.85, "all_probabilities": {}}
        elif any(w in text_lower for w in ["wicket", "out", "बाद", "आउट", "विकेट"]):
            return {"event_type": "WICKET", "confidence": 0.8, "all_probabilities": {}}
        elif any(w in text_lower for w in ["dot", "डॉट", "शून्य", "कोई रन नहीं"]):
            return {"event_type": "DOT", "confidence": 0.8, "all_probabilities": {}}
        elif any(w in text_lower for w in ["single", "एक रन", "एक"]):
            return {"event_type": "SINGLE", "confidence": 0.75, "all_probabilities": {}}
        elif any(w in text_lower for w in ["double", "दो रन", "दो"]):
            return {"event_type": "DOUBLE", "confidence": 0.75, "all_probabilities": {}}
        elif any(w in text_lower for w in ["wide", "वाइड"]):
            return {"event_type": "WIDE", "confidence": 0.8, "all_probabilities": {}}
        elif any(w in text_lower for w in ["no ball", "नो बॉल", "नो बाल"]):
            return {"event_type": "NO_BALL", "confidence": 0.8, "all_probabilities": {}}
        else:
            return {"event_type": "OTHER", "confidence": 0.5, "all_probabilities": {}}

    def extract_dismissal_type(self, text: str) -> str:
        """Extract dismissal type for WICKET events."""
        text_lower = text.lower()

        for dismissal_type, patterns in self.dismissal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return dismissal_type
        return "UNKNOWN"

    def extract_batsman(self, text: str, entities: List[Entity]) -> Optional[str]:
        """Extract batsman from text and entities."""
        # Priority 1: Player entity marked as batsman context
        for ent in entities:
            if ent.label == "PLAYER" and ent.confidence > 0.8:
                # Check if context suggests batsman
                context = text[max(0, ent.start-30):ent.end+30].lower()
                if any(w in context for w in ["batsman", "batter", "बल्लेबाज", "रन", "scored", "hit", "मारा", "खेला"]):
                    return ent.canonical

        # Priority 2: Any player entity
        players = [e for e in entities if e.label == "PLAYER"]
        if players:
            return max(players, key=lambda e: e.confidence).canonical

        return None

    def extract_bowler(self, text: str, entities: List[Entity]) -> Optional[str]:
        """Extract bowler from text and entities."""
        text_lower = text.lower()

        # Pattern-based extraction
        for pattern in self.bowler_patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).strip()
                # Try to canonicalize
                for ent in entities:
                    if ent.label == "PLAYER" and ent.canonical.lower() in name.lower():
                        return ent.canonical
                return name.title()

        # Check entities - bowler often mentioned with "bowls", "bowling", "यॉर्कर"
        for ent in entities:
            if ent.label == "PLAYER" and ent.confidence > 0.7:
                context = text[max(0, ent.start-20):ent.end+20].lower()
                if any(w in context for w in ["bowl", "bowls", "bowling", "यॉर्कर", "डाल", "गेंद"]):
                    return ent.canonical

        return None

    def extract_fielder(self, text: str, dismissal_type: str) -> Optional[str]:
        """Extract fielder for catches/run outs."""
        if dismissal_type not in ["CAUGHT", "RUN_OUT"]:
            return None

        text_lower = text.lower()

        for pattern in self.catch_fielder_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1).title()

        # Look for "c [Fielder] b [Bowler]" pattern
        c_match = re.search(r"c\s+(\w+(?:\s+\w+)?)\s+b\s+", text_lower)
        if c_match:
            return c_match.group(1).title()

        return None

    def extract_over_ball(self, text: str) -> tuple:
        """Extract over and ball number."""
        # Look for patterns like "18.4", "18.5", "over 18.4"
        for pattern in self.over_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    over_str = match.group(1)
                    over = float(over_str)
                    ball = int(round((over - int(over)) * 10))
                    return over, ball
                except:
                    pass
        return None, None

    def extract_runs(self, text: str, event_type: str) -> int:
        """Extract runs scored from text."""
        event_runs = {
            "FOUR": 4,
            "SIX": 6,
            "SINGLE": 1,
            "DOUBLE": 2,
            "TRIPLE": 3,
            "WIDE": 1,
            "NO_BALL": 1,
            "DOT": 0,
        }

        if event_type in event_runs:
            return event_runs[event_type]

        # Try to extract from text
        text_lower = text.lower()
        run_matches = re.findall(r'(\d+)\s*(?:run|runs|रन)', text_lower)
        if run_matches:
            return int(run_matches[0])

        return 0

    def calculate_importance(self, event: StructuredEvent, match_context: Dict = None) -> float:
        """Calculate importance score for an event."""
        base_scores = {
            "WICKET": 0.9,
            "SIX": 0.7,
            "FOUR": 0.5,
            "FIFTY": 0.6,
            "CENTURY": 0.8,
            "WIDE": 0.2,
            "NO_BALL": 0.3,
            "DOT": 0.1,
            "SINGLE": 0.1,
            "DOUBLE": 0.2,
            "TRIPLE": 0.3,
        }

        score = base_scores.get(event.event_type, 0.3)

        # Boost for dismissal type
        if event.event_type == "WICKET":
            dismissal_boost = {
                "BOWLED": 0.1, "CAUGHT": 0.05, "LBW": 0.1,
                "RUN_OUT": 0.15, "STUMPED": 0.1
            }
            score += dismissal_boost.get(event.event_subtype, 0)

        # Match context adjustments
        if match_context:
            # Late overs = higher pressure
            if event.over and event.over > 18:
                score += 0.1
            elif event.over and event.over > 15:
                score += 0.05

            # Close match = higher importance
            if match_context.get("run_rate_diff", 0) < 2:
                score += 0.1

        return min(score, 1.0)

    def extract_event(self, text: str, commentary_id: str = None, match_context: Dict = None) -> StructuredEvent:
        """Full event extraction pipeline."""
        # Stage 1: Event classification
        classification = self.classify_event(text)
        event_type = classification["event_type"]
        confidence = classification["confidence"]

        # Extract entities
        entities = self.entity_extractor.extract_all_flat(text)

        # Stage 2: Structured attribute extraction
        dismissal_type = self.extract_dismissal_type(text) if event_type == "WICKET" else ""
        batsman = self.extract_batsman(text, entities)
        bowler = self.extract_bowler(text, entities)
        fielder = self.extract_fielder(text, dismissal_type)
        runs = self.extract_runs(text, event_type)
        over, ball = self.extract_over_ball(text)

        # Calculate importance
        event = StructuredEvent(
            event_type=event_type,
            event_subtype=dismissal_type,
            batsman=batsman,
            bowler=bowler,
            fielder=fielder,
            runs=runs,
            over=over,
            ball=ball,
            commentary_id=commentary_id,
            confidence=confidence,
            importance_score=0.0,  # Will be set below
            raw_text=text
        )

        event.importance_score = self.calculate_importance(event, match_context)

        return event

    def extract_events_batch(self, commentaries: List[Dict], match_context: Dict = None) -> List[StructuredEvent]:
        """Extract events from a batch of commentaries."""
        events = []
        for c in commentaries:
            text = c.get("original_text") or c.get("preprocessed_text") or c.get("normalized_text", "")
            commentary_id = c.get("commentary_id")
            if text:
                event = self.extract_event(text, commentary_id, match_context)
                events.append(event)
        return events


if __name__ == "__main__":
    extractor = CricketEventExtractor()

    test_commentaries = [
        "18.4 Bumrah bowls a yorker and Kohli is bowled!",
        "18.5 Sharma hits Starc for six over long on!",
        "19.2 Kohli drives through cover for four runs.",
        "15.3 Pandya caught by Smith off Cummins.",
        "10.1 Wide! Sharma misses the sweep.",
        "12.4 LBW! Rohit trapped in front by Bumrah.",
        "45.2 Century for Kohli! What an innings.",
    ]

    for i, text in enumerate(test_commentaries):
        event = extractor.extract_event(text, f"C{i+1}")
        print(f"\nText: {text}")
        print(f"  Event: {event.event_type} ({event.event_subtype})")
        print(f"  Batsman: {event.batsman}")
        print(f"  Bowler: {event.bowler}")
        print(f"  Fielder: {event.fielder}")
        print(f"  Runs: {event.runs}")
        print(f"  Over: {event.over}.{event.ball}")
        print(f"  Confidence: {event.confidence:.2f}")
        print(f"  Importance: {event.importance_score:.2f}")