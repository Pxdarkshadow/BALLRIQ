"""
Streaming Analytics Simulator: Computes windowed rolling statistics over ball-by-ball commentary streams.
Simulates real-time Big Data Stream Processing (e.g. Apache Spark Streaming / Kafka).
"""
from typing import List, Dict, Any
from collections import deque


class LiveStreamSimulator:
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.ball_window = deque(maxlen=window_size)
        self.total_processed = 0

    def process_ball_event(self, ball_event: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest a ball event and compute sliding-window metrics."""
        self.ball_window.append(ball_event)
        self.total_processed += 1

        recent_runs = sum(b.get("runs", 0) for b in self.ball_window)
        recent_wickets = sum(1 for b in self.ball_window if b.get("is_wicket", 0) == 1)
        recent_boundaries = sum(1 for b in self.ball_window if b.get("is_boundary", 0) == 1)
        recent_dots = sum(1 for b in self.ball_window if b.get("is_dot", 0) == 1)
        window_len = len(self.ball_window)

        # Rolling run rate over last N balls (overs = window_len / 6)
        rolling_rr = round((recent_runs / (window_len / 6.0)), 2) if window_len > 0 else 0.0
        boundary_rate = round((recent_boundaries / window_len) * 100, 1) if window_len > 0 else 0.0
        dot_rate = round((recent_dots / window_len) * 100, 1) if window_len > 0 else 0.0

        # Pressure Index (0-100 scale: high dots + wickets increases pressure)
        pressure_index = min(100.0, round((dot_rate * 0.6) + (recent_wickets * 15.0) - (boundary_rate * 0.4), 1))
        pressure_index = max(0.0, pressure_index)

        return {
            "total_stream_events": self.total_processed,
            "window_size_balls": window_len,
            "rolling_run_rate": rolling_rr,
            "recent_runs": recent_runs,
            "recent_wickets": recent_wickets,
            "recent_boundaries": recent_boundaries,
            "dot_percentage": dot_rate,
            "pressure_index": pressure_index,
            "momentum": "Batting Surge" if rolling_rr > 9.5 else ("Bowling Strangle" if pressure_index > 60 else "Balanced")
        }


def simulate_stream_for_match(ball_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    streamer = LiveStreamSimulator(window_size=30)
    timeline = []
    for event in ball_events:
        metrics = streamer.process_ball_event(event)
        timeline.append({
            "over": event.get("over"),
            "ball": event.get("ball"),
            "event_label": event.get("event_label"),
            "metrics": metrics
        })
    return timeline
