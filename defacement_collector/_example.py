from abc import ABC
from typing import List

from playwright.sync_api import Page

from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.defacement_model import defacement_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _example(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self):
        """
        Initialize the _shared_sample class instance.
        Sets up attributes for storing card data, parsing content, and interacting with Redis.
        """
        self._card_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def __new__(cls):
        """
        Create a singleton instance of the _shared_sample class.
        Ensures only one instance of the class is created during runtime.
        """
        if cls._instance is None:
            cls._instance = super(_example, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        """
        Returns the seed URL for the data extraction process.
        This is the starting point for parsing the required content.
        """
        return "https://example.com/"

    @property
    def base_url(self) -> str:
        """
        Returns the base URL for relative URL resolution.
        Used to create absolute URLs during parsing.
        """
        return "https://example.com/"

    @property
    def rule_config(self) -> RuleModel:
        """
        Returns the configuration rules for data fetching.
        Specifies the use of TOR as the proxy and Selenium as the fetching mechanism.
        """
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    @property
    def card_data(self) -> List[leak_model]:
        """
        Returns the list of extracted card data models.
        Stores all parsed information from the leak extraction process.
        """
        return self._card_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:
        """
        Interacts with the Redis database to perform a specified command.

        Args:
            command (REDIS_COMMANDS): The Redis command to execute (e.g., GET, SET).
            key (CUSTOM_SCRIPT_REDIS_KEYS): The key for the operation.
            default_value: The default value to use if the key is not found.

        Returns:
            None
        """
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        """
        Returns the URL of the contact page for the shared sample data source.
        Useful for referencing or navigating to the contact page.
        """
        return "https://www.iana.org/help/example-domains"

    def parse_leak_data(self, page: Page):
        """
        Parses leak data from the given Playwright page object.
        Extracts details such as title, URL, and other attributes, and stores them in the card data model.

        Args:
            page (Page): The Playwright Page object representing the current browser page.

        Returns:
            None
        """
        m_content = "This is a sample defacement content."
        self._card_data = defacement_model(
            m_location=["United States", "California"],
            m_attacker=["HackerX", "AnonUser"],
            m_team="CyberCrew",
            m_web_server=["Apache/2.4.41", "nginx/1.18.0"],
            m_base_url=self.base_url,
            m_network=helper_method.get_network_type(self.base_url),
            m_content=m_content,
            m_ip=["192.168.1.1", "10.0.0.1"],
            m_date_of_leak="2025-03-17",
            m_web_url=["https://example.com/defaced", "https://example.com/hacked"],
            m_screenshot="https://example.com/screenshot.png",
            m_mirror_links=["https://mirror1.example.com", "https://mirror2.example.com"]
        )