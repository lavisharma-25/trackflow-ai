import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


FieldType = Literal[
    "string",
    "integer",
    "number",
    "boolean",
    "date",
    "datetime",
    "url",
    "select",
    "multi_select",
]


class FieldDefinition(BaseModel):
    key: str = Field(min_length=1, max_length=64)
    label: str = Field(min_length=1, max_length=120)
    type: FieldType = "string"
    required: bool = False
    options: list[str] = Field(default_factory=list)

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        normalized = value.strip().lower().replace(" ", "_")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", normalized):
            raise ValueError("Field keys must start with a letter and contain letters, numbers, or underscores")
        return normalized

    @field_validator("label")
    @classmethod
    def trim_label(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_options(self):
        self.options = list(dict.fromkeys(option.strip() for option in self.options if option.strip()))
        if self.type in {"select", "multi_select"} and not self.options:
            raise ValueError(f"{self.type} fields require at least one option")
        if self.type not in {"select", "multi_select"} and self.options:
            raise ValueError("Only select fields may define options")
        return self


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    fields: list[FieldDefinition] = Field(default_factory=list)

    @field_validator("name", "description")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("fields")
    @classmethod
    def unique_field_keys(cls, value: list[FieldDefinition]) -> list[FieldDefinition]:
        keys = [field.key for field in value]
        if len(keys) != len(set(keys)):
            raise ValueError("Field keys must be unique")
        return value


class CollectionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    fields: list[FieldDefinition] | None = None

    @field_validator("name", "description")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("fields")
    @classmethod
    def unique_field_keys(cls, value: list[FieldDefinition] | None):
        if value is not None:
            keys = [field.key for field in value]
            if len(keys) != len(set(keys)):
                raise ValueError("Field keys must be unique")
        return value


class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    field_definitions: list[dict]
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
