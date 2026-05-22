import pytest
import anyio
import httpx

from app.api import dependencies
from app.main import app
from app.schemas.action import TMDBChoice, WatchlistCreate
from app.services.ai.parser import RuleBasedIntentParser
from app.services.watchlist.service import WatchlistService
from app.storage.json_store import JsonStore
from app.workflows.watchlist import WatchlistWorkflow


class ASGITestClient:
    def __init__(self, asgi_app):
        self.app = asgi_app

    def get(self, url: str):
        return self.request("GET", url)

    def post(self, url: str, json: dict | None = None):
        return self.request("POST", url, json=json)

    def patch(self, url: str, json: dict | None = None):
        return self.request("PATCH", url, json=json)

    def delete(self, url: str):
        return self.request("DELETE", url)

    def request(self, method: str, url: str, json: dict | None = None):
        async def send():
            transport = httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.request(method, url, json=json)

        return anyio.run(send)


class FakeTMDBClient:
    def __init__(self):
        self.results = {
            "interstellar": [
                TMDBChoice(
                    tmdb_id=157336,
                    title="Interstellar",
                    media_type="movie",
                    release_date="2014-11-07",
                    overview="A team travels through a wormhole.",
                    poster_path="/interstellar.jpg",
                )
            ],
            "avatar": [
                TMDBChoice(
                    tmdb_id=19995,
                    title="Avatar",
                    media_type="movie",
                    release_date="2009-12-18",
                    overview="Pandora.",
                    poster_path="/avatar.jpg",
                ),
                TMDBChoice(
                    tmdb_id=37854,
                    title="Avatar: The Last Airbender",
                    media_type="tv",
                    release_date="2005-02-21",
                    overview="Elemental adventure.",
                    poster_path="/airbender.jpg",
                ),
            ],
        }

    def search(self, query: str, media_type: str | None = None):
        return self.results.get(query.lower(), [])

    def details_from_choice(self, choice: TMDBChoice):
        return WatchlistCreate(
            title=choice.title,
            media_type=choice.media_type,
            tmdb_id=choice.tmdb_id,
            genres=["Sci-Fi"],
            release_date=choice.release_date,
            overview=choice.overview,
            poster_path=choice.poster_path,
        )


@pytest.fixture()
def client(tmp_path):
    store = JsonStore(tmp_path / "data.json")
    tmdb = FakeTMDBClient()

    def workflow_override():
        return WatchlistWorkflow(
            store=store,
            parser=RuleBasedIntentParser(),
            tmdb_client=tmdb,
            watchlist_service=WatchlistService(store),
        )

    def service_override():
        return WatchlistService(store)

    app.dependency_overrides[dependencies.get_watchlist_workflow] = workflow_override
    app.dependency_overrides[dependencies.get_watchlist_service] = service_override
    yield ASGITestClient(app)
    app.dependency_overrides.clear()


def test_health_and_trackers(client):
    health = client.get("/api/v1/health-check")
    assert health.status_code == 200
    assert health.json() == {"message": "API is working fine!"}

    trackers = client.get("/api/v1/trackers")
    assert trackers.status_code == 200
    assert trackers.json()["trackers"][0]["key"] == "watchlist"
    assert any(tracker["key"] == "games" and not tracker["implemented"] for tracker in trackers.json()["trackers"])


def test_non_watchlist_tracker_is_safely_rejected(client):
    response = client.post(
        "/api/v1/assistant/message",
        json={"conversation_id": "c1", "tracker": "games", "message": "Add Elden Ring"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "not_implemented"
    assert client.get("/api/v1/watchlist").json() == []


def test_watchlist_rest_crud_and_duplicate(client):
    create = client.post(
        "/api/v1/watchlist",
        json={"title": "Arrival", "media_type": "movie", "tmdb_id": 329865, "status": "planned"},
    )
    assert create.status_code == 201
    entry = create.json()

    duplicate = client.post(
        "/api/v1/watchlist",
        json={"title": "Arrival", "media_type": "movie", "tmdb_id": 329865, "status": "planned"},
    )
    assert duplicate.status_code == 409

    listed = client.get("/api/v1/watchlist")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/api/v1/watchlist/{entry['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Arrival"

    updated = client.patch(f"/api/v1/watchlist/{entry['id']}", json={"status": "watched", "rating": 9})
    assert updated.status_code == 200
    assert updated.json()["status"] == "watched"

    deleted = client.delete(f"/api/v1/watchlist/{entry['id']}")
    assert deleted.status_code == 200
    assert client.get("/api/v1/watchlist").json() == []


def test_assistant_create_list_update_delete_and_duplicate(client):
    created = client.post(
        "/api/v1/assistant/message",
        json={"conversation_id": "c2", "tracker": "watchlist", "message": "Add Interstellar"},
    )
    assert created.status_code == 200
    assert created.json()["status"] == "saved"

    duplicate = client.post(
        "/api/v1/assistant/message",
        json={"conversation_id": "c2", "tracker": "watchlist", "message": "Add Interstellar"},
    )
    assert duplicate.json()["status"] == "duplicate"

    listed = client.post(
        "/api/v1/assistant/message",
        json={"conversation_id": "c2", "tracker": "watchlist", "message": "list watchlist"},
    )
    assert listed.json()["status"] == "ok"
    assert len(listed.json()["data"]) == 1

    updated = client.post(
        "/api/v1/assistant/message",
        json={"conversation_id": "c2", "tracker": "watchlist", "message": "mark Interstellar watched"},
    )
    assert updated.json()["status"] == "updated"
    assert updated.json()["data"]["status"] == "watched"

    deleted = client.post(
        "/api/v1/assistant/message",
        json={"conversation_id": "c2", "tracker": "watchlist", "message": "delete Interstellar"},
    )
    assert deleted.json()["status"] == "deleted"
    assert client.get("/api/v1/watchlist").json() == []


def test_assistant_ambiguity_and_pending_selection(client):
    ambiguous = client.post(
        "/api/v1/assistant/message",
        json={"conversation_id": "c3", "tracker": "watchlist", "message": "Add Avatar"},
    )
    assert ambiguous.status_code == 200
    assert ambiguous.json()["status"] == "needs_selection"
    assert len(ambiguous.json()["choices"]) == 2

    selected = client.post(
        "/api/v1/assistant/message",
        json={"conversation_id": "c3", "tracker": "watchlist", "message": "2"},
    )
    assert selected.json()["status"] == "saved"
    assert selected.json()["data"]["title"] == "Avatar: The Last Airbender"
    assert len(client.get("/api/v1/watchlist").json()) == 1
