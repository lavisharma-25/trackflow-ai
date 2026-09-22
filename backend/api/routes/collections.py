from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.database import get_db
from domain.collections.schemas import CollectionCreate, CollectionRead, CollectionUpdate
from domain.collections.service import (
    archive_collection,
    create_collection,
    get_collection,
    list_collections,
    restore_collection,
    update_collection,
)


router = APIRouter()


@router.post("", response_model=CollectionRead, status_code=201)
def create_collection_route(
    request: CollectionCreate,
    db: Session = Depends(get_db),
):
    return create_collection(db, request)


@router.get("", response_model=list[CollectionRead])
def list_collections_route(
    include_archived: bool = False,
    db: Session = Depends(get_db),
):
    return list_collections(db, include_archived)


@router.get("/{collection_id}", response_model=CollectionRead)
def get_collection_route(
    collection_id: str,
    include_archived: bool = False,
    db: Session = Depends(get_db),
):
    return get_collection(db, collection_id, include_archived)


@router.patch("/{collection_id}", response_model=CollectionRead)
def update_collection_route(
    collection_id: str,
    request: CollectionUpdate,
    db: Session = Depends(get_db),
):
    return update_collection(db, collection_id, request)


@router.delete("/{collection_id}", response_model=CollectionRead)
def archive_collection_route(
    collection_id: str,
    confirmed: bool = Query(False, description="Must be true to archive"),
    db: Session = Depends(get_db),
):
    return archive_collection(db, collection_id, confirmed)


@router.post("/{collection_id}/restore", response_model=CollectionRead)
def restore_collection_route(
    collection_id: str,
    db: Session = Depends(get_db),
):
    return restore_collection(db, collection_id)
