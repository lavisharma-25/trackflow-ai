def create_expenses_collection(client):
    response = client.post(
        "/api/v1/collections",
        json={
            "name": "Expenses",
            "description": "Personal spending",
            "fields": [
                {"key": "amount", "label": "Amount", "type": "number", "required": True},
                {
                    "key": "category",
                    "label": "Category",
                    "type": "select",
                    "options": ["food", "travel"],
                },
                {"key": "spent_on", "label": "Date", "type": "date"},
            ],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_health_and_frontend_cors(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    preflight = client.options(
        "/api/v1/collections",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_collection_and_item_lifecycle(client):
    collection = create_expenses_collection(client)

    invalid = client.post(
        f"/api/v1/collections/{collection['id']}/items",
        json={"title": "Coffee", "properties": {"category": "food"}},
    )
    assert invalid.status_code == 422
    assert "amount" in invalid.json()["detail"]

    created = client.post(
        f"/api/v1/collections/{collection['id']}/items",
        json={
            "title": "Coffee",
            "body": "Coffee with a friend",
            "properties": {"amount": 180.5, "category": "food", "spent_on": "2026-09-21"},
        },
    )
    assert created.status_code == 201, created.text
    item = created.json()

    search = client.get(
        f"/api/v1/collections/{collection['id']}/items", params={"search": "friend"}
    )
    assert search.status_code == 200
    assert [result["id"] for result in search.json()] == [item["id"]]

    not_confirmed = client.delete(
        f"/api/v1/collections/{collection['id']}/items/{item['id']}"
    )
    assert not_confirmed.status_code == 422

    archived = client.delete(
        f"/api/v1/collections/{collection['id']}/items/{item['id']}",
        params={"confirmed": True},
    )
    assert archived.status_code == 200
    assert archived.json()["archived_at"] is not None

    restored = client.post(
        f"/api/v1/collections/{collection['id']}/items/{item['id']}/restore"
    )
    assert restored.status_code == 200
    assert restored.json()["archived_at"] is None


def test_duplicate_collection_names_are_rejected(client):
    create_expenses_collection(client)
    duplicate = client.post(
        "/api/v1/collections",
        json={"name": "  expenses  ", "fields": []},
    )
    assert duplicate.status_code == 409


def test_incompatible_schema_change_is_rejected(client):
    collection = create_expenses_collection(client)
    client.post(
        f"/api/v1/collections/{collection['id']}/items",
        json={"title": "Train", "properties": {"amount": 500, "category": "travel"}},
    )

    response = client.patch(
        f"/api/v1/collections/{collection['id']}",
        json={"fields": [{"key": "category", "label": "Category", "type": "string"}]},
    )
    assert response.status_code == 422
    assert "Unknown properties" in response.json()["detail"]


def test_activity_log_records_writes(client):
    collection = create_expenses_collection(client)
    response = client.get("/api/v1/activity")
    assert response.status_code == 200
    assert response.json()[0]["action"] == "collection.created"
    assert response.json()[0]["entity_id"] == collection["id"]
