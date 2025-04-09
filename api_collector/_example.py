from abc import ABC
from typing import Dict, List
from playwright.async_api import BrowserContext

from crawler.crawler_instance.local_interface_model.api.api_collector_interface import api_collector_interface
from crawler.crawler_instance.local_interface_model.api.api_data_model import api_data_model
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
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
    """
        Initialize the class instance.
        Sets up containers for card data and entity data storage.
        """
    self._card_data = []
    self._entity_data = []

  def __new__(cls):
    """
        Implements singleton pattern to ensure only one instance exists.
        """
    if cls._instance is None:
      cls._instance = super(_example, cls).__new__(cls)
    return cls._instance

  @property
  def base_url(self) -> str:
    """
        Returns the base URL for the class.

        Example:
            >> instance = _example()
            >> print(instance.base_url)
            "https://example.com"
        """
    return "https://example.com"

  @property
  def rule_config(self) -> RuleModel:
    """
        Returns the RuleModel configuration for this implementation.

        Example:
            >> instance = _example()
            >> config = instance.rule_config
            >> print(config.m_fetch_proxy, config.m_fetch_config)
            FetchProxy.TOR FetchConfig.PLAYRIGHT
        """
    return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT)

  @property
  def card_data(self) -> List[leak_model]:
    """
        Returns the list of parsed leak_model objects (breach records).
        """
    return self._card_data

  @property
  def entity_data(self) -> List[entity_model]:
    """
        Returns the list of parsed entity_model objects (associated metadata).
        """
    return self._entity_data

  def append_leak_data(self, leak: leak_model, entity: entity_model):
    """
        Appends a single leak_model and its corresponding entity_model to internal storage.
        """
    self._card_data.append(leak)
    self._entity_data.append(entity)

  async def parse_leak_data(self, query: Dict[str, str], context: BrowserContext):
    """
        Asynchronously parses breach data from the given context using the provided query.

        Args:
            query (Dict[str, str]): Dictionary with keys like 'email' and 'username'.
            context (BrowserContext): The Playwright browser context used for scraping.

        Returns:
            api_data_model: A model populated with the discovered card and entity data.
        """
    p_data_url = self.base_url
    email = query.get("email", "john.doe@gmail.com")
    username = query.get("username", "johndoe123")

    collector_model = api_data_model(base_url=p_data_url, content_type=["email", "username"])

    combined_records = set()

    page = await context.new_page()
    await page.goto(p_data_url)

    combined_records.update(["Adobe Breach 2013", "LinkedIn Leak 2016"])

    card_data = leak_model(
      m_title="Breach Found",
      m_url=p_data_url,
      m_base_url=p_data_url,
      m_screenshot="",
      m_content="Data breach detected.",
      m_important_content="Records exposed.",
      m_network=helper_method.get_network_type(p_data_url),
      m_content_type=["stolen"],
      m_weblink=[],
      m_dumplink=list(combined_records),
    )

    entity_data = entity_model(
      m_email_addresses=[email],
      m_name=username
    )

    self.append_leak_data(card_data, entity_data)
    collector_model.cards_data = self.card_data
    return collector_model
