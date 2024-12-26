from typing import List
from pydantic import BaseModel, Field

from shared_collector.lib.model.card_extraction_model import card_extraction_model


class leak_data_model(BaseModel):
    cards_data: List[card_extraction_model] = Field(default_factory=list)
    contact_link: str = ""
    base_url: str = ""
    m_network: str = ""
    content_type: List[str] = []

