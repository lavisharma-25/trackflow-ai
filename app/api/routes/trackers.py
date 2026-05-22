from fastapi import APIRouter

from app.core.trackers import SUPPORTED_TRACKERS

router = APIRouter()


@router.get("/trackers")
async def list_trackers():
    return {"trackers": SUPPORTED_TRACKERS}
