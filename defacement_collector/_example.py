from abc import ABC
from typing import List

from playwright.sync_api import Page

from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.defacement_model import defacement_model
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _example(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self, callback=None):
        """
        Initialize the _example class instance.
        Sets up attributes for storing card data, parsing content, and interacting with Redis.
        Optionally accepts a no-argument callback function.
        """
        self.callback = callback
        self._card_data = []
        self._entity_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def init_callback(self, callback=None):
        """
        Initialize or update the callback function that will be triggered upon parsing new leak data.
        """
        self.callback = callback

    def __new__(cls, callback=None):
        """
        Implements singleton behavior to ensure only one instance of the class exists.
        Optionally accepts a no-argument callback function.
        """
        if cls._instance is None:
            cls._instance = super(_example, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        """Return the seed URL to start crawling from."""
        return "https://example.com/"

    @property
    def base_url(self) -> str:
        """Return the base domain URL of the source."""
        return "https://example.com/"

    @property
    def rule_config(self) -> RuleModel:
        """Return the crawling rule configuration."""
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        """Return the list of parsed leak models (card data)."""
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        """Return the list of parsed leak models (entity data)."""
        return self._entity_data

    def invoke_db(self, command: int, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):
        """
        Interact with Redis using the given command and key.
        Returns the result of invoking a Redis trigger with the current class name as context.
        """
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        """Return the contact page URL of the data source."""
        return "https://www.iana.org/help/example-domains"

    def append_leak_data(self, leak: defacement_model, entity: entity_model):
        """
        Appends a defacement_model object to the internal card data list.
        Calls the callback function if it is provided.
        """
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        """
        Parses defacement data from the given Playwright page and appends a defacement_model.
        This is an example implementation that creates hardcoded sample leak and entity data.
        """
        m_content = "This is a sample defacement content."

        card_data = defacement_model(
            m_screenshot="",
            m_url=self.base_url,
            m_web_server=["Apache/2.4.41", "nginx/1.18.0"],
            m_base_url=self.base_url,
            m_network=helper_method.get_network_type(self.base_url),
            m_content=m_content,
            m_web_url=["https://example.com/defaced", "https://example.com/hacked"],
            m_mirror_links=["https://mirror1.example.com", "https://mirror2.example.com"]
        )

        entity_data = entity_model(
            m_ip=["192.168.1.1", "10.0.0.1"],
        )

        self.append_leak_data(card_data, entity_data)
