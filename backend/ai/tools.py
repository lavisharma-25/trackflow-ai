from typing import Any

from langchain_core.tools import tool

from db.database import SessionLocal
from domain.collections.schemas import CollectionCreate
from domain.collections.service import (
    create_collection,
    get_collection_by_name,
    list_collections,
)
from domain.items.schemas import ItemCreate
from domain.items.service import create_item, list_items


def _collection_data(collection) -> dict:
    return {
        "id": collection.id,
        "name": collection.name,
        "description": collection.description,
        "fields": collection.field_definitions,
    }


def _item_data(item) -> dict:
    return {
        "id": item.id,
        "collection_id": item.collection_id,
        "title": item.title,
        "body": item.body,
        "properties": item.properties,
    }


@tool
def list_available_collections() -> list[dict]:
    """List active collections and their field definitions."""
    with SessionLocal() as db:
        return [_collection_data(collection) for collection in list_collections(db)]


@tool
def create_new_collection(
    name: str,
    fields: list[dict[str, Any]],
    description: str = "",
) -> dict:
    """Create a collection. Fields need key, label, type, required, and optional options."""
    with SessionLocal() as db:
        request = CollectionCreate(name=name, description=description, fields=fields)
        return _collection_data(create_collection(db, request))


@tool
def add_item_to_collection(
    collection_name: str,
    title: str,
    properties: dict[str, Any],
    body: str = "",
) -> dict:
    """Add an item to an existing collection using its defined property keys and types."""
    with SessionLocal() as db:
        collection = get_collection_by_name(db, collection_name)
        item = create_item(
            db,
            collection.id,
            ItemCreate(title=title, body=body, properties=properties),
        )
        return _item_data(item)


@tool
def search_saved_items(
    query: str,
    collection_name: str | None = None,
) -> list[dict]:
    """Search item titles, bodies, and properties, optionally inside one collection."""
    with SessionLocal() as db:
        collections = (
            [get_collection_by_name(db, collection_name)]
            if collection_name
            else list_collections(db)
        )
        results = []
        for collection in collections:
            for item in list_items(db, collection.id, search=query, limit=25):
                results.append({"collection": collection.name, **_item_data(item)})
        return results[:50]
