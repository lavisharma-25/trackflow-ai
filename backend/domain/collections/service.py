from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.exceptions import ConflictError, DomainValidationError, NotFoundError
from db.models import Collection
from domain.activity import record_event
from domain.collections.schemas import CollectionCreate, CollectionUpdate
from domain.items.validation import validate_properties


def _name_key(name: str) -> str:
    return " ".join(name.strip().casefold().split())


def get_collection(
    db: Session, collection_id: str, include_archived: bool = False
) -> Collection:
    collection = db.get(Collection, collection_id)
    if collection is None or (
        collection.archived_at is not None and not include_archived
    ):
        raise NotFoundError("Collection not found")
    return collection


def get_collection_by_name(db: Session, name: str) -> Collection:
    collection = db.scalar(
        select(Collection).where(
            Collection.name_key == _name_key(name),
            Collection.archived_at.is_(None),
        )
    )
    if collection is None:
        raise NotFoundError(f"Collection '{name}' not found")
    return collection


def create_collection(db: Session, request: CollectionCreate) -> Collection:
    key = _name_key(request.name)
    if db.scalar(select(Collection).where(Collection.name_key == key)):
        raise ConflictError(f"A collection named '{request.name}' already exists")

    collection = Collection(
        name=request.name,
        name_key=key,
        description=request.description,
        field_definitions=[field.model_dump(mode="json") for field in request.fields],
    )
    db.add(collection)
    db.flush()
    record_event(
        db,
        "collection.created",
        "collection",
        collection.id,
        {"name": collection.name},
    )
    db.commit()
    db.refresh(collection)
    return collection


def list_collections(db: Session, include_archived: bool = False) -> list[Collection]:
    query = select(Collection).order_by(Collection.name)
    if not include_archived:
        query = query.where(Collection.archived_at.is_(None))
    return list(db.scalars(query))


def update_collection(
    db: Session, collection_id: str, request: CollectionUpdate
) -> Collection:
    collection = get_collection(db, collection_id)
    changes = request.model_dump(exclude_unset=True)

    if "name" in changes:
        key = _name_key(changes["name"])
        duplicate = db.scalar(
            select(Collection).where(
                Collection.name_key == key,
                Collection.id != collection.id,
            )
        )
        if duplicate:
            raise ConflictError(f"A collection named '{changes['name']}' already exists")
        collection.name = changes["name"]
        collection.name_key = key

    if "description" in changes:
        collection.description = changes["description"]

    if "fields" in changes:
        fields = request.fields or []
        definitions = [field.model_dump(mode="json") for field in fields]
        for item in collection.items:
            if item.archived_at is None:
                validate_properties(item.properties, definitions)
        collection.field_definitions = definitions

    record_event(
        db,
        "collection.updated",
        "collection",
        collection.id,
        {"changed": list(changes)},
    )
    db.commit()
    db.refresh(collection)
    return collection


def archive_collection(
    db: Session, collection_id: str, confirmed: bool
) -> Collection:
    if not confirmed:
        raise DomainValidationError("Archiving requires confirmed=true")
    collection = get_collection(db, collection_id)
    collection.archived_at = datetime.now(timezone.utc)
    record_event(db, "collection.archived", "collection", collection.id)
    db.commit()
    db.refresh(collection)
    return collection


def restore_collection(db: Session, collection_id: str) -> Collection:
    collection = get_collection(db, collection_id, include_archived=True)
    collection.archived_at = None
    record_event(db, "collection.restored", "collection", collection.id)
    db.commit()
    db.refresh(collection)
    return collection
