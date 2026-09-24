from datetime import date, datetime
from typing import Any

from pydantic import AnyUrl, TypeAdapter, ValidationError

from core.exceptions import DomainValidationError
from domain.collections.schemas import FieldDefinition


def _validate_value(field: FieldDefinition, value: Any) -> None:
    if value is None:
        if field.required:
            raise DomainValidationError(f"Property '{field.key}' is required")
        return

    valid = True
    if field.type == "string":
        valid = isinstance(value, str)
    elif field.type == "integer":
        valid = isinstance(value, int) and not isinstance(value, bool)
    elif field.type == "number":
        valid = isinstance(value, (int, float)) and not isinstance(value, bool)
    elif field.type == "boolean":
        valid = isinstance(value, bool)
    elif field.type == "date":
        try:
            date.fromisoformat(value)
        except (TypeError, ValueError):
            valid = False
    elif field.type == "datetime":
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, TypeError, ValueError):
            valid = False
    elif field.type == "url":
        try:
            TypeAdapter(AnyUrl).validate_python(value)
        except ValidationError:
            valid = False
    elif field.type == "select":
        valid = isinstance(value, str) and value in field.options
    elif field.type == "multi_select":
        valid = isinstance(value, list) and all(
            isinstance(option, str) and option in field.options for option in value
        )

    if not valid:
        raise DomainValidationError(
            f"Property '{field.key}' must be of type {field.type}"
        )


def validate_properties(properties: dict[str, Any], definitions: list[dict]) -> None:
    fields = [FieldDefinition.model_validate(definition) for definition in definitions]
    field_map = {field.key: field for field in fields}
    unknown = sorted(set(properties) - set(field_map))
    if unknown:
        raise DomainValidationError(f"Unknown properties: {', '.join(unknown)}")

    for field in fields:
        value = properties.get(field.key)
        if field.required and (field.key not in properties or value in (None, "", [])):
            raise DomainValidationError(f"Property '{field.key}' is required")
        if field.key in properties:
            _validate_value(field, value)
