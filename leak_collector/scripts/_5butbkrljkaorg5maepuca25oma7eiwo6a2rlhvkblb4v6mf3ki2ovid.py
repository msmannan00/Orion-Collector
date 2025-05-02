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


class _5butbkrljkaorg5maepuca25oma7eiwo6a2rlhvkblb4v6mf3ki2ovid(leak_extractor_interface, ABC):
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
            cls._instance = super(_5butbkrljkaorg5maepuca25oma7eiwo6a2rlhvkblb4v6mf3ki2ovid, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://5butbkrljkaorg5maepuca25oma7eiwo6a2rlhvkblb4v6mf3ki2ovid.onion"

    @property
    def base_url(self) -> str:
        return "http://5butbkrljkaorg5maepuca25oma7eiwo6a2rlhvkblb4v6mf3ki2ovid.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "http://5butbkrljkaorg5maepuca25oma7eiwo6a2rlhvkblb4v6mf3ki2ovid.onion"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            if self.callback():
                self._card_data.clear()
                self._entity_data.clear()

    def parse_leak_data(self, page: Page):
        try:
            cards = page.query_selector_all('.companies-list__item')

            for card in cards:
                title_el = card.query_selector('.name a')
                description_el = card.query_selector('.text')
                weblink_el = description_el.query_selector('a[href^="http"]') if description_el else None
                dumplink_el = card.query_selector('a.btn.btn-primary:not([disabled])')

                title = title_el.text_content().strip() if title_el else "No Title"
                description = description_el.text_content().strip() if description_el else "No Description"
                weblink = weblink_el.get_attribute("href") if weblink_el else ""
                dumplink = dumplink_el.get_attribute("href") if dumplink_el else ""

                card_data = leak_model(
                    m_title=title,
                    m_url=page.url,
                    m_base_url=self.base_url,
                    m_screenshot=helper_method.get_screenshot_base64(page, title),
                    m_content=description,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_important_content=description,
                    m_content_type=["leaks"],
                    m_weblink=[weblink],
                    m_dumplink=[dumplink],
                )

                entity_data = entity_model(
                    m_email_addresses=helper_method.extract_emails(description),
                    m_phone_numbers=helper_method.extract_phone_numbers(description),
                )

                self.append_leak_data(card_data, entity_data)

        except Exception as e:
            print(f"An error occurred while parsing leak data: {e}")