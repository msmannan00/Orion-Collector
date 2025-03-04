from abc import ABC
from typing import List

from playwright.sync_api import Page

from crawler.crawler_instance.local_interface_model.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _ks5424y3wpr5zlug5c7i6svvxweinhbdcqcfnptkfcutrncfazzgz5id(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self):

        self._card_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(_ks5424y3wpr5zlug5c7i6svvxweinhbdcqcfnptkfcutrncfazzgz5id, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:

        return "http://ks5424y3wpr5zlug5c7i6svvxweinhbdcqcfnptkfcutrncfazzgz5id.onion/posts.php?pid=kjR1jYcN0m8P5Il0SbJ6hvDm"

    @property
    def base_url(self) -> str:

        return "http://ks5424y3wpr5zlug5c7i6svvxweinhbdcqcfnptkfcutrncfazzgz5id.onion"

    @property
    def rule_config(self) -> RuleModel:

        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    @property
    def card_data(self) -> List[card_extraction_model]:

        return self._card_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:

        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:

        return "http://ks5424y3wpr5zlug5c7i6svvxweinhbdcqcfnptkfcutrncfazzgz5id.onion/index.php#contact"

    def parse_leak_data(self, page: Page):
        links = page.query_selector_all('a[post]')
        link_urls = []
        for link in links:
            href = link.get_attribute('href')
            if href:
                full_url = f"{self.base_url}/posts.php{href}"
                link_urls.append(full_url)

        for url in link_urls[:3]:
            page.goto(url)

            title = page.query_selector('st').inner_text() if page.query_selector('st') else ""
            description = page.query_selector('card in p').inner_text() if page.query_selector('card in p') else ""
            payment_info = page.query_selector('card.rs in cont p').inner_text() if page.query_selector('card.rs in cont p') else ""

            gallery_images = page.query_selector_all('gallery img')
            images = [img.get_attribute('src').strip() for img in gallery_images if
                      img.get_attribute('src') and img.get_attribute('src').endswith('.png')]

            download_urls = []
            for btn in page.query_selector_all('a.btn'):
                onclick = btn.get_attribute('onclick')
                if onclick and "showdir" in onclick:
                    download_url = f"{self.base_url}/download_path_here"  # Replace with the correct logic if available
                    download_urls.append(download_url)

            combined_content = f"{description}{payment_info}"

            self._card_data.append(card_extraction_model(
                m_title=title,
                m_url=url,
                m_base_url=self.base_url,
                m_content=combined_content,
                m_network=helper_method.get_network_type(self.base_url),
                m_important_content=combined_content,
                m_weblink=[],
                m_dumplink=download_urls,
                m_email_addresses=helper_method.extract_emails(combined_content),
                m_phone_numbers=helper_method.extract_phone_numbers(combined_content),
                m_content_type="leaks",
                m_logo_or_images=images,
            ))