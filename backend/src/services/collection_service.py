from datetime import date, datetime, timezone
from typing import Any

from pydantic import AnyUrl, TypeAdapter, ValidationError
from sqlalchemy import String, cast, or_, select
from sqlalchemy.orm import Session

from src.db.models import ActivityEvent, Collection, Item
from src.schemas.collection import CollectionCreate, CollectionUpdate, FieldDefinition
from src.schemas.item import ItemCreate, ItemUpdate
from src.services.exceptions import ConflictError, DomainValidationError, NotFoundError


def _name_key(name: str) -> str:
    return " ".join(name.strip().casefold().split())


def _event(db: Session, action: str, entity_type: str, entity_id: str, data: dict | None = None):
    db.add(
        ActivityEvent(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            event_data=data or {},
        )
    )


def get_collection(db: Session, collection_id: str, include_archived: bool = False) -> Collection:
    collection = db.get(Collection, collection_id)
    if collection is None or (collection.archived_at is not None and not include_archived):
        raise NotFoundError("Collection not found")
    return collection


def get_collection_by_name(db: Session, name: str) -> Collection:
    collection = db.scalar(
        select(Collection).where(
            Collection.name_key == _name_key(name), Collection.archived_at.is_(None)
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
    _event(db, "collection.created", "collection", collection.id, {"name": collection.name})
    db.commit()
    db.refresh(collection)
    return collection


def list_collections(db: Session, include_archived: bool = False) -> list[Collection]:
    query = select(Collection).order_by(Collection.name)
    if not include_archived:
        query = query.where(Collection.archived_at.is_(None))
    return list(db.scalars(query))


def update_collection(db: Session, collection_id: str, request: CollectionUpdate) -> Collection:
    collection = get_collection(db, collection_id)
    changes = request.model_dump(exclude_unset=True)

    if "name" in changes:
        key = _name_key(changes["name"])
        duplicate = db.scalar(
            select(Collection).where(Collection.name_key == key, Collection.id != collection.id)
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

    _event(db, "collection.updated", "collection", collection.id, {"changed": list(changes)})
    db.commit()
    db.refresh(collection)
    return collection


def archive_collection(db: Session, collection_id: str, confirmed: bool) -> Collection:
    if not confirmed:
        raise DomainValidationError("Archiving requires confirmed=true")
    collection = get_collection(db, collection_id)
    collection.archived_at = datetime.now(timezone.utc)
    _event(db, "collection.archived", "collection", collection.id)
    db.commit()
    db.refresh(collection)
    return collection


def restore_collection(db: Session, collection_id: str) -> Collection:
    collection = get_collection(db, collection_id, include_archived=True)
    collection.archived_at = None
    _event(db, "collection.restored", "collection", collection.id)
    db.commit()
    db.refresh(collection)
    return collection


def _validate_value(field: FieldDefinition, value: Any) -> None:
    if value is None:
        if field.required:
            raise DomainValidationError(f"Property '{field.key}' is required")
        return

    valid = True
    if field.type == "string":
        valid = isinstance(value, str)
    elif field.type == "integer":
        valid = isinstance(value, int) and not isinstance(value, bool)
    elif field.type == "number":
        valid = isinstance(value, (int, float)) and not isinstance(value, bool)
    elif field.type == "boolean":
        valid = isinstance(value, bool)
    elif field.type == "date":
        try:
            date.fromisoformat(value)
        except (TypeError, ValueError):
            valid = False
    elif field.type == "datetime":
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, TypeError, ValueError):
            valid = False
    elif field.type == "url":
        try:
            TypeAdapter(AnyUrl).validate_python(value)
        except ValidationError:
            valid = False
    elif field.type == "select":
        valid = isinstance(value, str) and value in field.options
    elif field.type == "multi_select":
        valid = (
            isinstance(value, list)
            and all(isinstance(option, str) and option in field.options for option in value)
        )

    if not valid:
        raise DomainValidationError(f"Property '{field.key}' must be of type {field.type}")


def validate_properties(properties: dict[str, Any], definitions: list[dict]) -> None:
    fields = [FieldDefinition.model_validate(definition) for definition in definitions]
    field_map = {field.key: field for field in fields}
    unknown = sorted(set(properties) - set(field_map))
    if unknown:
        raise DomainValidationError(f"Unknown properties: {', '.join(unknown)}")

    for field in fields:
        value = properties.get(field.key)
        if field.required and (field.key not in properties or value in (None, "", [])):
            raise DomainValidationError(f"Property '{field.key}' is required")
        if field.key in properties:
            _validate_value(field, value)


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
    _event(db, "item.created", "item", item.id, {"collection_id": collection.id})
    db.commit()
    db.refresh(item)
    return item


def get_item(db: Session, collection_id: str, item_id: str, include_archived: bool = False) -> Item:
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


def update_item(db: Session, collection_id: str, item_id: str, request: ItemUpdate) -> Item:
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

    _event(db, "item.updated", "item", item.id, {"changed": list(changes)})
    db.commit()
    db.refresh(item)
    return item


def archive_item(db: Session, collection_id: str, item_id: str, confirmed: bool) -> Item:
    if not confirmed:
        raise DomainValidationError("Archiving requires confirmed=true")
    item = get_item(db, collection_id, item_id)
    item.archived_at = datetime.now(timezone.utc)
    _event(db, "item.archived", "item", item.id)
    db.commit()
    db.refresh(item)
    return item


def restore_item(db: Session, collection_id: str, item_id: str) -> Item:
    item = get_item(db, collection_id, item_id, include_archived=True)
    item.archived_at = None
    _event(db, "item.restored", "item", item.id)
    db.commit()
    db.refresh(item)
    return item
