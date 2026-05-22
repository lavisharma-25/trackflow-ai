from typing import Any

import httpx

from app.config import TMDB_API_KEY, TMDB_BASE_URL
from app.schemas.action import TMDBChoice, WatchlistCreate


class TMDBClientError(RuntimeError):
    pass


class TMDBClient:
    def __init__(self, api_key: str | None = None, base_url: str = TMDB_BASE_URL):
        self.api_key = api_key or TMDB_API_KEY
        self.base_url = base_url.rstrip("/")

    def search(self, query: str, media_type: str | None = None) -> list[TMDBChoice]:
        if not self.api_key:
            raise TMDBClientError("TMDB_API_KEY is not configured.")
        endpoint = media_type if media_type in {"movie", "tv"} else "multi"
        data = self._get(f"/search/{endpoint}", {"query": query, "include_adult": "false"})
        choices: list[TMDBChoice] = []
        for item in data.get("results", []):
            mapped = self._map_search_result(item)
            if mapped:
                choices.append(mapped)
        return choices[:5]

    def details_from_choice(self, choice: TMDBChoice) -> WatchlistCreate:
        if not self.api_key:
            return WatchlistCreate(**choice.model_dump(), genres=[])
        data = self._get(f"/{choice.media_type}/{choice.tmdb_id}", {})
        genres = [genre["name"] for genre in data.get("genres", []) if "name" in genre]
        return WatchlistCreate(
            title=data.get("title") or data.get("name") or choice.title,
            media_type=choice.media_type,
            tmdb_id=choice.tmdb_id,
            genres=genres,
            release_date=data.get("release_date") or data.get("first_air_date") or choice.release_date,
            overview=data.get("overview") or choice.overview,
            poster_path=data.get("poster_path") or choice.poster_path,
        )

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        request_params = {"api_key": self.api_key, **params}
        try:
            response = httpx.get(f"{self.base_url}{path}", params=request_params, timeout=10)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise TMDBClientError(f"TMDB request failed: {exc}") from exc
        return response.json()

    def _map_search_result(self, item: dict[str, Any]) -> TMDBChoice | None:
        media_type = item.get("media_type")
        if media_type not in {"movie", "tv"}:
            if "title" in item:
                media_type = "movie"
            elif "name" in item:
                media_type = "tv"
            else:
                return None
        title = item.get("title") or item.get("name")
        tmdb_id = item.get("id")
        if not title or not tmdb_id:
            return None
        return TMDBChoice(
            tmdb_id=tmdb_id,
            title=title,
            media_type=media_type,
            release_date=item.get("release_date") or item.get("first_air_date"),
            overview=item.get("overview"),
            poster_path=item.get("poster_path"),
        )
