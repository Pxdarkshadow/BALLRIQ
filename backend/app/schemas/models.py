"""Pydantic request/response models for the API."""
from pydantic import BaseModel, ConfigDict, Field


class _ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---- Responses for DB entities ----

class MatchResponse(_ORM):
    match_id: str
    date: str | None = None
    format: str | None = None
    tournament: str | None = None
    venue: str | None = None
    team_a: str | None = None
    team_b: str | None = None
    winner: str | None = None
    result: str | None = None
    toss_winner: str | None = None
    toss_decision: str | None = None


class PlayerResponse(_ORM):
    player_id: str
    name: str | None = None
    team: str | None = None
    role: str | None = None
    batting_style: str | None = None
    bowling_style: str | None = None


class CommentaryResponse(_ORM):
    commentary_id: str
    match_id: str
    language: str | None = None
    original_text: str | None = None
    normalized_text: str | None = None
    timestamp: str | None = None
    over: int | None = None
    ball: int | None = None
    player_mentions: list[str] | None = None
    team_mentions: list[str] | None = None
    event_label: str | None = None
    dismissal_type: str | None = None
    is_synthetic: int | None = None
    translator_id: str | None = None
    confidence: float | None = None


class EventResponse(_ORM):
    id: int
    match_id: str
    event_type: str | None = None
    event_subtype: str | None = None
    player: str | None = None
    team: str | None = None
    bowler: str | None = None
    batter: str | None = None
    fielder: str | None = None
    dismissal_type: str | None = None
    runs: int | None = None
    over: int | None = None
    ball: int | None = None
    importance_score: float | None = None
    confidence: float | None = None
    raw_text: str | None = None
    commentary_id: str | None = None


class BattingStatResponse(_ORM):
    id: int
    record_id: str | None = None
    match_id: str
    innings_id: str
    player_id: str | None = None
    runs: int | None = None
    balls: int | None = None
    fours: int | None = None
    sixes: int | None = None
    strike_rate: float | None = None
    dismissal: str | None = None


class BowlingStatResponse(_ORM):
    id: int
    record_id: str | None = None
    match_id: str
    innings_id: str
    player_id: str | None = None
    overs: float | None = None
    runs_conceded: int | None = None
    wickets: int | None = None
    economy: float | None = None
    wides: int | None = None
    no_balls: int | None = None


class MatchStatsResponse(BaseModel):
    match: MatchResponse
    batting: list[BattingStatResponse]
    bowling: list[BowlingStatResponse]


# ---- Filters / requests ----

class CommentaryFilter(BaseModel):
    language: str | None = None
    event_type: str | None = None
    over_min: int | None = None
    over_max: int | None = None
    match_id: str | None = None


class QueryRequest(BaseModel):
    text: str
    language: str | None = None
    match_id: str | None = None


# ---- LLM / NLP / IR service outputs ----

class Source(BaseModel):
    text: str
    score: float | None = None
    metadata: dict = {}


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source] = []
    scores: dict = {}
    metadata: dict = {}


class NLPResultResponse(BaseModel):
    detected_language: str | None = None
    entities: list[dict] = []
    events: list[dict] = []
    structured_output: dict = {}


class RankedDocument(BaseModel):
    text: str
    score: float = 0.0
    metadata: dict = {}


class IRResultResponse(BaseModel):
    query: str | None = None
    documents: list[RankedDocument] = []
    scores: list[float] = []


# ---- Dataset / preprocessing / evaluations ----

class DatasetStatsResponse(BaseModel):
    counts: dict[str, int] = {}
    total_records: int = 0


class PreprocessingStepResponse(BaseModel):
    step_name: str
    status: str
    records_processed: int = 0
    details: dict = {}


class NLPMetricsResponse(BaseModel):
    pass

class NLPClassifyResponse(BaseModel):
    predicted_event: str
    confidence: float
    all_probabilities: dict[str, float]
    preprocessed_text: str | None = None
    detected_language: str | None = None
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    details: dict = {}


class IRMetricsResponse(BaseModel):
    precision_at_k: float | None = None
    recall: float | None = None
    mrr: float | None = None
    ndcg: float | None = None
    map: float | None = None
    details: dict = {}