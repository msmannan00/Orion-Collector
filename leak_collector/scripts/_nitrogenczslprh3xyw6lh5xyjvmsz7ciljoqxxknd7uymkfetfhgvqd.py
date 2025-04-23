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


class _nitrogenczslprh3xyw6lh5xyjvmsz7ciljoqxxknd7uymkfetfhgvqd(leak_extractor_interface, ABC):
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
            cls._instance = super(_nitrogenczslprh3xyw6lh5xyjvmsz7ciljoqxxknd7uymkfetfhgvqd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        """Return the seed URL to start crawling from."""
        return "http://nitrogenczslprh3xyw6lh5xyjvmsz7ciljoqxxknd7uymkfetfhgvqd.onion"

    @property
    def base_url(self) -> str:
        """Return the base domain URL of the source."""
        return "http://nitrogenczslprh3xyw6lh5xyjvmsz7ciljoqxxknd7uymkfetfhgvqd.onion"

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
        return "http://nitrogenczslprh3xyw6lh5xyjvmsz7ciljoqxxknd7uymkfetfhgvqd.onion"

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
        try:
            page.goto(self.seed_url)

            # Get all hrefs from the specified class
            href_elements = page.query_selector_all('.w3-button.w3-padding-large.w3-white.w3-border')
            href_links = []

            for element in href_elements:
                href = element.get_attribute("href")
                if href:
                    # Check if the href is a relative path
                    if not href.startswith('http'):
                        # Remove leading slash if present to avoid double slashes
                        if href.startswith('/'):
                            href = href[1:]
                        # Combine with base URL
                        full_href = f"{self.base_url}/{href}"
                    else:
                        full_href = href

                    if full_href not in href_links:
                        href_links.append(full_href)

            # Process each href link
            for link in href_links:
                # Navigate to the link
                page.goto(link)

                # Wait for the container to load
                page.wait_for_selector('.w3-container')

                # Find the content container specifically
                container = page.query_selector('.w3-container')
                if not container:
                    continue

                # Find the container
                container = page.query_selector('.w3-container')
                if not container:
                    continue

                # Extract title from h3 tag
                title_element = container.query_selector('h3 b')
                title = title_element.inner_text().strip() if title_element else ""

                # Extract web link from first p tag with an anchor
                web_link_element = container.query_selector('p a')
                m_weblinks = web_link_element.get_attribute("href") if web_link_element else ""

                # Extract all p tags text for description
                p_elements = container.query_selector_all('p')
                m_description = ""
                for p in p_elements:
                    p_text = p.inner_text().strip()
                    if p_text:
                        m_description += p_text + " "
                m_description = m_description.strip()

                # Extract image sources from the column class
                column_element = container.query_selector('.column')
                m_images = []
                if column_element:
                    img_elements = column_element.query_selector_all('img')
                    for img in img_elements:
                        src = img.get_attribute("src")
                        if src:
                            # Convert relative paths to absolute
                            if src.startswith("../"):
                                src = src.replace("../", f"{self.base_url}/")
                            m_images.append(src)

                # Extract button links from w3-col class
                button_container = container.query_selector('.w3-col.m8.s12')
                button_links = []
                if button_container:
                    button_elements = button_container.query_selector_all('a.w3-button')
                    for button in button_elements:
                        button_href = button.get_attribute("href")
                        button_text = button.inner_text().strip()
                        if button_href or button_text:
                            button_links.append({
                                "text": button_text,
                                "href": button_href
                            })

                # Create card data
                card_data = leak_model(
                    m_screenshot="",
                    # helper_method.get_screenshot_base64(page, title),
                    m_title=title,
                    m_url=page.url,
                    m_base_url=self.base_url,
                    m_content=m_description,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_important_content=m_description,
                    m_content_type=["leaks"],
                    m_weblink=[m_weblinks],
                    m_logo_or_images=m_images,
                    m_dumplink=button_links
                )

                entity_data = entity_model()
                self.append_leak_data(card_data, entity_data)

        except Exception as e:
            print(f"Error parsing second website data: {str(e)}")