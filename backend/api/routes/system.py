from fastapi import APIRouter
from core.settings import settings

router = APIRouter()

@router.get("/health", status_code=200)
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "environment": settings.APP_ENV}