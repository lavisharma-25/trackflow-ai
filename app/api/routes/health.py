from fastapi import APIRouter

router = APIRouter()

@router.get("/health-check")
async def root():
    return {"message": "API is working fine!"}