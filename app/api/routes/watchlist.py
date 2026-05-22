from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_watchlist_service
from app.schemas.action import WatchlistCreate, WatchlistEntry, WatchlistUpdate
from app.services.watchlist.service import (
    DuplicateWatchlistEntry,
    WatchlistNotFound,
    WatchlistService,
)

router = APIRouter()


@router.get("/watchlist", response_model=list[WatchlistEntry])
async def list_watchlist(service: WatchlistService = Depends(get_watchlist_service)):
    return service.list_entries()


@router.post("/watchlist", response_model=WatchlistEntry, status_code=status.HTTP_201_CREATED)
async def create_watchlist_entry(
    payload: WatchlistCreate,
    service: WatchlistService = Depends(get_watchlist_service),
):
    try:
        return service.create_entry(payload)
    except DuplicateWatchlistEntry as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/watchlist/{entry_id}", response_model=WatchlistEntry)
async def get_watchlist_entry(
    entry_id: str,
    service: WatchlistService = Depends(get_watchlist_service),
):
    try:
        return service.get_entry(entry_id)
    except WatchlistNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/watchlist/{entry_id}", response_model=WatchlistEntry)
async def update_watchlist_entry(
    entry_id: str,
    payload: WatchlistUpdate,
    service: WatchlistService = Depends(get_watchlist_service),
):
    try:
        return service.update_entry(entry_id, payload)
    except WatchlistNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/watchlist/{entry_id}", response_model=WatchlistEntry)
async def delete_watchlist_entry(
    entry_id: str,
    service: WatchlistService = Depends(get_watchlist_service),
):
    try:
        return service.delete_entry(entry_id)
    except WatchlistNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
