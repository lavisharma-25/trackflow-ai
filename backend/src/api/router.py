from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import ActivityEvent
from src.schemas.collection import CollectionCreate, CollectionRead, CollectionUpdate
from src.schemas.item import ItemCreate, ItemRead, ItemUpdate
from src.services.collection_service import (
    archive_collection,
    archive_item,
    create_collection,
    create_item,
    get_collection,
    get_item,
    list_collections,
    list_items,
    restore_collection,
    restore_item,
    update_collection,
    update_item,
)


router = APIRouter(prefix="/api/v1")


@router.post("/collections", response_model=CollectionRead, status_code=201)
def create_collection_route(request: CollectionCreate, db: Session = Depends(get_db)):
    return create_collection(db, request)


@router.get("/collections", response_model=list[CollectionRead])
def list_collections_route(
    include_archived: bool = False, db: Session = Depends(get_db)
):
    return list_collections(db, include_archived)


@router.get("/collections/{collection_id}", response_model=CollectionRead)
def get_collection_route(
    collection_id: str,
    include_archived: bool = False,
    db: Session = Depends(get_db),
):
    return get_collection(db, collection_id, include_archived)


@router.patch("/collections/{collection_id}", response_model=CollectionRead)
def update_collection_route(
    collection_id: str,
    request: CollectionUpdate,
    db: Session = Depends(get_db),
):
    return update_collection(db, collection_id, request)


@router.delete("/collections/{collection_id}", response_model=CollectionRead)
def archive_collection_route(
    collection_id: str,
    confirmed: bool = Query(False, description="Must be true to archive"),
    db: Session = Depends(get_db),
):
    return archive_collection(db, collection_id, confirmed)


@router.post("/collections/{collection_id}/restore", response_model=CollectionRead)
def restore_collection_route(collection_id: str, db: Session = Depends(get_db)):
    return restore_collection(db, collection_id)


@router.post("/collections/{collection_id}/items", response_model=ItemRead, status_code=201)
def create_item_route(
    collection_id: str,
    request: ItemCreate,
    db: Session = Depends(get_db),
):
    return create_item(db, collection_id, request)


@router.get("/collections/{collection_id}/items", response_model=list[ItemRead])
def list_items_route(
    collection_id: str,
    search: str | None = None,
    include_archived: bool = False,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list_items(db, collection_id, search, include_archived, limit)


@router.get("/collections/{collection_id}/items/{item_id}", response_model=ItemRead)
def get_item_route(
    collection_id: str,
    item_id: str,
    include_archived: bool = False,
    db: Session = Depends(get_db),
):
    return get_item(db, collection_id, item_id, include_archived)


@router.patch("/collections/{collection_id}/items/{item_id}", response_model=ItemRead)
def update_item_route(
    collection_id: str,
    item_id: str,
    request: ItemUpdate,
    db: Session = Depends(get_db),
):
    return update_item(db, collection_id, item_id, request)


@router.delete("/collections/{collection_id}/items/{item_id}", response_model=ItemRead)
def archive_item_route(
    collection_id: str,
    item_id: str,
    confirmed: bool = Query(False, description="Must be true to archive"),
    db: Session = Depends(get_db),
):
    return archive_item(db, collection_id, item_id, confirmed)


@router.post("/collections/{collection_id}/items/{item_id}/restore", response_model=ItemRead)
def restore_item_route(
    collection_id: str,
    item_id: str,
    db: Session = Depends(get_db),
):
    return restore_item(db, collection_id, item_id)


@router.get("/activity")
def list_activity_route(
    limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)
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
