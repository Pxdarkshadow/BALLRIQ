"""
BDA FastAPI Router: Big Data Lakehouse & DuckDB OLAP Endpoints
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.app.bda.olap_engine import CricketOLAPEngine
from backend.app.bda.streaming_analytics import LiveStreamSimulator

router = APIRouter(prefix="/api/bda", tags=["bda"])
olap_engine = CricketOLAPEngine()


class CustomSQLRequest(BaseModel):
    query: str


@router.get("/lakehouse-stats")
async def lakehouse_stats():
    """Returns storage layout, Parquet tables, partition info, and sizes."""
    return olap_engine.get_lakehouse_summary()


@router.get("/phase-analytics")
async def phase_analytics(match_id: Optional[str] = Query(None)):
    """OLAP aggregate analysis by match phase (Powerplay, Middle, Death)."""
    return olap_engine.get_phase_analytics(match_id)


@router.get("/multilingual-metrics")
async def multilingual_metrics():
    """Text length and boundary mention analytics across languages."""
    return olap_engine.get_multilingual_commentary_metrics()


@router.get("/top-batters")
async def top_batters(limit: int = Query(10, ge=1, le=50)):
    """Top batting performances aggregated across all matches."""
    return olap_engine.get_top_batting_aggregates(limit)


@router.get("/top-bowlers")
async def top_bowlers(limit: int = Query(10, ge=1, le=50)):
    """Top bowling performances aggregated across all matches."""
    return olap_engine.get_top_bowling_aggregates(limit)


@router.post("/query")
async def execute_custom_sql(req: CustomSQLRequest):
    """Execute arbitrary read-only analytical SQL query on the Parquet Lake."""
    return olap_engine.execute_custom_sql(req.query)


@router.get("/streaming-metrics")
async def streaming_metrics(match_id: Optional[str] = None):
    """Simulate streaming window metrics for real-time momentum analysis."""
    # Pull recent balls from OLAP engine
    where_clause = f"WHERE match_id = '{match_id}'" if match_id else ""
    query = f"SELECT over, ball, event_label, runs, is_wicket, is_boundary, is_dot FROM ball_events {where_clause} ORDER BY over, ball LIMIT 60;"
    res = olap_engine.con.execute(query).df().to_dict(orient="records")

    simulator = LiveStreamSimulator(window_size=20)
    timeline = []
    for ball in res:
        metrics = simulator.process_ball_event(ball)
        timeline.append({
            "over": ball["over"],
            "ball": ball["ball"],
            "event_label": ball["event_label"],
            "metrics": metrics
        })

    return {
        "match_id": match_id or "All",
        "stream_length": len(timeline),
        "latest_metrics": timeline[-1]["metrics"] if timeline else {},
        "timeline_sample": timeline[-15:]
    }
