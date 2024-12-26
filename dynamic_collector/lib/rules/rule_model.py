from enum import Enum
from pydantic import BaseModel

class FetchConfig(str, Enum):
    SELENIUM = "selenium"
    REQUESTS = "requests"

class FetchProxy(str, Enum):
    TOR = "tor"
    NONE = "none"

class RuleModel(BaseModel):
    def __init__(self, m_depth: int = 0, m_fetch_config: FetchConfig = FetchConfig.SELENIUM, m_fetch_proxy: FetchProxy = FetchProxy.TOR):
        super().__init__(m_depth=m_depth, m_fetch_config=m_fetch_config, m_fetch_proxy=m_fetch_proxy)
        self.m_depth = m_depth
        self.m_fetch_config = m_fetch_config
        self.m_fetch_proxy = m_fetch_proxy
