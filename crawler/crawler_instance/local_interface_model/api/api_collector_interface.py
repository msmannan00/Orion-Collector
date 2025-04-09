from abc import ABC, abstractmethod
from typing import Dict, List

from playwright.async_api import BrowserContext

from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel

class api_collector_interface(ABC):
    @property
    @abstractmethod
    def base_url(self) -> str:
        """Return the base URL."""
        pass

    @property
    @abstractmethod
    def rule_config(self) -> RuleModel:
        """Return the rule configuration."""
        pass

    @property
    @abstractmethod
    def card_data(self) -> List[leak_model]:
        """Return the list of parsed leak models (card data)."""
        pass

    @property
    @abstractmethod
    def entity_data(self) -> List[entity_model]:
        """Return the list of parsed leak models (entity data)."""
        pass

    @abstractmethod
    def parse_leak_data(self, query: Dict[str, str], context: BrowserContext):
        pass
