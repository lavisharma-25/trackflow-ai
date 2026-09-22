from fastapi import APIRouter

from api.routes import activity, assistant, collections, items


router = APIRouter(prefix="/api/v1")
router.include_router(collections.router, prefix="/collections", tags=["collections"])
router.include_router(
    items.router,
    prefix="/collections/{collection_id}/items",
    tags=["items"],
)
router.include_router(activity.router, prefix="/activity", tags=["activity"])
router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
