from abc import ABC
from typing import Dict
from playwright.async_api import BrowserContext
from crawler.crawler_instance.local_interface_model.api.api_collector_interface import api_collector_interface
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_instance.local_interface_model.api.api_data_model import api_data_model
from crawler.crawler_services.shared.helper_method import helper_method

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


class _example(api_collector_interface, ABC):
    _instance = None

    def __init__(self):
        pass

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_example, cls).__new__(cls)
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
        return "https://example.com"

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

    async def parse_leak_data(self, query: Dict[str, str], context: BrowserContext) -> api_data_model:
        p_data_url = self.base_url
        email = query.get("email", "john.doe@gmail.com")
        username = query.get("username", "johndoe123")

        collector_model = api_data_model(base_url=p_data_url, content_type=["email", "username"])
        combined_records = set()

        page = await context.new_page()
        await page.goto(p_data_url)

        combined_records.update(["Adobe Breach 2013", "LinkedIn Leak 2016"])

        collector_model.cards_data = [leak_model(
            m_title="Breach Found",
            m_url=p_data_url,
            m_base_url=p_data_url,
            m_content="Data breach detected.",
            m_important_content="Records exposed.",
            m_network=helper_method.get_network_type(p_data_url),
            m_content_type=["stolen"],
            m_weblink=[],
            m_dumplink=list(combined_records),
            m_email_addresses=[email],
            m_name=username
        )]

        await page.close()
        return collector_model