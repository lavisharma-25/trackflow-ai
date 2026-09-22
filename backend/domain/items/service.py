from datetime import datetime, timezone

from sqlalchemy import String, cast, or_, select
from sqlalchemy.orm import Session

from core.exceptions import DomainValidationError, NotFoundError
from db.models import Item
from domain.activity import record_event
from domain.collections.service import get_collection
from domain.items.schemas import ItemCreate, ItemUpdate
from domain.items.validation import validate_properties


def create_item(db: Session, collection_id: str, request: ItemCreate) -> Item:
    collection = get_collection(db, collection_id)
    validate_properties(request.properties, collection.field_definitions)
    item = Item(
        collection_id=collection.id,
        title=request.title,
        body=request.body,
        properties=request.properties,
    )
    db.add(item)
    db.flush()
    record_event(
        db,
        "item.created",
        "item",
        item.id,
        {"collection_id": collection.id},
    )
    db.commit()
    db.refresh(item)
    return item


def get_item(
    db: Session,
    collection_id: str,
    item_id: str,
    include_archived: bool = False,
) -> Item:
    get_collection(db, collection_id, include_archived=include_archived)
    item = db.get(Item, item_id)
    if (
        item is None
        or item.collection_id != collection_id
        or (item.archived_at is not None and not include_archived)
    ):
        raise NotFoundError("Item not found")
    return item


def list_items(
    db: Session,
    collection_id: str,
    search: str | None = None,
    include_archived: bool = False,
    limit: int = 100,
) -> list[Item]:
    get_collection(db, collection_id, include_archived=include_archived)
    query = select(Item).where(Item.collection_id == collection_id)
    if not include_archived:
        query = query.where(Item.archived_at.is_(None))
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(
            or_(
                Item.title.ilike(pattern),
                Item.body.ilike(pattern),
                cast(Item.properties, String).ilike(pattern),
            )
        )
    query = query.order_by(Item.updated_at.desc()).limit(limit)
    return list(db.scalars(query))


def update_item(
    db: Session,
    collection_id: str,
    item_id: str,
    request: ItemUpdate,
) -> Item:
    collection = get_collection(db, collection_id)
    item = get_item(db, collection_id, item_id)
    changes = request.model_dump(exclude_unset=True)

    if "properties" in changes:
        merged = {**item.properties, **(request.properties or {})}
        validate_properties(merged, collection.field_definitions)
        item.properties = merged
    if "title" in changes:
        item.title = changes["title"]
    if "body" in changes:
        item.body = changes["body"]

    record_event(
        db,
        "item.updated",
        "item",
        item.id,
        {"changed": list(changes)},
    )
    db.commit()
    db.refresh(item)
    return item


def archive_item(
    db: Session, collection_id: str, item_id: str, confirmed: bool
) -> Item:
    if not confirmed:
        raise DomainValidationError("Archiving requires confirmed=true")
    item = get_item(db, collection_id, item_id)
    item.archived_at = datetime.now(timezone.utc)
    record_event(db, "item.archived", "item", item.id)
    db.commit()
    db.refresh(item)
    return item


def restore_item(db: Session, collection_id: str, item_id: str) -> Item:
    item = get_item(db, collection_id, item_id, include_archived=True)
    item.archived_at = None
    record_event(db, "item.restored", "item", item.id)
    db.commit()
    db.refresh(item)
    return item
