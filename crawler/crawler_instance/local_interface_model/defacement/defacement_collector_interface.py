from abc import ABC, abstractmethod
from playwright.async_api import Page

from crawler.crawler_instance.local_interface_model.defacement.defacement_data_model import defacement_data_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel

class defacement_collector_interface(ABC):
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

    @abstractmethod

    def parse_leak_data(self, page:Page) -> defacement_data_model:
        pass
