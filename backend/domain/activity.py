from sqlalchemy.orm import Session

from db.models import ActivityEvent


def record_event(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str,
    data: dict | None = None,
) -> None:
    db.add(
        ActivityEvent(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            event_data=data or {},
        )
    )
