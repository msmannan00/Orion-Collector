from abc import ABC
from typing import List
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _example(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self, callback=None):
        """
        Initialize the _example class instance.
        Optionally accepts a callback function (no params) to be called after each leak is added.
        Sets up Redis controller and initializes internal storage for parsed data.
        """
        self.callback = callback
        self._card_data = []
        self._entity_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def init_callback(self, callback=None):
        """
        Initialize or update the callback function.
        The callback is triggered each time a new leak is parsed and added.
        """
        self.callback = callback

    def __new__(cls, callback=None):
        """
        Singleton pattern: ensures only one instance of _example exists.
        Optionally accepts a callback function during instantiation.
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
        """Return the crawling rule configuration for Playwright with TOR proxy."""
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        """Return the list of parsed leak models (card data)."""
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        """Return the list of parsed entity models."""
        return self._entity_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):
        """
        Perform a Redis database operation using the provided command, key, and default value.
        The key is suffixed with the current class name to ensure uniqueness.
        """
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        """Return the contact page URL of the data source."""
        return "https://www.iana.org/help/example-domains"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        """
        Append a leak_model and entity_model instance to internal storage.
        Triggers the callback function if it was initialized.
        """
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        """
        Extract leak-related information from a Playwright Page object.
        Parses the title and URL, derives network type, and extracts emails and phone numbers from the content.
        Constructs and stores corresponding leak_model and entity_model instances.
        """
        m_content = ""

        card_data = leak_model(
            m_title=page.title(),
            m_url=page.url,
            m_base_url=self.base_url,
            m_screenshot="",
            m_content=m_content,
            m_network=helper_method.get_network_type(self.base_url),
            m_important_content=m_content,
            m_weblink=[],
            m_dumplink=[],
            m_content_type=["leaks"],
        )

        entity_data = entity_model(
            m_email_addresses=helper_method.extract_emails(m_content),
            m_phone_numbers=helper_method.extract_phone_numbers(m_content),
        )

        self.append_leak_data(card_data, entity_data)
