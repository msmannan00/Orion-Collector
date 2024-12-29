from abc import ABC
from typing import Dict
from playwright.async_api import BrowserContext
from crawler.crawler_instance.local_interface_model.collector_interface import collector_interface
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_instance.local_shared_model.collector_data_model import collector_data_model

'''
 Implementation Guidelines:
 1. Class Naming Convention:
    - The class name must align with the host URL's format. For example, "https://google.com" should translate to a class name "_google".
    - This ensures clarity and consistency across implementations.

 2. File Naming Convention:
    - The file name must match the class name. For example, if the class is named "_google", the file should be named "_google.py".
    - This simplifies file management and enhances code traceability.

 3. Mandatory Method Implementations:
    - `base_url` (property): Returns the base URL as a string.
    - `rule_config` (property): Returns a `RuleModel` instance specifying the fetch proxy and fetch configuration.
    - `parse_leak_data`: An asynchronous method that parses leak data. It takes a query (dictionary) and a BrowserContext as input, and returns an instance of `collector_data_model` populated with relevant data.
'''


class _sample(collector_interface, ABC):
    _instance = None

    def __init__(self):
        pass

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_sample, cls).__new__(cls)
        return cls._instance

    @property
    def base_url(self) -> str:
        """
        Returns the base URL for the class.

        Example:
            >> instance = _sample()
            >> print(instance.base_url)
            "http://sample.onion"
        """
        return "http://sample.onion"

    @property
    def rule_config(self) -> RuleModel:
        """
        Returns the RuleModel configuration for this implementation.

        Example:
            >> instance = _sample()
            >> config = instance.rule_config
            >> print(config.m_fetch_proxy, config.m_fetch_config)
            FetchProxy.TOR FetchConfig.SELENIUM
        """
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    async def parse_leak_data(self, query: Dict[str, str], context: BrowserContext) -> collector_data_model:
        """
        Parses leak data by navigating the page using Playwright's context.

        Args:
            query (Dict[str, str]): Query dictionary containing "url", "email", and "username".
            context (BrowserContext): Playwright's BrowserContext for interacting with web pages.

        Returns:
            collector_data_model: A model containing the parsed data.
        """
        p_data_url = query.get("url", "")
        collector_model = collector_data_model(base_url=p_data_url, content_type=["email", "username"])
        collector_model.cards_data = []

        page = await context.new_page()
        try:
            await page.goto(p_data_url)
        except Exception as e:
            pass
        finally:
            await page.close()

        return collector_model
