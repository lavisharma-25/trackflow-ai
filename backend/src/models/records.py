from pydantic import BaseModel
from typing import Any, Dict


class Record(BaseModel):
    data: Dict[str, Any]