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
import time


class _rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad(leak_extractor_interface, ABC):
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
            cls._instance = super(_rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad.onion/"

    @property
    def base_url(self) -> str:
        return "http://rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad.onion/"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT, m_resoource_block=False)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: int, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):

        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "http://rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad.onion/"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        page.wait_for_selector("button#archive_button")
        page.click("button#archive_button")

        page.wait_for_selector("button.btn.btn-secondary[data-company]", timeout=5000)
        more_buttons = page.locator("button.btn.btn-secondary[data-company]").all()

        for button in more_buttons:
            try:
                button.click()
                page.wait_for_timeout(5000)
                # page.wait_for_selector("div.col-8 p.h4", timeout=5000)

                title = page.locator("div.col-8 p.h4").first.text_content() or ""
                print(title)

                p_tags = page.locator("div.col-8 p").all()
                descriptions = [
                    p.text_content() for p in p_tags if p.text_content() and "Documents" not in p.text_content()
                ]
                description = "\n".join(descriptions)
                print(descriptions)

                doc_links = [
                    a.get_attribute("href") for a in page.locator("div.col-8 a").all()
                    if a.get_attribute("href") and ".onion" in a.get_attribute("href")
                ]
                print(doc_links)

                img_urls = [
                    img.get_attribute("src") for img in page.locator("div.row.m-2 div.col img").all()
                    if img.get_attribute("src")
                ]
                print(img_urls)

                extra_description = page.locator("div.m-2").nth(-1).text_content() or ""
                m_content = f"{description} {extra_description}"

                card_data = leak_model(
                    m_title=title,
                    m_url=page.url,
                    m_base_url=self.base_url,
                    m_screenshot="",
                    m_content=m_content,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_important_content=m_content,
                    m_weblink=doc_links,
                    m_dumplink=[],
                    m_content_type=["leaks"],
                )

                entity_data = entity_model(
                    m_email_addresses=helper_method.extract_emails(m_content),
                    m_phone_numbers=helper_method.extract_phone_numbers(m_content),
                )

                self.append_leak_data(card_data, entity_data)

                page.locator(".modal.show button.btn-close[data-bs-dismiss='modal']").click()

            except Exception as e:
                print(f"Error processing card: {e}")