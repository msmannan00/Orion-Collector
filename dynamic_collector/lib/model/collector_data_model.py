from pydantic import BaseModel, Field, SkipValidation
from dynamic_collector.lib.model.collector_extraction_model import collector_extraction_model
from typing import List

class collector_data_model(BaseModel):
    cards_data: List[SkipValidation[collector_extraction_model]] = Field(default_factory=list)
    base_url: str = ""
    content_type: List[str] = []
