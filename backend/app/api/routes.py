from fastapi import APIRouter, HTTPException

from app.api.models import CreateWorldRequest
from app.engine import service

router = APIRouter()


@router.post("/api/worlds")
def create_world(body: CreateWorldRequest) -> dict:
    return service.create_world(
        name=body.name,
        organism_count=body.organism_count,
        seed=body.seed,
        max_tick=body.max_tick,
    )


@router.get("/api/worlds/{world_id}")
def get_world(world_id: int) -> dict:
    try:
        return service.snapshot(world_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="world not found") from None


@router.get("/api/worlds/{world_id}/stats")
def get_stats(world_id: int) -> dict:
    try:
        return service.stats_for(world_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="world not found") from None


@router.get("/api/worlds/{world_id}/events")
def get_events(world_id: int, limit: int = 50) -> dict:
    try:
        return service.events_for(world_id, limit=limit)
    except KeyError:
        raise HTTPException(status_code=404, detail="world not found") from None


@router.get("/api/organisms/{organism_id}")
def get_organism(organism_id: str) -> dict:
    try:
        return service.organism_for(organism_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="organism not found") from None
