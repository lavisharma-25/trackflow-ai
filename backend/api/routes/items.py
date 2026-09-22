from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.database import get_db
from domain.items.schemas import ItemCreate, ItemRead, ItemUpdate
from domain.items.service import (
    archive_item,
    create_item,
    get_item,
    list_items,
    restore_item,
    update_item,
)


router = APIRouter()


@router.post("", response_model=ItemRead, status_code=201)
def create_item_route(
    collection_id: str,
    request: ItemCreate,
    db: Session = Depends(get_db),
):
    return create_item(db, collection_id, request)


@router.get("", response_model=list[ItemRead])
def list_items_route(
    collection_id: str,
    search: str | None = None,
    include_archived: bool = False,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list_items(db, collection_id, search, include_archived, limit)


@router.get("/{item_id}", response_model=ItemRead)
def get_item_route(
    collection_id: str,
    item_id: str,
    include_archived: bool = False,
    db: Session = Depends(get_db),
):
    return get_item(db, collection_id, item_id, include_archived)


@router.patch("/{item_id}", response_model=ItemRead)
def update_item_route(
    collection_id: str,
    item_id: str,
    request: ItemUpdate,
    db: Session = Depends(get_db),
):
    return update_item(db, collection_id, item_id, request)


@router.delete("/{item_id}", response_model=ItemRead)
def archive_item_route(
    collection_id: str,
    item_id: str,
    confirmed: bool = Query(False, description="Must be true to archive"),
    db: Session = Depends(get_db),
):
    return archive_item(db, collection_id, item_id, confirmed)


@router.post("/{item_id}/restore", response_model=ItemRead)
def restore_item_route(
    collection_id: str,
    item_id: str,
    db: Session = Depends(get_db),
):
    return restore_item(db, collection_id, item_id)
