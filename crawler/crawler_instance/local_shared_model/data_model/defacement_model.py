from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List

@dataclass
class defacement_model:
    m_location: str
    m_attacker: str
    m_team: str
    m_web_server: str
    m_base_url: str
    m_ip: str
    m_date_of_leak: Optional[date]
    m_web_url: str
    m_screenshot: Optional[str] = None
    m_mirror_links: List[str] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.m_date_of_leak, str):
            try:
                self.d_date_of_leak = datetime.strptime(self.m_date_of_leak, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Invalid date format for d_date_of_leak: {self.d_date_of_leak}. Expected format: YYYY-MM-DD.")
