from abc import ABC
from typing import List

from playwright.sync_api import Page

from crawler.crawler_instance.local_interface_model.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _dataleakypypu7uwblm5kttv726l3iripago6p336xjnbstkjwrlnlid(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self):

        self._card_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(_dataleakypypu7uwblm5kttv726l3iripago6p336xjnbstkjwrlnlid, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:

        return "http://dataleakypypu7uwblm5kttv726l3iripago6p336xjnbstkjwrlnlid.onion/"

    @property
    def base_url(self) -> str:

        return "http://dataleakypypu7uwblm5kttv726l3iripago6p336xjnbstkjwrlnlid.onion/"

    @property
    def rule_config(self) -> RuleModel:

        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    @property
    def card_data(self) -> List[card_extraction_model]:

        return self._card_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:

        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:

        return "https://t.me/BlackLockChanel"

    def parse_leak_data(self, page: Page):
        icons = page.query_selector_all(".img")
        for icon in icons[:3]:
            try:
                icon.click()
                page.wait_for_selector(".box")
                content = page.query_selector(".box .white").inner_text()
                print(content)

                title_element = page.query_selector(".box h3")
                title = title_element.inner_text() if title_element else "No Title"
                print(f"Title: {title}")

                data_link_element = page.query_selector(".links a")
                if data_link_element:
                    data_link = data_link_element.get_attribute("href")
                    full_data_link = f"{self.base_url}{data_link}"
                    print(f"Data link: {full_data_link}")
                else:
                    full_data_link = ""

                self._card_data.append(card_extraction_model(
                    m_title=title,
                    m_url=page.url,
                    m_base_url=self.base_url,
                    m_content=content,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_important_content="",
                    m_weblink=[],
                    m_dumplink=[full_data_link],
                    m_email_addresses=[],
                    m_phone_numbers=[],
                    m_content_type="leaks",
                ))

                close_button = page.query_selector(".close")
                if close_button:
                    close_button.click()
                    page.wait_for_selector(".box", state="detached")

            except Exception as e:
                print(f"Failed to click and extract content: {e}")
                continue