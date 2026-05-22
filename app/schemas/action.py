from typing import Any, Literal

from pydantic import BaseModel, Field

MediaType = Literal["movie", "tv"]
WatchlistStatus = Literal["planned", "watching", "watched", "dropped"]
AssistantIntent = Literal["create", "list", "get", "update", "delete", "unknown"]


class ParsedAction(BaseModel):
    intent: AssistantIntent = "unknown"
    entity: str | None = None
    media_type: MediaType | None = None
    status: WatchlistStatus | None = None
    notes: str | None = None
    rating: float | None = Field(default=None, ge=0, le=10)
    target_id: str | None = None
    release_year: int | None = None


class AssistantMessageRequest(BaseModel):
    conversation_id: str = Field(min_length=1)
    tracker: str = Field(min_length=1)
    message: str = Field(min_length=1)


class AssistantMessageResponse(BaseModel):
    status: str
    message: str
    data: dict[str, Any] | list[dict[str, Any]] | None = None
    choices: list[dict[str, Any]] | None = None


class WatchlistBase(BaseModel):
    title: str | None = None
    media_type: MediaType | None = None
    tmdb_id: int | None = None
    genres: list[str] = Field(default_factory=list)
    release_date: str | None = None
    overview: str | None = None
    poster_path: str | None = None
    status: WatchlistStatus = "planned"
    notes: str | None = None
    rating: float | None = Field(default=None, ge=0, le=10)


class WatchlistCreate(WatchlistBase):
    title: str
    media_type: MediaType = "movie"


class WatchlistUpdate(BaseModel):
    title: str | None = None
    media_type: MediaType | None = None
    tmdb_id: int | None = None
    genres: list[str] | None = None
    release_date: str | None = None
    overview: str | None = None
    poster_path: str | None = None
    status: WatchlistStatus | None = None
    notes: str | None = None
    rating: float | None = Field(default=None, ge=0, le=10)


class WatchlistEntry(WatchlistCreate):
    id: str
    created_at: str
    updated_at: str


class TMDBChoice(BaseModel):
    tmdb_id: int
    title: str
    media_type: MediaType
    release_date: str | None = None
    overview: str | None = None
    poster_path: str | None = None
