from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ai.agent import LLMConfigurationError
from api.router import router as api_router
from core.exceptions import (
    ConflictError,
    DomainValidationError,
    NotFoundError,
)
from core.settings import settings
from db.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
async def not_found_handler(_: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
async def conflict_handler(_: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(DomainValidationError)
async def validation_handler(_: Request, exc: DomainValidationError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(LLMConfigurationError)
async def llm_configuration_handler(_: Request, exc: LLMConfigurationError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=False)
