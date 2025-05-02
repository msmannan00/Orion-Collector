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
from bs4 import BeautifulSoup

class _yrz6bayqwhleymbeviter7ejccxm64sv2ppgqgderzgdhutozcbbhpqd(leak_extractor_interface, ABC):
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
            cls._instance = super(_yrz6bayqwhleymbeviter7ejccxm64sv2ppgqgderzgdhutozcbbhpqd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://yrz6bayqwhleymbeviter7ejccxm64sv2ppgqgderzgdhutozcbbhpqd.onion/"

    @property
    def base_url(self) -> str:
        return "http://yrz6bayqwhleymbeviter7ejccxm64sv2ppgqgderzgdhutozcbbhpqd.onion/"

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
        return "http://yrz6bayqwhleymbeviter7ejccxm64sv2ppgqgderzgdhutozcbbhpqd.onion/contacts"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            if self.callback():
                self._card_data.clear()
                self._entity_data.clear()

    def parse_leak_data(self, page: Page):
        page_content = page.content()
        self.soup = BeautifulSoup(page_content, "html.parser")

        card_links = [
            self.base_url + a['href']
            for a in self.soup.find_all("a", string="Learn more")
            if a.has_attr("href")
        ]


        for card_url in card_links:
            page.goto(card_url)
            detail_content = page.content()
            detail_soup = BeautifulSoup(detail_content, "html.parser")

            try:
                weblink = detail_soup.find("div", class_="flex flex-row").find_next("span").text.strip()

                revenue_tag = detail_soup.find_all("div", class_="flex flex-row")[1]
                revenue = revenue_tag.find("span").text.strip()

                country_tag = detail_soup.find_all("div", class_="flex flex-row")[2]
                country = country_tag.find("span").text.strip()

                description_tag = detail_soup.find("div", class_="text-gray-900 whitespace-pre-line")
                description = description_tag.text.strip() if description_tag else ""

                explore_data_link_tag = detail_soup.find("a", string=lambda s: s and "Explore data" in s)
                explore_data_link = (
                    self.base_url + explore_data_link_tag["href"]
                    if explore_data_link_tag and explore_data_link_tag.has_attr("href")
                    else ""
                )
                m_content=description
                card_data = leak_model(
                    m_title=page.title(),
                    m_url=page.url,
                    m_base_url=self.base_url,
                    m_screenshot=helper_method.get_screenshot_base64(page,page.title()),
                    m_content=m_content,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_important_content=m_content,
                    m_weblink=[weblink],
                    m_dumplink=[explore_data_link],
                    m_content_type=["leaks"],
                    m_revenue=revenue

                )
                entity_data = entity_model(
                    m_email_addresses=helper_method.extract_emails(m_content),
                    m_phone_numbers=helper_method.extract_phone_numbers(m_content),
                    m_country_name=country

                )

                self.append_leak_data(card_data, entity_data)

            except Exception as e:
                        print(f"Failed to extract from {card_url}: {e}")
