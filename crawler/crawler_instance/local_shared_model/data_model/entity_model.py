from pydantic import BaseModel
from typing import List, Optional


class entity_model(BaseModel):
  m_password: Optional[str] = None
  m_email: List[str] = []
  m_phone_numbers: List[str] = []
  m_states: List[str] = []
  m_location: List[str] = []
  m_social_media_profiles: List[str] = []
  m_social_channel: List[str] = []
  m_name: str = ""
  m_industry: Optional[str] = None
  m_company_name: Optional[str] = None
  m_country_name: Optional[str] = None
  m_ip: Optional[List[str]] = None
  m_team: Optional[str] = None
  m_attacker: List[str] = []

  model_config = {
    "extra": "allow"
  }
