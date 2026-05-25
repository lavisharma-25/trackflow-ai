from fastapi import APIRouter

router = APIRouter()

@router.get("/health-check")
async def root():
    return {"message": "TrackFlow AI is running"}