from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import ActivityEvent


router = APIRouter()


@router.get("")
def list_activity_route(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    events = db.scalars(
        select(ActivityEvent).order_by(ActivityEvent.created_at.desc()).limit(limit)
    )
    return [
        {
            "id": event.id,
            "action": event.action,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "data": event.event_data,
            "created_at": event.created_at,
        }
        for event in events
    ]
