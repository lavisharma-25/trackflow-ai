import re
from datetime import UTC, datetime
from uuid import uuid4

from app.schemas.action import WatchlistCreate, WatchlistEntry, WatchlistUpdate
from app.storage.json_store import JsonStore


class WatchlistError(ValueError):
    pass


class DuplicateWatchlistEntry(WatchlistError):
    pass


class WatchlistNotFound(WatchlistError):
    pass


class WatchlistService:
    def __init__(self, store: JsonStore | None = None):
        self.store = store or JsonStore()

    def list_entries(self) -> list[WatchlistEntry]:
        return [WatchlistEntry(**item) for item in self.store.get_collection("watchlist")]

    def create_entry(self, payload: WatchlistCreate) -> WatchlistEntry:
        entries = self.list_entries()
        duplicate = self.find_duplicate(payload, entries)
        if duplicate:
            raise DuplicateWatchlistEntry(f"{duplicate.title} already exists in the watchlist.")
        now = self._now()
        entry = WatchlistEntry(
            id=str(uuid4()),
            created_at=now,
            updated_at=now,
            **payload.model_dump(),
        )
        entries.append(entry)
        self._save_entries(entries)
        return entry

    def get_entry(self, entry_id: str) -> WatchlistEntry:
        for entry in self.list_entries():
            if entry.id == entry_id:
                return entry
        raise WatchlistNotFound("Watchlist entry was not found.")

    def find_by_title(self, title: str) -> WatchlistEntry:
        normalized = self._normalize(title)
        for entry in self.list_entries():
            if self._normalize(entry.title) == normalized:
                return entry
        raise WatchlistNotFound("Watchlist entry was not found.")

    def update_entry(self, entry_id: str, payload: WatchlistUpdate) -> WatchlistEntry:
        entries = self.list_entries()
        for index, entry in enumerate(entries):
            if entry.id != entry_id:
                continue
            update_data = payload.model_dump(exclude_unset=True)
            updated = entry.model_copy(update={**update_data, "updated_at": self._now()})
            entries[index] = updated
            self._save_entries(entries)
            return updated
        raise WatchlistNotFound("Watchlist entry was not found.")

    def delete_entry(self, entry_id: str) -> WatchlistEntry:
        entries = self.list_entries()
        for index, entry in enumerate(entries):
            if entry.id == entry_id:
                removed = entries.pop(index)
                self._save_entries(entries)
                return removed
        raise WatchlistNotFound("Watchlist entry was not found.")

    def find_duplicate(
        self,
        payload: WatchlistCreate,
        entries: list[WatchlistEntry] | None = None,
    ) -> WatchlistEntry | None:
        entries = entries or self.list_entries()
        for entry in entries:
            if payload.tmdb_id and entry.tmdb_id == payload.tmdb_id:
                return entry
            same_title = self._normalize(entry.title) == self._normalize(payload.title)
            if same_title and entry.media_type == payload.media_type:
                return entry
        return None

    def _save_entries(self, entries: list[WatchlistEntry]) -> None:
        self.store.replace_collection("watchlist", [entry.model_dump() for entry in entries])

    def _normalize(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.lower())

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()
