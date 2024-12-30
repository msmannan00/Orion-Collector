from abc import ABC
from typing import  Tuple, Set
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from crawler.crawler_instance.local_interface_model.collector_interface import collector_interface
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_instance.local_shared_model.leak_data_model import leak_data_model

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
    - `parse_leak_data`: Parses leak data. It takes `html_content` (string) and `p_data_url` (string) as input, and returns a tuple consisting of:
        - An instance of `leak_data_model` populated with relevant data.
        - A set of sub-links extracted from the content.
    - `contact_page`: Returns the URL of the contact page as a string.
'''

class _shared_sample(collector_interface, ABC):
    _instance = None

    def __init__(self):
        self.soup = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_shared_sample, cls).__new__(cls)
        return cls._instance

    @property
    def base_url(self) -> str:
        return "http://dynamic_sample.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    def parse_leak_data(self, html_content: str, p_data_url: str) -> Tuple[leak_data_model, Set[str]]:
        self.soup = BeautifulSoup(html_content, 'html.parser')
        data_model = leak_data_model(
            cards_data=[],
            contact_link=self.contact_page(),
            base_url=self.base_url,
            content_type=["leak"]
        )
        return data_model, set()

    def contact_page(self) -> str:
        return urljoin(self.base_url, "contact")
