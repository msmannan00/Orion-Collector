from pydantic import BaseModel
from typing import List

class entity_model(BaseModel):
    key: str
    value: str
    relationship: str

    def __init__(self, key: str, value: str, relationship: List[str]):
        super().__init__(key=key, value=value, relationship=relationship)
