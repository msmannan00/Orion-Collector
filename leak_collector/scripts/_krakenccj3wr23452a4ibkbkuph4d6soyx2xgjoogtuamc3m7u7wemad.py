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


class _krakenccj3wr23452a4ibkbkuph4d6soyx2xgjoogtuamc3m7u7wemad(leak_extractor_interface, ABC):
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
            cls._instance = super(_krakenccj3wr23452a4ibkbkuph4d6soyx2xgjoogtuamc3m7u7wemad, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:

        return "http://krakenccj3wr23452a4ibkbkuph4d6soyx2xgjoogtuamc3m7u7wemad.onion"

    @property
    def base_url(self) -> str:

        return "http://krakenccj3wr23452a4ibkbkuph4d6soyx2xgjoogtuamc3m7u7wemad.onion"

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

        return "http://krakenccj3wr23452a4ibkbkuph4d6soyx2xgjoogtuamc3m7u7wemad.onion"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        try:

            base_url = self.base_url


            all_hrefs = []


            detail_elements = page.query_selector_all('a[href*="/news/"]')
            for element in detail_elements:
                href = element.get_attribute("href")
                if href and href not in all_hrefs:
                    absolute_href = f"{base_url}{href}" if href.startswith('/') else href
                    all_hrefs.append(absolute_href)


            for href in all_hrefs:
                try:

                    page.goto(href)


                    page.wait_for_selector('.col h4')
                    page.wait_for_selector('div[style*="white-space: pre-wrap"]')


                    title_element = page.query_selector('.col h4')
                    title = title_element.inner_text().strip() if title_element else ""


                    description_element = page.query_selector('div[style*="white-space: pre-wrap"]')
                    description = description_element.inner_text().strip() if description_element else ""


                    print(f"Title: {title}")
                    print(f"Description: {description}")


                    card_data = leak_model(
                        m_title=title,
                        m_url=href,
                        m_base_url=base_url,
                        m_content=description,
                        m_important_content=description[:500],
                        m_content_type=["leaks"],
                        m_network=helper_method.get_network_type(self.base_url),
                        m_screenshot=helper_method.get_screenshot_base64(page,title),

                    )


                    entity_data = entity_model()
                    self.append_leak_data(card_data, entity_data)

                except Exception as e:
                    print(f"Error processing href {href}: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error in parse_leak_data: {str(e)}")