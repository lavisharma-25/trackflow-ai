import re

from pydantic import BaseModel, Field, field_validator
from typing import List, Literal


ColumnType = Literal["string", "int", "float", "bool", "date"]


class ColumnSchema(BaseModel):
    name: str = Field(..., min_length=1)
    type: ColumnType


class CreateTrackerRequest(BaseModel):
    name: str = Field(..., min_length=1)
    columns: List[ColumnSchema]

    @field_validator("columns")
    @classmethod
    def validate_columns(cls, v):
        if len(v) == 0:
            raise ValueError("At least one column is required")
        names = [column.name.casefold() for column in v]
        if len(names) != len(set(names)):
            raise ValueError("Column names must be unique")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
            raise ValueError("Legacy tracker names may contain only letters, numbers, _ and -")
        return value
