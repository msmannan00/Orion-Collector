from abc import ABC, abstractmethod

from playwright.async_api import Browser, Page, BrowserContext

from crawler.crawler_instance.local_shared_model.collector_data_model import collector_data_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel

class collector_interface(ABC):
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
    def parse_leak_data(self, page: Page, browser: Browser, context: BrowserContext, p_data_url: str) -> collector_data_model:
        """Parse leak data from the loaded page and return a tuple of collector_data_model and a set of sub-links."""
        pass
