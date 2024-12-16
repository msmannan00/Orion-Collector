from pydantic import BaseModel, Field
from typing import List, Optional


class collector_extraction_model(BaseModel):
    m_title: str = ""
    description: str = ""
    sections: List[str] = Field(default_factory=list)
    name: str = ""
    url: str = ""
    email_addresses: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    addresses: List[str] = Field(default_factory=list)
    social_media_profiles: List[str] = Field(default_factory=list)
    websites: List[str] = Field(default_factory=list)
    company_name: Optional[str] = None
    industry: Optional[str] = None
    job_title_or_position: Optional[str] = None
    associated_entities: List[str] = Field(default_factory=list)
    aliases_or_alternate_names: List[str] = Field(default_factory=list)
    logo_or_images: List[str] = Field(default_factory=list)
    business_categories: List[str] = Field(default_factory=list)
    services_or_products: List[str] = Field(default_factory=list)
    public_records: List[str] = Field(default_factory=list)
    online_activity: List[str] = Field(default_factory=list)
    last_updated: Optional[str] = None
