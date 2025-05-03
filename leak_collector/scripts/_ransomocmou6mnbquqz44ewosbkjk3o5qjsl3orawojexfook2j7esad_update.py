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
from urllib.parse import urlparse
import time

class _ransomocmou6mnbquqz44ewosbkjk3o5qjsl3orawojexfook2j7esad(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self, callback=None):

        self.callback = callback
        self._card_data = []
        self._entity_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def init_callback(self, callback=None):

        self.callback = callback

    def __new__(cls, callback=None):

        if cls._instance is None:
            cls._instance = super(_ransomocmou6mnbquqz44ewosbkjk3o5qjsl3orawojexfook2j7esad, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://ransomocmou6mnbquqz44ewosbkjk3o5qjsl3orawojexfook2j7esad.onion/news"

    @property
    def base_url(self) -> str:
        return "http://ransomocmou6mnbquqz44ewosbkjk3o5qjsl3orawojexfook2j7esad.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: int, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):

        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "http://ransomocmou6mnbquqz44ewosbkjk3o5qjsl3orawojexfook2j7esad.onion/about"


    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()


    def parse_leak_data(self, page: Page):
        page.wait_for_selector('div.category-item.js-open-chat')

        category_items = page.query_selector_all('div.category-item.js-open-chat')
        link_urls = []
        for item in category_items:
            translit = item.get_attribute('data-translit')
            if translit:
                full_url = f"{self.seed_url}/{translit}"
                link_urls.append(full_url)

        for url in link_urls:
            page.goto(url)
            page.wait_for_load_state("networkidle")
            title = page.query_selector('div.flex.js-c-sb h3').inner_text() if page.query_selector(
                'div.flex.js-c-sb h3') else ""
            description = page.query_selector('p.mt-3.publication-description').inner_text() if page.query_selector(
                'p.mt-3.publication-description') else ""
            date = page.query_selector('div.mt-3.date-view').inner_text() if page.query_selector(
                'div.mt-3.date-view') else ""
            views = page.query_selector('div.mt-3.count-view.mr-5').inner_text().strip() if page.query_selector(
                'div.mt-3.count-view.mr-5') else ""

            content = f"{title}: {description} Date: {date} Views: {views}"
            important_content = description

            image_elements = page.query_selector_all('div a.form-image-preview img')
            images = []
            for img in image_elements:
                img_src = img.get_attribute('src')
                if img_src:
                    parsed_url = urlparse(img_src)
                    images.append(parsed_url.path.strip())

            card_data = leak_model(
                m_screenshot="",
                m_title=title,
                m_url=url,
                m_base_url=self.base_url,
                m_content=content,
                m_network=helper_method.get_network_type(self.base_url),
                m_important_content=important_content,
                m_dumplink=[],  # No explicit download link provided in this case
                m_content_type=["leaks"],
                m_logo_or_images=images,
                m_weblink=[],
            )

            entity_data = entity_model(
                m_email_addresses=helper_method.extract_emails(content),
                m_phone_numbers=helper_method.extract_phone_numbers(content),
            )

            self.append_leak_data(card_data, entity_data)
