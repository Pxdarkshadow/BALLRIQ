from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.db.database import get_db
from backend.app.db.models import Match, Innings, BattingStat, BowlingStat, Player, Commentary, ExtractedEvent

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("/")
async def list_matches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match))
    return [m.__dict__ for m in result.scalars().all()]


@router.get("/{match_id}")
async def get_match(match_id: str, db: AsyncSession = Depends(get_db)):
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    innings_result = await db.execute(select(Innings).where(Innings.match_id == match_id))
    innings_list = innings_result.scalars().all()

    innings_data = []
    for inn in innings_list:
        batting = await db.execute(select(BattingStat).where(BattingStat.innings_id == inn.id))
        bowling = await db.execute(select(BowlingStat).where(BowlingStat.innings_id == inn.id))
        innings_data.append({
            **inn.__dict__,
            "batting_stats": [b.__dict__ for b in batting.scalars().all()],
            "bowling_stats": [b.__dict__ for b in bowling.scalars().all()],
        })

    return {**match.__dict__, "innings": innings_data}


@router.get("/{match_id}/innings")
async def get_innings(match_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Innings).where(Innings.match_id == match_id))
    innings = result.scalars().all()
    if not innings:
        raise HTTPException(status_code=404, detail="No innings found")
    return [i.__dict__ for i in innings]


@router.get("/{match_id}/commentary")
async def get_commentary(
    match_id: str,
    language: str = Query(None),
    event_type: str = Query(None),
    over_from: int = Query(None),
    over_to: int = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Commentary).where(Commentary.match_id == match_id)
    if language:
        query = query.where(Commentary.language == language)
    if event_type:
        query = query.where(Commentary.event_label == event_type)
    if over_from is not None:
        query = query.where(Commentary.over >= over_from)
    if over_to is not None:
        query = query.where(Commentary.over <= over_to)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return {"total": total, "offset": offset, "limit": limit, "items": [c.__dict__ for c in items]}


@router.get("/{match_id}/events")
async def get_events(match_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Commentary.event_label, func.count())
        .where(Commentary.match_id == match_id)
        .group_by(Commentary.event_label)
    )
    return [{"event": row[0], "count": row[1]} for row in result.all()]


@router.get("/{match_id}/stats")
async def get_stats(match_id: str, db: AsyncSession = Depends(get_db)):
    innings_result = await db.execute(select(Innings).where(Innings.match_id == match_id))
    innings_list = innings_result.scalars().all()

    all_batting, all_bowling = [], []
    for inn in innings_list:
        batting = await db.execute(select(BattingStat).where(BattingStat.innings_id == inn.id))
        bowling = await db.execute(select(BowlingStat).where(BowlingStat.innings_id == inn.id))
        all_batting.extend([b.__dict__ for b in batting.scalars().all()])
        all_bowling.extend([b.__dict__ for b in bowling.scalars().all()])

    return {"match_id": match_id, "batting": all_batting, "bowling": all_bowling}


@router.get("/{match_id}/players")
async def get_players(match_id: str, db: AsyncSession = Depends(get_db)):
    # Players are linked to matches through batting_stats/bowling_stats player_ids
    batting = await db.execute(select(BattingStat.player_id).where(BattingStat.match_id == match_id).distinct())
    bowling = await db.execute(select(BowlingStat.player_id).where(BowlingStat.match_id == match_id).distinct())
    player_ids = {r[0] for r in batting.all() if r[0]} | {r[0] for r in bowling.all() if r[0]}
    if not player_ids:
        return []
    result = await db.execute(select(Player).where(Player.player_id.in_(player_ids)))
    return [p.__dict__ for p in result.scalars().all()]
