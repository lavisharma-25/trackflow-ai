from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.assistant import router as assistant_router
from app.api.routes.health import router as health_router
from app.api.routes.trackers import router as trackers_router
from app.api.routes.watchlist import router as watchlist_router
from app.config import APP_NAME, APP_VERSION


app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1", tags=["Health Check"])
app.include_router(trackers_router, prefix="/api/v1", tags=["Trackers"])
app.include_router(assistant_router, prefix="/api/v1", tags=["Assistant"])
app.include_router(watchlist_router, prefix="/api/v1", tags=["Watchlist"])


from fastapi import FastAPI
from app.api.routes.assistant import router

app = FastAPI(title="TrackFlow AI")

app.include_router(router)
